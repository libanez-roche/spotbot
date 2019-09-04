import time
from datetime import datetime, date, timedelta
from config import get_env


class Actions:
	def __init__(self, slackhelper, user_info=None):
		self.user_info = user_info
		self.slackhelper = slackhelper

	def info(self):
	
		return {
			'text': 'Hello! I am spotbot :smile:'}