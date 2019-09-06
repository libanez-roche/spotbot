import time
from datetime import datetime, date, timedelta
from config import get_env


class Actions:
	def __init__(self, slackhelper, user_info=None):
		self.user_info = user_info
		self.slackhelper = slackhelper

	def info(self):
	
		return {
			'text': 'Hello! I am spotbot :smile:\nIf you want to add your location, please write in one line where are you located (city, building, floor...)\nIf you need to search for a user, use his username with the @.\nThank you! :smile:'}
