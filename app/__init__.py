import os
import redis
import json
from flask_api import FlaskAPI
from config.env import app_env
from app.utils.slackhelper import SlackHelper
from flask import request, jsonify
from app.actions import Actions
from re import match
import re


allowed_commands = [
		'info'
	]


def create_app(config_name):

	bot_id = 'UMTM6Q95F'
	app = FlaskAPI(__name__, instance_relative_config=False)
	app.config.from_object(app_env[config_name])
	app.config.from_pyfile('../config/env.py')
	redis_client = redis.from_url(os.environ.get("REDIS_URL"))

	@app.route('/send', methods=['GET'])
	def send():
		slackhelper = SlackHelper()
		request = slackhelper.get_users_in_channel()
		if request['ok']:
			for item in request['members']:
				print item['name']

	@app.route('/spotbot', methods=['POST'])
	def hackabot():
		command_text = request.data.get('text')
		command_text = command_text.split(' ')
		slack_uid = request.data.get('user_id')
		slackhelper = SlackHelper()
		slack_user_info = slackhelper.user_info(slack_uid)
		actions = Actions(slackhelper, slack_user_info)

		if command_text[0] not in allowed_commands:
			response_body = {'text': 'Invalid Command Sent - `/spotbot info` for available commands'}

		if command_text[0] == 'info':
			response_body = actions.info()

		response = jsonify(response_body)
		response.status_code = 200
		return response

	@app.route('/change', methods=['POST'])
	def change():
		text = request.data.get('text')
		slack_uid = request.data.get('user_id')
		slackhelper = SlackHelper()
		slack_user_info = slackhelper.user_info(slack_uid)
		user_name = slack_user_info['user']['name']
		redis_client.set(user_name, text.encode('utf8'))
		response_body = "Your location is stored succesfully as %s" % (text)
		response = jsonify(response_body)
		response.status_code = 200
		return response

	@app.route('/locate', methods=['POST'])
	def locate():
		text = request.data.get('text')
		text = text.split(' ')
		user = text[0]


		if not user.startswith('@'):
			response_body = {'text': 'The username must start with @'}
		else:
			location = redis_client.get(user[1:]).decode('utf8') or '%s hasn\'t set his location yet' % (user)
			response_body = "%s: %s" % (user, location)

		response = jsonify(response_body)
		response.status_code = 200
		return response

	@app.route('/reaction', methods=['POST'])
	def reaction():
		type = request.data.get('type')
		event = request.data.get('event')
		user_id = event['user']
		channel = event['channel']
		text = event['text']

		if type == 'url_verification':
			response_body = request.data.get('challenge')
		else:
			response_body = 'Hi!'
			if not user_id == bot_id:
				slackhelper = SlackHelper()
				slack_user_info = slackhelper.user_info(user_id)
				words_to_check = [' close to ',' near ',' next to ',' beside ',' in front of ',' behind ',' on ',' in ',' at ',' on ',' top of ',' within ',' beneath ',' under ','building','bau','basel','kau','kaiseraugst','floor']
				
				print (text)
				if re.search("@(?!\W)", text):
					m = re.findall(r'[@]\w+', text)
					print(m)
					user = m[0]
					print(user)
					location = redis_client.get(user[1:]).decode('utf8') or 'The user hasn\'t set the location yet'
					if location == 'The user hasn\'t set the location yet':
						slackhelper.post_message(location, channel)
					else:
						slackhelper.post_message("The user %s is located in %s" % (user, location), channel)
				elif any(word in text for word in words_to_check):
					slackhelper = SlackHelper()
					slack_user_info = slackhelper.user_info(user_id)
					user_name = slack_user_info['user']['name']
					redis_client.set(user_name, text.encode('utf8'))
					slackhelper.post_message('Thank you! :smile: I have recorded your location.\nHave a good day!', channel)
				elif 'list' in text:
					if redis_client.keys() > 0:

				else:
					slackhelper.post_message('Sorry :sad:, I didn\'t understand your request. If you need to search for a user use his username with the @.\nThank you! :smile:', channel)

			else:
				user_name = slack_user_info['user']['profile']['display_name']
		response = jsonify(response_body)
		response.status_code = 200
		return response

	return app
