import os
import redis
from flask_api import FlaskAPI
from config.env import app_env
from app.utils.slackhelper import SlackHelper
from flask import request, jsonify
from app.actions import Actions
from re import match

allowed_commands = [
		'info'
	]


def create_app(config_name):

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
		redis_client.set(slack_uid, text)
		response_body = "Location stored succesfully for user %s on %s" % (slack_user_info, text)
		response = jsonify(response_body)
		response.status_code = 200
		return response

	return app
