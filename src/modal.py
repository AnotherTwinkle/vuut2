from text import strip_wrappers as stripw
import time

class ModalLine:
	"""Intelligent modal line rendering"""
	def __init__(self, elems = None, priority = [2, 0, 1]):
		self.priority = priority
		if elems is None:
			elems = []
		self.elements = elems
		while len(self.elements) < 3:
			self.elements.append('')

	@property
	def left(self):
		return self.elements[0]

	@left.setter
	def left(self, w):
		self.elements[0] = w

	@property
	def center(self):
		return self.elements[1]

	@center.setter
	def center(self, w):
		self.elements[1] = w

	@property
	def right(self):
		return self.elements[2]

	@right.setter
	def right(self, w):
		self.elements[2] = w

	def get_renderable(self, max_length):
		elements = [str(element) for element in self.elements]
		n = max_length

		# Keep removing until we are happy. Removal priority is 1 > 0 > 2
		while (sum([len(stripw(l)) for l in elements]) >= max_length):
			match len(elements):
				case 1:
					elements = []
				case 2:
					elements.pop()
				case 3:
					elements.pop(1)

		if not elements:
			return ' ' * n

		if len(elements) == 1:
			stripped = stripw(elements[0])
			mid = (n - len(stripped)) // 2
			left = ' ' * mid
			right = ' ' * (n - mid - len(stripped))
			return left + elements[0] + right

		if len(elements) == 2:
			left_elem, right_elem = elements
			middle_space = n - len(stripw(left_elem)) - len(stripw(right_elem))
			return left_elem + (' ' * middle_space) + right_elem

		if len(elements) == 3:
			e1, e2, e3 = elements
			total_len = sum([len(stripw(l)) for l in elements])
			total_spaces = n - total_len
			gap1 = total_spaces // 2
			gap2 = total_spaces - gap1
			return e1 + ' ' * gap1 + e2 + ' ' * gap2 + e3

class Modal:
	def __init__(self, max_lines, lines = []):
		self.max_lines = max_lines
		self.lines = lines
		while (len(lines) < max_lines):
			lines.append(ModalLine())

		self._remove_on = []
		for i in range(max_lines):
			self._remove_on.append([None, None, None])

	def on_screen_update(self):
		curtime = time.time()
		for i in range(self.max_lines):
			for j in range(3):
				if self._remove_on[i][j] and curtime >= self._remove_on[i][j]:
					self.set(i, j, '')
					self._remove_on[i][j] = None

	def set(self, line, idx, text, timeout = None):
		self.lines[line].elements[idx] = text

		curtime = time.time()
		self._remove_on[line][idx] = curtime + timeout if timeout else None

	def set_line(self, line, modal_line : ModalLine, timeout = None):
		self.lines[line] = modal_line

		end_time = time.time() + timeout if timeout else None
		self._remove_on[line] = [end_time, end_time, end_time]
	
	def get(self, line, idx):
		return self.lines[line].elements[idx]

	def get_line(self, line):
		return self.lines[line]
	

