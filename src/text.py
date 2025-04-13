import re
import curses
import logging

from colors import *

def lr_justified(left, right, n):
	if (left.size + right.size) > n:
		raise ValueError("Too large")

	middle_space = n - left.size - right.size
	return left+ (' ' * middle_space) + right

def with_prefix(line_content, created_at, author_name, len_max, is_first_line, formatting_tags = []):
	# Note, len_max includes the " | "
	prefix = lr_justified(Text(created_at), Text(author_name), len_max - 3)
	if not is_first_line:
		prefix = " "*len(prefix.clean)

	prefix += " | "

	prefmt = ''.join(formatting_tags)
	suffmt = ''.join(formatting_tags[::-1])

	res = prefix + prefmt + line_content + suffmt
	# logging.error(res)
	return res

def get_formatting_patterns():
	formatting_patterns = [
		(r'\*\*(.+?)\*\*', curses.A_BOLD),
		(r'\*(.+?)\*', curses.A_DIM),
		(r'`(.+?)`', curses.A_REVERSE),
		(r'_(.+?)_', curses.A_UNDERLINE),
		(r'<g>(.+?)<g>', curses.color_pair(GREEN)),
		(r'<r>(.+?)<r>', curses.color_pair(RED)),
		(r'<y>(.+?)<y>', curses.color_pair(YELLOW))
	]
	return formatting_patterns

def strip_wrappers(text):
	"""Remove the formatting wrappers from any given text"""
	patterns = get_formatting_patterns()
	for pattern, value in patterns:
		text = re.sub(pattern, r'\1', text)
	return text	

def render_text_line(window, y, x, line, default_attr = curses.A_NORMAL):
	idx = 0
	while line:
		# Find earliest match
		earliest = None
		earliest_match = None
		earliest_attr = None

		for pattern, attr in get_formatting_patterns():
			match = re.search(pattern, line)
			if match:
				if earliest is None or match.start() < earliest:
					earliest = match.start()
					earliest_match = match
					earliest_attr = attr

		if earliest_match:
			pre_text = line[:earliest_match.start()]
			content = earliest_match.group(1)
			line = line[earliest_match.end():]

			if pre_text:
				window.addstr(y, x + idx, pre_text, default_attr)
				idx += len(pre_text)

			window.addstr(y, x + idx, content, default_attr | earliest_attr)
			idx += len(content)
		else:
			window.addstr(y, x + idx, line, default_attr)
			break

class Text(str):
	def __init__(self, raw):
		self._str = raw
		super = raw

	@property
	def raw_size(self):
		return len(self)

	@property
	def size(self):
		return len(self.clean)

	@property
	def clean(self):
		return Text(strip_wrappers(self))

	def __add__(self, other):
		return Text(self._str + other)

	def __mul__(self, other):
		return Text(self._str + other)

	def __rmul__(self, other):
		return Text(self._str + other)

	def capitalize(self, *args, **kwargs):
		return Text(self._str.capitalize(*args, **kwargs))


	def casefold(self, *args, **kwargs):
		return Text(self._str.casefold(*args, **kwargs))

	def center(self, *args, **kwargs):
		return Text(self._str.center(*args, **kwargs))

	def endswith(self, *args, **kwargs):
		return Text(self._str.endswith(*args, **kwargs))

	def expandtabs(self, *args, **kwargs):
		return Text(self._str.expandtabs(*args, **kwargs))

	def format(self, *args, **kwargs):
		return Text(self._str.format(*args, **kwargs))

	def format_map(self, *args, **kwargs):
		return Text(self._str.format_map(*args, **kwargs))

	def join(self, *args, **kwargs):
		return Text(self._str.join(*args, **kwargs))

	def ljust(self, *args, **kwargs):
		return Text(self._str.ljust(*args, **kwargs))

	def lower(self, *args, **kwargs):
		return Text(self._str.lower(*args, **kwargs))

	def lstrip(self, *args, **kwargs):
		return Text(self._str.lstrip(*args, **kwargs))

	def removeprefix(self, *args, **kwargs):
		return Text(self._str.removeprefix(*args, **kwargs))

	def removesuffix(self, *args, **kwargs):
		return Text(self._str.removesuffix(*args, **kwargs))

	def replace(self, *args, **kwargs):
		return Text(self._str.replace(*args, **kwargs))

	def rjust(self, *args, **kwargs):
		return Text(self._str.rjust(*args, **kwargs))

	def rsplit(self, *args, **kwargs):
		return [Text(s) for s in self._str.rsplit(*args, **kwargs)]

	def rstrip(self, *args, **kwargs):
		return Text(self._str.rstrip(*args, **kwargs))

	def split(self, *args, **kwargs):
		return [Text(s) for s in self._str.split(*args, **kwargs)]

	def splitlines(self, *args, **kwargs):
		return [Text(s) for s in self._str.splitlines(*args, **kwargs)]

	def strip(self, *args, **kwargs):
		return Text(self._str.strip(*args, **kwargs))

	def title(self, *args, **kwargs):
		return Text(self._str.title(*args, **kwargs))

	def translate(self, *args, **kwargs):
		return Text(self._str.translate(*args, **kwargs))

	def upper(self, *args, **kwargs):
		return Text(self._str.upper(*args, **kwargs))

	def zfill(self, *args, **kwargs):
		return Text(self._str.zfill(*args, **kwargs))

