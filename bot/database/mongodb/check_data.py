# -*- coding: UTF-8 -*-

from datetime import datetime, timedelta
import logging

from helper_classes.assistant import MinorOperations
from database.mongodb.interaction import Interaction
from zoom_api.zoom import get_list_meeting
from exceptions import *



helper = MinorOperations()
db = Interaction()


class CheckData:
	def __init__(self, user_id) -> None:
		self.user_id = user_id

	
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
				illegal_intervals = await self.get_available_time_for_meeting(date)
				return illegal_intervals
		
		except Exception as e:
				raise DataInputError

			
	
	async def get_available_time_for_meeting(self, entered_date: str) -> dict:
		"""
		Получение временных интервалов доступных временных интервалов для создания конференции
		"""
		filter_by_id = {'users.tg_id': self.user_id}
		date = datetime.strptime(entered_date, '%Y-%m-%d')
  
		illegal_intervals = [[],[],[]]
		
		for i in range(0, 3):
			account = await helper.fill_account_credits(i)
			meeting_list = await get_list_meeting(account, date.strftime('%Y-%m-%d'))

			for meeting in meeting_list['meetings']:
				start_time = meeting['start_time'].split('T')[0]

				if start_time == date.strftime('%Y-%m-%d'):
					start_time = datetime.strptime(meeting['start_time'], '%Y-%m-%dT%H:%M:%SZ')   
					end_time = start_time + timedelta(minutes= meeting['duration'])

					illegal_intervals[i].append((start_time+timedelta(hours=3), end_time+timedelta(hours=3)))

		if illegal_intervals:
			update = {'$set': {'users.$.illegal_intervals': illegal_intervals}}
			await db.update_data(filter_by_id, update)
    
			return illegal_intervals
	
 
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
			
			#response_logs 
			primary_logs = []
			secondary_logs = []
			for account_intervals in illegal_intervals:
				for start, end in account_intervals:

					if ((start_time > start) and (start_time >= end)) or ((start_time < start) and (start_time <= end)):
						secondary_logs.append('True')
					else:
						secondary_logs.append('False')
				print(secondary_logs)
				if 'False' in secondary_logs:
					primary_logs.append('False')
					secondary_logs = []
				else:
					primary_logs.append('True')
					secondary_logs = []

			print(primary_logs)
			
			if not('True' in primary_logs):
				raise LongTimeInputError
			else:
				update = {'$set': {'users.$.start_time': entered_start_time}}
				await db.update_data(filter_by_id, update)
    
		except LongTimeInputError:
			raise LongTimeInputError
		except HalfTimeInputError:
			raise HalfTimeInputError
		except Exception as e:
			logging.error(f"Error during checking_the_start_time_for_accuracy: {e}")
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
			counter_account = 0

			primary_logs = []
			secondary_logs = []
   
			if illegal_intervals:
				for account_intervals in illegal_intervals:
					for start, end in account_intervals:
						if ((start < date and end <= date) or (start >= date + timedelta(hours=duration) and end > date + timedelta(hours=duration))):
							secondary_logs.append('True')
						else:
							secondary_logs.append('False')
					print(secondary_logs)
					if 'False' in secondary_logs:
						primary_logs.append('False')
						secondary_logs = []
					else:
						primary_logs.append('True')
						secondary_logs = []
						update = {'$set': {'users.$.duration_meeting': duration, 'users.$.choosen_zoom': counter_account}}
						break
					counter_account+=1
	
				print(primary_logs)
				print(counter_account)
				
				if not('True' in primary_logs):
					raise LongTimeInputError
				else:
					update = {'$set': {'users.$.duration_meeting': duration, 'users.$.choosen_zoom': counter_account}}

			else:
				update = {'$set': {'users.$.duration_meeting': duration, 'users.$.choosen_zoom': counter_account}}
			

			await db.update_data(filter_by_id, update)
		except LongTimeInputError:
			raise LongTimeInputError
		except HalfTimeInputError:
			raise HalfTimeInputError
		except Exception as e:
			logging.error(f"Error during checking_the_duration_meeting_for_accuracy: {e}")
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
