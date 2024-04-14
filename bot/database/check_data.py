# -*- coding: UTF-8 -*-

from datetime import datetime, timedelta
from typing import Union
import ast
import os

from helper_classes.assistant import MinorOperations
from database.interaction import Interaction
from zoom_api.zoom import get_list_meeting
from exceptions import *



helper = MinorOperations()
db = Interaction(
			user= helper.get_login(),
			password= helper.get_password()
		)


class CheckData:
	def __init__(self, user_id) -> None:
		self.user_id = user_id


	async def check_zoom_for_accuracy(self, choosen_zoom: str) -> Union[str, dict]:
		"""
		Проверка зума на корректность
		"""
		if choosen_zoom not in ['1','2','3']:
			raise DataInputError

		try:
				api_accounts = ast.literal_eval(os.environ.get('API_ACCOUNTS'))
				zoom = api_accounts[int(choosen_zoom)-1]

				if zoom:
					filter_by_id = {'users.tg_id': self.user_id}
					update = {'$set': {'users.$.choosen_zoom': int(choosen_zoom)-1}}
					await  db.update_data(filter_by_id, update)
					return zoom[0]

		except Exception as e:
			raise DataInputError
	
	
	async def checking_the_date_for_accuracy(self, entered_date: str) -> str:
		"""
		Проверка даты на корректность
		"""
		if len(entered_date.split('.')) != 2:
			raise DataInputError
		try:
				date = datetime.strptime(entered_date, '%d.%m')

				if date.month < datetime.now().month:
					date = datetime.strptime(entered_date+'.'+str(datetime.now().year+1), '%d.%m.%Y')
				else:
					date = datetime.strptime(entered_date+'.'+str(datetime.now().year), '%d.%m.%Y')
				
				date = date.strftime('%Y-%m-%d')

				filter_by_id = {'users.tg_id': self.user_id}
				update = {'$set': {'users.$.date': f'{date}',}}
				await db.update_data(filter_by_id, update)

				return date
		
		except Exception as e:
				raise DataInputError

			
	
	async def get_available_time_for_meeting(self,entered_date: str) -> dict:
		"""
		Получение временных интервалов доступных временных интервалов для создания конференции
		"""
		filter_by_id = {'users.tg_id': self.user_id}

		date = datetime.strptime(entered_date, '%Y-%m-%d')

		account = await helper.fill_account_credits(self.user_id)

		meeting_list = await get_list_meeting(account, date.strftime('%Y-%m-%d'))
		planned_meeting_list = []

		for meeting in meeting_list['meetings']:

			start_time = meeting['start_time'].split('T')[0]

			if start_time == date.strftime('%Y-%m-%d'):
				start_time = datetime.strptime(meeting['start_time'], '%Y-%m-%dT%H:%M:%SZ')
				end_time = start_time + timedelta(minutes= meeting['duration'])
				planned_meeting_list.append(((start_time+timedelta(hours=3)), (end_time+timedelta(hours=3))))

		if planned_meeting_list:
			update = {'$set': {'users.$.illegal_intervals': planned_meeting_list}}
			await db.update_data(filter_by_id, update)

			return planned_meeting_list
	



	async def checking_the_start_time_for_accuracy(self, entered_start_time: str) -> None:
		"""
		Проверка времени начала конференции на корректность
		"""
		if len(entered_start_time.split(':')) != 2:
			raise DataInputError
		
		filter_by_id = {'users.tg_id': self.user_id}
		entered_date = await db.get_data(self.user_id, 'date')
		illegal_intervals = await db.get_data(self.user_id, 'illegal_intervals')

		try:
			start_time = datetime.strptime(entered_date + entered_start_time, '%Y-%m-%d%H:%M')

			if start_time.minute %30 != 0:
				raise HalfTimeInputError
			
			response_logs = []
			for start, end in illegal_intervals:

				if ((start_time > start) and (start_time >= end)) or ((start_time < start) and (start_time <= end)):
					response_logs.append('True')
				else:
					response_logs.append('False')
					
			if 'False' in response_logs:
				raise LongTimeInputError
			else:
				update = {'$set': {'users.$.start_time': entered_start_time}}
				await db.update_data(filter_by_id, update)

		except Exception as e:
				raise DataInputError


	async def checking_the_duration_meeting_for_accuracy(self, duration: str) -> None:
		"""
		Проверка продолжительности конференции на корректность
		"""
		
		filter_by_id = {'users.tg_id': self.user_id}
		entered_date = await db.get_data(self.user_id, 'date')
		start_time = await db.get_data(self.user_id, 'start_time')
		illegal_intervals = await db.get_data(self.user_id, 'illegal_intervals')

		if len(start_time.split(':')) != 2:
			raise DataInputError
		
		try:
			date = datetime.strptime(entered_date + start_time, '%Y-%m-%d%H:%M')
			if int(duration[2:]) %15 != 0:
				raise HalfTimeInputError
			
			duration = await helper.duration_conversion(duration)

			if illegal_intervals:
				for start, end in illegal_intervals:
					if ((start < date and end <= date) or (start >= date + timedelta(hours=duration) and end > date + timedelta(hours=duration))):
						update = {'$set': {'users.$.duration_meeting': duration}}
					else:
						raise LongTimeInputError
			else:
				update = {'$set': {'users.$.duration_meeting': duration}}
			await db.update_data(filter_by_id, update)

		except Exception as e:
			raise DataInputError
		


	async def check_record_for_accuracy(self, flag: str) -> None:
		"""
		Проверка ответа на вопрос о записи
		"""
		if not(1 < len(flag) < 4):
			raise DataInputError

		filter_by_id = {'users.tg_id': self.user_id}

		try:
			if flag == 'Да':
				update = {'$set': {'users.$.autorecord_flag': 'cloud'}}
			elif flag == 'Нет':
				update = {'$set': {'users.$.autorecord_flag': 'none'}}
			else:
				raise DataInputError
			await db.update_data(filter_by_id, update)

		except Exception as e:
			raise DataInputError
