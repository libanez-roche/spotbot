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


	@app.route('/spotbot', methods=['POST'])
	def hackabot():
		command_text = request.data.get('text')
		command_text = command_text.split(' ')
		slack_uid = request.data.get('user_id')
		slackhelper = SlackHelper()
		slack_user_info = slackhelper.user_info(slack_uid)
		actions = Actions(slackhelper, slack_user_info)

		if command_text[0] not in allowed_commands:
			response_body = {'text': 'Invalid Command Sent - `/hackabot help` for available commands'}

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
		redis_client.set(user_name, text)
		response_body = "Location stored succesfully for user %s on %s" % (user_name, text)
		response = jsonify(response_body)
		response.status_code = 200
		return response

	@app.route('/locate', methods=['POST'])
	def locate():
		text = request.data.get('text')
		text = text.split(' ')
		user = text[0]


		if not user.startswith('@'):
			response_body = {'text': 'User must start with @'}
		else:
			location = redis_client.get(user[1:]) or 'The user hasn\'t set the location yet'
			response_body = "The user %s is located in %s" % (user, location)

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
				print (text)
				if re.search("@(?!\W)", text):
					m = re.findall(r'[@]\w+', text)
					print(m)
					user = m[0]
					print(user)
					location = redis_client.get(user[1:]) or 'The user hasn\'t set the location yet'
					if location == 'The user hasn\'t set the location yet':
						slackhelper.post_message(location)
					else:
						slackhelper.post_message("The user %s is located in %s" % (user, location))
				else:
					slackhelper.post_message('User must start with @')

			else:
				user_name = slack_user_info['user']['profile']['display_name']
				slackhelper.post_message(f"Hi! {user_name} :smile:", channel)
			print(request.data)

		response = jsonify(response_body)
		response.status_code = 200
		return response

	return app
