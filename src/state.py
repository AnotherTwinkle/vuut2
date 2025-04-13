import traceback
import textwrap
import asyncio 
import logging
import shlex
import time

import cmdlib
import utils
import text
import page
import config

from modal import ModalLine, Modal

logging.basicConfig(filename='debug.log', level=logging.ERROR)

class State:
	def __init__(self, modules =  []):
		self.input = ''
		self.process_commands = False

		self.on_first_screen_update_called = False
		self.modal = Modal(3)
		self.modal.set(0, 1 , "<g>Vuut2.0<g> <r>Alpha<r> <y>Tests<y>")

		self.window_dimensions = (1,1)
		self.output_height = 0
	
		self.pageman = page.PageManager(self)

		self.parser = cmdlib.Parser()
		for module in modules:
			self.parser.load_module(module)

	def load_module(self, module):
		self.parser.load_module(module)

	def process_command(self, itext):
		args = shlex.split(itext)
		command, args, flags = self.parser.parse(args[0], args[1:])
		ctx = cmdlib.Context(command= command, state= self, page= self.pageman.focus)

		command.invoke(ctx, *args, **flags)

	def handle_input(self, itext):
		if self.process_commands:
			if itext.startswith(":"):
				itext = itext[1:]
				self.process_command(itext)
			else:
				pass

		else:
			if itext.strip() and isinstance(self.pageman.focus, page.ChannelChatPage) and not config.DISABLE_MESSAGE_SEND:
				asyncio.create_task(self.pageman.focus.channel.send(itext.strip()))
			
		self.input = ''

	def output(self):
		if self.pageman.focus:
			return self.pageman.focus.get_renderable()
		return ''

	def on_first_screen_update(self, window_dimensions, output_height):
		if not config.START_BOT:
			import random
			import string
			for i in range(100):
				# logging.error("hi")
				size = random.randint(100, 500)
				#logging.error(size)
				self.current_channel_page.add_line(str(i) + '.'+ ''.join([random.choice(string.ascii_lowercase) for j in range(size)]))


	def on_screen_update(self, window_dimensions, output_height):
		self.window_dimensions = window_dimensions
		self.output_height = output_height
		self.modal.set(0, 2, utils.get_clock_time(int(time.time())))
		self.modal.on_screen_update()
		if self.pageman.focus:
			self.pageman.focus.on_screen_update(window_dimensions, output_height)

		if not self.on_first_screen_update_called:
			self.on_first_screen_update(window_dimensions, output_height)
			self.on_first_screen_update_called = True
