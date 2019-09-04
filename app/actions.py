import time
from datetime import datetime, date, timedelta
from config import get_env


class Actions:
	def __init__(self, slackhelper, user_info=None):
		self.user_info = user_info
		self.slackhelper = slackhelper

	def help(self):
		"""
		Return the Available commands in the system and their usage format
		"""
		return {
			'text': 'WELCOME TO THE S2EA HACKATHON: \n '
					'\n Daniel Butnaru and Luis Ibanez ara vailable for any question during the hackathon \n You can find all the information about the hackathon in this document: https://docs.google.com/document/d/1b9prezD65wZXAm22B1CO1SdUptnCEGVp6zRajRU3Z30/edit?usp=sharing \n Good Luck! \n \n Hackabot Ver: 1.0'}
