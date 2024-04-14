# -*- coding: UTF-8 -*-

from datetime import datetime, timedelta
import random
import ast
import os

from data_storage.data_storage_classes import ZoomAccount, MeetingData
from database.interaction import Interaction

db = Interaction(
			user= os.environ.get('MONGO_INITDB_ROOT_USERNAME'),
			password= os.environ.get('MONGO_INITDB_ROOT_PASSWORD')
		)

class MinorOperations:
	def __init__(self):
		pass
	

	async def determining_end_word(self, quantity_users: int) -> str:
		quantity_users += 1

		if str(quantity_users)[-1] in  ['1', '4', '5', '9', '0']:
			quantity_users = str(quantity_users) + '-ый'

		elif str(quantity_users)[-1] in ['2', '6', '7', '8']:
			quantity_users = str(quantity_users) + '-ой'
		
		elif str(quantity_users)[-1] in '3':
			quantity_users = str(quantity_users) + '-ий'
		
		return quantity_users
	
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

	def get_login(self):
		return os.environ.get('MONGO_INITDB_ROOT_USERNAME')


	def get_password(self):
		return os.environ.get('MONGO_INITDB_ROOT_PASSWORD')


	async def get_token(self):
		return os.environ.get('TELEGRAM_TOKEN')
	
	async def fill_account_credits(self, user_id: int) -> ZoomAccount:

		
		api_accounts = ast.literal_eval(os.environ.get("API_ACCOUNTS"))
		index_mas_account = await db.get_data(user_id, 'choosen_zoom')
		mas_account = api_accounts[index_mas_account]

		account = ZoomAccount(
	        name=mas_account[0],
					account_id=mas_account[1],
	        client_id=mas_account[2],
	        client_secret=mas_account[3]
		)
		return account
	
	async def fill_meeting_data_credits(self, user_id: int, name: str) -> MeetingData:
		entered_date = await db.get_data(user_id, 'date')
		start_time = await  db.get_data(user_id, 'start_time')
		duration = await  db.get_data(user_id, 'duration_meeting')
		auto_recording = await  db.get_data(user_id, 'autorecord_flag')
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
		return meeting_data, access_code
	
	