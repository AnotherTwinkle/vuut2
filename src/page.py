import math
import config 
import textwrap
import logging
import utils
import asyncio

from text import Text, with_prefix

class PageManager:
	def __init__(self, state):
		self.state = state
		self.pages = []
		self.channel_pages_mapping = {}
		self.focus = None

	def set_focus(self, page, teardown = True):
		if (teardown and self.focus):
			self.focus.teardown()

		self.focus = page

	def add_page(self, page):
		self.pages.append(page)
		if isinstance(page, ChannelChatPage):
			self.channel_pages_mapping[page.channel.id] = page

	async def process_message(self, message, show_time = True):
		channel_id = message.channel.id
		if channel_id not in self.channel_pages_mapping.keys():
			return

		await self.channel_pages_mapping[channel_id].process_message(message, show_time)

		
class Page:
	def __init__(self, parent = None, text = ''):
		self.parent = parent
		self.lines = text.split('\n')

	def teardown(self):
		pass

	def close(self):
		self.teardown()

	def handle_back(self):
		if self.parent is None:
			return self.close()

		return self.parent

	def add_line(self, line):
		self.lines.append(line)

	def on_screen_update(self, window_dimensions, output_height):
		pass

	def get_renderable(self):
		pass

class ScrollablePage(Page):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.output_height = 0
		self.window_dimensions = (0, 0)

		self.cur_viewport_lines = self.lines
		self.current_scroll_head = 0

	@property
	def true_output_height(self):
		return self.output_height - 2*int(config.OUTPUT_BORDER_ENABLED)

	def add_line(self, line):
		super().add_line(line)
		self.update_viewport_lines()

	def get_renderable(self):
		count = self.true_output_height

		lines = []
		for i in range(len(self.cur_viewport_lines)):
			if i < self.current_scroll_head:
				continue

			if i > (self.current_scroll_head + self.true_output_height - 1):
				break

			lines.append(self.cur_viewport_lines[i])

		# Only send what output window can display
		# Just to be safe
		lines = lines[-self.true_output_height:]
		return '\n'.join(lines)

	def on_scroll_up(self):
		self.current_scroll_head = max(0, self.current_scroll_head - 1)
		# logging.error(self.current_scroll_head)

	def on_scroll_down(self):
		self.current_scroll_head = min(len(self.cur_viewport_lines) - self.true_output_height, self.current_scroll_head+1)
		# logging.error(self.current_scroll_head)

	def update_viewport_lines(self):
		# logging.error(self.lines)
		lines = []
		for i in range(len(self.lines)):
			cur_lines = textwrap.wrap(self.lines[i], self.window_dimensions[1])
			lines += cur_lines

		self.cur_viewport_lines = lines

	# This does not work
	def on_screen_update(self, window_dimensions, output_height):
		self.output_height = output_height
		if window_dimensions != self.window_dimensions:
			# Do nothing to the text if the window has not been updated
			old_window_dimensions = self.window_dimensions
			char_idx_prev = self.current_scroll_head * old_window_dimensions[1]
			if char_idx_prev:
				char_idx_prev += 1

			self.window_dimensions = window_dimensions
			self.current_scroll_head = math.ceil(char_idx_prev / self.window_dimensions[1])
			if self.current_scroll_head: # Do nothing if 0
				self.current_scroll_head -= 1

			self.update_viewport_lines()

class AutoScrolledPage(ScrollablePage):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.update_scroll_head = True

	def on_scroll_down(self):
		super().on_scroll_down()
		if self.current_scroll_head == len(self.cur_viewport_lines) - self.true_output_height:
			self.update_scroll_head = True # Enable autoscroll

	def on_scroll_up(self):
		super().on_scroll_up()
		self.update_scroll_head = False

	def add_line(self, line):
		super().add_line(line)
		if self.update_scroll_head:
			self.current_scroll_head = len(self.cur_viewport_lines) - self.true_output_height

class ChannelChatPage(AutoScrolledPage):
	def __init__(self, channel, bot, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.channel = channel
		self.bot = bot
		self.opened = False

	def on_first_open(self):
		if self.opened:
			return

		asyncio.create_task(self.send_history(100))
		self.opened = True

	async def process_message(self, message, show_time = False):
		if not self.opened:
			return

		if (message.channel.id != self.channel.id):
			return

		curtime = int(message.created_at.timestamp())
		clockmsg = f'{utils.get_clock_time(curtime)}'

		# handle line breaks. In future, this should all be moved to state
		line_content = message.content
		author_name = f'{message.author.display_name}'
		fmt_tags = []
		if message.author.id != self.bot.user.id:
			fmt_tags.append("**")
			author_name = "**" + author_name + "**"

		# output = with_prefix(line_content, clockmsg, message.author.display_name, 32, True, fmt_tags)
		
		wrapped_lines = textwrap.wrap(line_content, self.window_dimensions[1] - config.PREFIX_LEN - 8) 
		for i in range(len(wrapped_lines)):
			if (i == 0):
				first = True
			else:
				first = False
			wrapped_lines[i] = with_prefix(Text(wrapped_lines[i]), Text(clockmsg), Text(author_name), config.PREFIX_LEN, first, fmt_tags)

		for line in wrapped_lines:
			self.add_line(line)

	async def send_history(self, limit):
		history = list(reversed([message async for message in self.channel.history(limit = limit)]))
		for message in history:
			await self.process_message(message, show_time = True)
