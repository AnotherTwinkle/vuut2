import cmdlib
import logging
import page

class Core(cmdlib.Module):
	def __init__(self, parser, state, bot):
		self.parser = parser
		self.state = state
		self.bot = bot 

	@cmdlib.command(name = "ping")
	def ping(self, ctx):
		logging.error("Pong!")

	@cmdlib.add_flag(name = "lower", default = False)
	@cmdlib.add_flag(name = "upper", default = False)
	@cmdlib.command(name = "echo")
	def echo(self, ctx, message):
		if ctx.flags.lower and ctx.flags.upper:
			raise ValueError()

		if ctx.flags.upper:
			logging.error(message.upper())

		elif ctx.flags.lower:
			logging.error(message.lower())

		else:
			logging.error(message)

	@cmdlib.command(name = 'select', aliases = ['s'])
	def select(self, ctx, idx : int):
		if not isinstance(ctx.page, page.OptionsPage):
			return

		ctx.state.pageman.set_focus(ctx.page.on_select(idx), parent = ctx.page)

	@cmdlib.command(name = 'back', aliases = ['b'])
	def back(self, ctx):
		ctx.state.pageman.go_back()

