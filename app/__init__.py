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

	@app.route('/sendall', methods=['GET'])
	def sendall():
		slackhelper = SlackHelper()
		request = slackhelper.get_users_in_channel()
		if request['ok']:
			for item in request['members']:
				print(item['id'])
				slackhelper.post_message('Morning, where are you located today?\nPlease write your location in one line (city, building, floor...)\nIf you need to search for a user, use his username with the @.\nThank you! :smile:', item['id'])
		
		response_body = {'text': ':)'}
		response = jsonify(response_body)
		response.status_code = 200
		return response

	@app.route('/send', methods=['GET'])
	def send():
		slackhelper = SlackHelper()
		slackhelper.post_message('Morning, where are you located today?\nPlease write your location in one line (city, building, floor...)\nIf you need to search for a user, use his username with the @.\nThank you! :smile:', 'DN036B2PJ')
		response_body = {'text': ':)'}
		response = jsonify(response_body)
		response.status_code = 200
		return response

	@app.route('/clean', methods=['GET'])
	def clean():
		redis_client.flushdb()
		response_body = {'text': ':)'}
		response = jsonify(response_body)
		response.status_code = 200
		return response

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
		redis_client.set(user_name.encode('utf8'), text)
		response_body = "Your location is stored succesfully as %s" % (text)
		response = jsonify(response_body)
		response.status_code = 200
		return response

	@app.route('/locate', methods=['POST'])
	def locate():
		text = request.data.get('text')
		text = text.split(' ')
		user = text[0]
		print(user)

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
				user_name = slack_user_info['user']['name']
				clean_user_name = slack_user_info['user']['profile']['real_name_normalized']
				words_to_check = [' close to ',' near ',' next to ',' beside ',' in front of ',' behind ',' on ',' in ',' at ',' on ',' top of ',' within ',' beneath ',' under ','building','bau','basel','kau','kaiseraugst','floor','home','wfh']
				
				print (text)
				if re.search("@(?!\W)", text):
					m = re.findall(r'[@]\w+', text)
					print(m)
					user = m[0]
					print('username: ' + user_name)
					print('user: ' + user)
					search_user_info = slackhelper.user_info(user[1:])
					print(search_user_info)
					search_clean_user_name = search_user_info['user']['profile']['real_name_normalized']
					location = redis_client.get(user[1:]) or 'The user hasn\'t set the location yet'
					if location == 'The user hasn\'t set the location yet':
						slackhelper.post_message(location, channel)
					else:
						slackhelper.post_message("%s:  %s" % (search_clean_user_name, location.decode('utf8')), channel)
				elif any(word.lower() in text.lower() for word in words_to_check):
					slackhelper = SlackHelper()
					print(user_name)
					redis_client.set(user_id, text)
					slackhelper.post_message('Thank you! :smile: I have recorded your location.\nHave a good day!', channel)
				elif 'list' in text:
					if len(redis_client.keys()) > 0:
						list = ''
						print(redis_client.keys())
						for user in redis_client.keys():
							print(user)
							print(slackhelper.user_info(user))
							name =  slackhelper.user_info(user)['user']['profile']['real_name_normalized']
							list = list + name + ': '+ redis_client.get(user).decode('utf8') + '\n'
						slackhelper.post_message(list, user_id)
					else:
						slackhelper.post_message('Sorry, there are no users registered', user_id)

				else:
					slackhelper.post_message('Sorry :disappointed:, I didn\'t understand your request.\n - If you want to add your location, please say in one line where are you located (city, building, floor...)\nIf you need to search for a user use his username with the @.\nThank you! :smile:', channel)

			else:
				print("nothing")
		response = jsonify(response_body)
		response.status_code = 200
		return response

	return app
