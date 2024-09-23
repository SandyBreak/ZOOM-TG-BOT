# -*- coding: UTF-8 -*-

from datetime import datetime, timedelta
import logging


from utils.assistant import MinorOperations
from services.postgres.create_meeting_service import CreateMeetingService
from services.zoom_api.zoom import get_list_meeting
from exceptions.errors import DataInputError, LongTimeInputError, LongTimeInputError, HalfTimeInputError


helper = MinorOperations()


class CheckData:
	def __init__(self, user_id) -> None:
		self.user_id = user_id


	async def checking_the_date_for_accuracy(self, entered_date: str) -> None:
		"""
		Проверка даты на корректность
		"""
		try:
			date = datetime.strptime(entered_date, '%d.%m')
   
			if date.month < datetime.now().month:
				date = datetime.strptime(entered_date + '.' + str(datetime.now().year+1), '%d.%m.%Y')
			else:
				date = datetime.strptime(entered_date + '.' + str(datetime.now().year), '%d.%m.%Y')
				
			await CreateMeetingService.save_data(self.user_id, 'date', date.strftime('%Y-%m-%d'))
			
			await self.get_available_time_for_meeting(date.strftime('%Y-%m-%d'))
		except Exception as e:
			logging.error(f"Error during checking_the_date_for_accuracy: {e}")

			
	async def get_available_time_for_meeting(self, entered_date: str) -> None:
		"""Получение временных интервалов недоступных временных интервалов для создания конференции и сохранение их в базу данных

		Args:
			entered_date (str): Дата выбранная пользователем для создания конференции
		"""
		date = datetime.strptime(entered_date, '%Y-%m-%d')

		illegal_intervals = {
      		'zoom1':[],
			'zoom2':[],
			'zoom3':[],
		}
		zoom_keys = ['zoom1', 'zoom2', 'zoom3']
  
		for i in range(0, 3): # Перебираем все аккаунты
			account = await helper.fill_account_credits(i)
			print(account.name)
			meeting_list = await get_list_meeting(account, date.strftime('%Y-%m-%d'))

			for meeting in meeting_list['meetings']:

				start_time_date = meeting['start_time'].split('T')[0]
				if start_time_date == date.strftime('%Y-%m-%d'):
					start_time = datetime.strptime(meeting['start_time'][:-4], "%Y-%m-%dT%H:%M")
					end_time = start_time + timedelta(minutes= meeting['duration'])
					illegal_intervals[zoom_keys[i]].append(((start_time + timedelta(hours=3)).strftime('%Y-%m-%dT%H:%M'), (end_time + timedelta(hours=3)).strftime('%Y-%m-%dT%H:%M')))
			
			logging.info(illegal_intervals[zoom_keys[i]])
		
		
		print('==============')
		print(illegal_intervals)
		print('==============')

		if illegal_intervals:
			await CreateMeetingService.save_data(self.user_id, "illegal_intervals", illegal_intervals)
	
 
	async def checking_the_start_time_for_accuracy(self, entered_start_time: str) -> None:
		"""
  			Проверка времени начала конференции на корректность

		Args:
			entered_start_time (str): Время начала конференции выбраное пользователем

		Raises:
			LongTimeInputError: Ошибка пересечения конференций
			DataInputError: Любая другая ошибка
		"""
		entered_date = await CreateMeetingService.get_data(self.user_id, 'date')
		illegal_intervals = await CreateMeetingService.get_data(self.user_id, 'illegal_intervals')
		
		try:
			start_time = datetime.strptime(entered_date + entered_start_time, '%Y-%m-%d%H:%M')

			is_time_valid = True  # Флаг для проверки корректности времени
			response_logs = []
   
			for account_intervals in illegal_intervals.values():
				print(account_intervals)
				for start, end in account_intervals:
					start = datetime.strptime(start, "%Y-%m-%dT%H:%M")
					end = datetime.strptime(end, "%Y-%m-%dT%H:%M")

        	        # Проверка, попадает ли start_time в интервал
					if (start_time >= start and start_time < end):
						is_time_valid = False
						break
				response_logs.append(is_time_valid)
				is_time_valid = True
    
			print('response_logs:', response_logs)
			if not True in response_logs:
				raise LongTimeInputError
			else:
				await CreateMeetingService.save_data(self.user_id, 'start_time', entered_start_time)
    
		except LongTimeInputError:
			raise LongTimeInputError
		except Exception as e:
			logging.error(f"Error during checking_the_start_time_for_accuracy: {e}")
			raise DataInputError


	async def checking_the_duration_meeting_for_accuracy(self, duration: str) -> None:
		"""
		Проверка продолжительности конференции на корректность
		"""
		entered_date = await CreateMeetingService.get_data(self.user_id, 'date')
		start_time = await CreateMeetingService.get_data(self.user_id, 'start_time')
		illegal_intervals = await CreateMeetingService.get_data(self.user_id, 'illegal_intervals')
		
		
		try:
			start_conference = datetime.strptime(entered_date + start_time, '%Y-%m-%d%H:%M')
			
			duration_hours = await helper.duration_conversion(duration)
			valid_account_found = False
			counter_account = 0
			if illegal_intervals:
				for account_intervals in illegal_intervals.values():
					if await MinorOperations.is_duration_valid(account_intervals, start_conference, duration_hours):
						valid_account_found = True
						break
					counter_account += 1
				if not valid_account_found:
					raise LongTimeInputError
			else:
            	# Если нет недоступных интервалов, просто сохраняем данные
				valid_account_found = True
			update = [duration_hours, counter_account]
			await CreateMeetingService.save_data(self.user_id, 'duration_and_zoom_account', update)
		except LongTimeInputError:
			raise LongTimeInputError
		except Exception as e:
			logging.error(f"Error during checking_the_duration_meeting_for_accuracy: {e}")
			raise DataInputError

	async def check_record_for_accuracy(self, flag: str) -> None:    
		"""
		Проверка ответа на вопрос о записи
		"""

		try:
			await CreateMeetingService.save_data(self.user_id, 'autorecord_flag', flag)
		except Exception as e:
			logging.error("Error during check_record_for_accuracy: {e}")
			raise DataInputError
