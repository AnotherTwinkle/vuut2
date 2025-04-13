import curses
import asyncio
import discord 
import signal 
import logging

import text
from state import State
from client import Vuut

import config 

from token import *
from config import *
from colors import *

import modules

async def run_curses_ui(stdscr, state):
	global WINDOW_MAX_X, WINDOW_MAX_Y, OUTPUT_HEIGHT

	curses.curs_set(1)
	stdscr.nodelay(True)
	stdscr.timeout(100)
   
	curses.start_color()
	curses.use_default_colors()

	curses.init_pair(GREEN, curses.COLOR_GREEN, -1)
	curses.init_pair(RED, curses.COLOR_RED, -1)
	curses.init_pair(YELLOW, curses.COLOR_YELLOW, -1)

	buffer = ''
	while True:
		try:
			ch = stdscr.get_wch()
			if ch == -1:
				continue

			ESCAPE = "\x1b"
			if ch == '\n':
				state.handle_input(buffer)
				buffer = ''
			elif ch in ('\b', '\x7f', curses.KEY_BACKSPACE):
				buffer = buffer[:-1]
			elif ch == ESCAPE:
				buffer = ''
				if not state.process_commands:
					state.modal.set(0, 0, "COMMAND MODE")
				else:
					state.modal.set(0, 0, '')
				state.process_commands = not state.process_commands

			elif isinstance(ch, str) and ch.isprintable():
				buffer += ch
			elif ch == curses.KEY_UP:
				state.pageman.focus.on_scroll_up()
			elif ch == curses.KEY_DOWN:
				state.pageman.focus.on_scroll_down()

		except curses.error:
			pass

		WINDOW_MAX_Y, WINDOW_MAX_X = stdscr.getmaxyx()
		OUTPUT_HEIGHT = WINDOW_MAX_Y - INPUT_HEIGHT - MODAL_HEIGHT

		# Gotta do some monkey business here
		config.WINDOW_MAX_X = WINDOW_MAX_X
		config.WINDOW_MAX_Y = WINDOW_MAX_Y
		config.OUTPUT_HEIGHT = OUTPUT_HEIGHT

		# Modal window
		modal_win = curses.newwin(MODAL_HEIGHT, WINDOW_MAX_X, 0,0)
		modal_win.erase()

		modal_lines = state.modal.lines
		if len(modal_lines) > MODAL_HEIGHT - 2*int(MODAL_BORDER_ENABLED):
			modal_lines = [f"Cannot render modal : Too many lines ({len(modal_lines)})"]

		for idx, line in enumerate(modal_lines):
			text.render_text_line(modal_win, idx + int(MODAL_BORDER_ENABLED), 1, line.get_renderable(WINDOW_MAX_X - 2),)

		modal_win.border()
		modal_win.refresh()

		# Output window
		output_win = curses.newwin(OUTPUT_HEIGHT, WINDOW_MAX_X, MODAL_HEIGHT, 0)
		output_win.erase()

		output = state.output()
		output_lines = output.splitlines()
		for idx, line in enumerate(output_lines[-(OUTPUT_HEIGHT- int(OUTPUT_BORDER_ENABLED)):]):
			text.render_text_line(output_win, idx + int(OUTPUT_BORDER_ENABLED), 1, line)

		output_win.border()
		output_win.refresh()

		# Input window
		input_win = curses.newwin(INPUT_HEIGHT, WINDOW_MAX_X, WINDOW_MAX_Y - INPUT_HEIGHT, 0)
		input_win.scrollok(True)
		input_win.erase()

		input_win.border()
		input_win.addstr(1, 1, buffer[-(WINDOW_MAX_X - 2):])
		input_win.refresh()

		state.on_screen_update(stdscr.getmaxyx(), OUTPUT_HEIGHT)

		await asyncio.sleep(0.01)

async def noop():
	42

async def main():
	state = State()
	intents = discord.Intents.all()
	bot = Vuut(state, intents=intents)

	state.load_module(modules.Core(state.parser, state, bot))
	loop = asyncio.get_event_loop()

	# Set up curses UI in raw mode
	stdscr = curses.initscr()
	curses.noecho()
	curses.cbreak()
	stdscr.keypad(True)

	# Handle cleanup gracefully
	def shutdown():
		curses.nocbreak()
		stdscr.keypad(False)
		curses.echo()
		curses.endwin()
		loop.stop()

	for sig in (signal.SIGINT, signal.SIGTERM):
		loop.add_signal_handler(sig, shutdown)

	try:
		await asyncio.gather(
			bot.start(DISCORD_TOKEN) if config.START_BOT else noop(),
			run_curses_ui(stdscr, state)
		)
	finally:
		shutdown()


if __name__ == '__main__':
	asyncio.run(main())
