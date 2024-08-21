# -*- coding: UTF-8 -*-

from datetime import datetime, timedelta
import random
import ast
import os

from data_storage.dataclasses import ZoomAccount, MeetingData
from database.mongodb.interaction import Interaction

mongodb_interface = Interaction()

class MinorOperations:
	def __init__(self):
		pass


	def get_mongo_login(self):
		return os.environ.get('MONGO_INITDB_ROOT_USERNAME')


	def get_mongo_password(self):
		return os.environ.get('MONGO_INITDB_ROOT_PASSWORD')


	async def get_tg_token(self):
		return os.environ.get('TELEGRAM_TOKEN')

	
	async def fill_account_credits(self, account_index: int) -> ZoomAccount:
		api_accounts = ast.literal_eval(os.environ.get("API_ACCOUNTS"))
		mas_account = api_accounts[account_index]
		
		account = ZoomAccount(
	        name=mas_account[0],
			account_id=mas_account[1],
	        client_id=mas_account[2],
	        client_secret=mas_account[3]
		)
		return account


	async def fill_meeting_data_credits(self, user_id: int, name: str) -> MeetingData:
		entered_date = await mongodb_interface.get_data(user_id, 'date')
		start_time = await  mongodb_interface.get_data(user_id, 'start_time')
		duration = await  mongodb_interface.get_data(user_id, 'duration_meeting')
		auto_recording = await  mongodb_interface.get_data(user_id, 'autorecord_flag')
		choosen_zoom = await  mongodb_interface.get_data(user_id, 'choosen_zoom')
		access_code = random.randint(100000, 999999)
		meeting_data = MeetingData(
	  		topic=name,
	  		type=2,
	  		start_time=datetime.strptime(entered_date + start_time, '%Y-%m-%d%H:%M')- timedelta(hours=3),
	  		duration=int(duration * 60),
	  		password=access_code,
	  		timezone='Europe/Moscow',
        	password_required=True,
        	auto_recording=auto_recording
	    )
		return meeting_data, access_code, choosen_zoom
	
	
	async def duration_conversion(self, duration: int) -> float:
		dec_duration = float('0.' + duration[2:])
		duration = float(duration.replace(":", "."))

		if dec_duration == 0.15:
			duration = duration//1 + 0.25

		elif dec_duration == 0.3:
			duration = duration//1 + 0.5

		elif dec_duration == 0.45:
			duration = duration//1 + 0.75
		
		return duration