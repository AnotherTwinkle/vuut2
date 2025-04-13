import time
from text import Text
from datetime import datetime

def get_clock_time(timestamp):
	return Text(datetime.fromtimestamp(timestamp).strftime("%H:%M:%S"))

def get_date(timestamp):
	return Text(datetime.fromtimestamp(timestamp).strftime("%d/%m/%y"))

def lr_justified(left : Text, right : Text, n):
	if (left.size + right.size) > n:
		raise ValueError("Too large")

	middle_space = n - left.size - right.size
	return Text(left+ (' ' * middle_space) + right)
