import discord
import utils
import time
import textwrap
import logging
import config 
import curses
import os
import page

from text import Text, with_prefix

TARGET_CHANNEL_ID = 1110903386540347404

class Vuut(discord.Client):
	def __init__(self, state, **kwargs):
		super().__init__(status = discord.Status.offline, **kwargs)
		self.state = state

	async def on_ready(self):
		for guild in self.guilds:
			for channel in guild.channels:
				self.state.pageman.add_page(page.ChannelChatPage(channel, self))

		self.state.pageman.set_focus(self.state.pageman.channel_pages_mapping[TARGET_CHANNEL_ID])

		if isinstance(self.state.pageman.focus, page.ChannelChatPage) and self.state.pageman.focus.opened == False:
			self.state.pageman.focus.on_first_open()

	async def on_message(self, message):
		channel_id = message.channel.id
		await self.state.pageman.process_message(message, show_time = True)

	async def on_presence_update(self, before, after):
		if not isinstance(self.state.pageman.focus, page.ChannelChatPage):
			return

		if before.guild != self.state.pageman.focus.channel.guild:
			return

		if not before.status == discord.Status.offline and \
			(after.status == discord.Status.idle \
			or (before.status == discord.Status.idle and after.status == discord.Status.online)):
			return

		# Cases
		# offline -> idle
		# offline -> online
		# online -> offline
		# idle -> offline
		clockmsg = utils.get_clock_time(int(time.time()))
		datemsg = utils.get_date(int(time.time()))

		msg = f"{after.display_name}: {before.status} -> {after.status}"
		msg = with_prefix(msg, clockmsg, "\u2192", config.PREFIX_LEN, True)

		match after.status:
			case discord.Status.online:
				clr = '<g>'
			case discord.Status.idle:
				clr = '<y>'
			case _:
				clr = ''

		self.state.pageman.focus.add_line(Text(f'{clr}{msg}{clr}'))
			
		if os.name == 'posix': # Use linux notification api
			try:
				os.system(f'notify-send "Status Update" "{after.display_name}: {before.status} -> {after.status}" -u critical')
			except Exception as e:
				logging.error(e)
				pass
