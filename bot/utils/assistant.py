# -*- coding: UTF-8 -*-

from datetime import datetime, timedelta
from typing import Union
import random

from config import API_ACCOUNTS

from models.dataclasses import ZoomAccount, MeetingData

from services.postgres.create_meeting_service import CreateMeetingService

class MinorOperations:
	def __init__(self):
		pass
    
    
	@staticmethod
	async def fill_account_credits(account_index: int) -> ZoomAccount:
		"""
        Заполнение структуры с данными о ZOOM аккаунте 
        """
		api_accounts = API_ACCOUNTS
		mas_account = api_accounts[account_index]
		
		account = ZoomAccount(
	        name=mas_account[0],
			account_id=mas_account[1],
	        client_id=mas_account[2],
	        client_secret=mas_account[3]
		)
		return account


	@staticmethod
	async def fill_meeting_data_credits(user_id: int, name: str) -> Union[MeetingData, int, str]:
		"""
		Заполнение структуры с данными о создаваемой конференции
        """
		conference_data = await CreateMeetingService.get_data(user_id, 'all')
  
		access_code = random.randint(100000, 999999)

		meeting_data = MeetingData(
	  		topic=name,
	  		type=2,
	  		start_time=datetime.strptime(conference_data.date + conference_data.start_time, '%Y-%m-%d%H:%M')- timedelta(hours=3),
	  		duration=int(conference_data.duration_meeting * 60),
	  		password=access_code,
	  		timezone='Europe/Moscow',
        	password_required=True,
        	auto_recording=conference_data.autorecord_flag
	    )
		return meeting_data, access_code, conference_data.choosen_zoom
	
	@staticmethod
	async def duration_conversion(duration: int) -> float:
		"""_summary_

		Args:
			duration (int): _description_

		Returns:
			float: _description_
		"""
		dec_duration = float('0.' + duration[2:])
		duration = float(duration.replace(":", "."))

		if dec_duration == 0.15:
			duration = duration//1 + 0.25

		elif dec_duration == 0.3:
			duration = duration//1 + 0.5

		elif dec_duration == 0.45:
			duration = duration//1 + 0.75
		
		return duration

	@staticmethod
	async def create_worktime_slots(entered_date: str) -> list:
		time_slots = []
		start_time = datetime.strptime(entered_date + "09:00", '%Y-%m-%d%H:%M')  # Начало рабочего дня
		end_time = datetime.strptime(entered_date + "21:00", '%Y-%m-%d%H:%M')  # Конец рабочего дня

		current_slot_start = start_time # Текущий временной интервал
        
        # Генерация временных слотов по 30 минут
		while current_slot_start < end_time:
			current_slot_end = current_slot_start + timedelta(minutes=30)
			if current_slot_start > datetime.now():
				time_slots.append(current_slot_start)  # Добавляем слот
			current_slot_start = current_slot_end  # Переходим к следующему слоту

		return time_slots


	@staticmethod
	async def is_slot_valid(slot: datetime, account_intervals: list) -> bool:
		for start, end in account_intervals:  # Здесь мы перебираем интервалы
			start = datetime.strptime(start, "%Y-%m-%dT%H:%M")
			end = datetime.strptime(end, "%Y-%m-%dT%H:%M")
	
			if (start <= slot < end) or (slot < datetime.now()):
				return False
		return True


	@staticmethod
	async def is_duration_valid(account_intervals, start_conference, duration_hours):
		"""
		Проверка, доступна ли продолжительность для данного аккаунта
		"""
		for start, end in account_intervals:
			start = datetime.fromisoformat(start)
			end = datetime.fromisoformat(end)
			if not ((start < start_conference and end <= start_conference) or (start >= start_conference + timedelta(hours=duration_hours) and end > start_conference + timedelta(hours=duration_hours))):
				return False
		return True

	async def is_conflict(start, end, time_slots):
		for slot in time_slots:
			existing_start = datetime.fromisoformat(slot[0])
			existing_end = datetime.fromisoformat(slot[1])
    	    # Проверка на пересечение
			if start < existing_end and end > existing_start:
				return True
		return False


	@staticmethod
	async def max_duration_for_account(time_slots: list, conference_start: datetime):
    	# Проверка длительностей от 30 минут до 9 часов
		min_duration = timedelta(minutes=30)
		max_duration = timedelta(hours=9)
		step = timedelta(minutes=30)

		available_durations = []
		# Генерация всех возможных длительностей
		duration = min_duration
		while duration <= max_duration:
			conference_end = conference_start + duration
			if not await MinorOperations.is_conflict(conference_start, conference_end, time_slots):
				available_durations.append(duration)
			duration += step
		return_max_duration_value = 0
    	# Вывод доступных длительностей
		for duration in available_durations:
			return_max_duration_value = duration
		print('Max duration for Account:', return_max_duration_value)
		if return_max_duration_value:
			return conference_start + return_max_duration_value
		else:
			return conference_start
	
	@staticmethod
	async def is_conflict(start, end, time_slots) -> bool:
		for slot in time_slots:
			existing_start = datetime.fromisoformat(slot[0])
			existing_end = datetime.fromisoformat(slot[1])
    	    # Проверка на пересечение
			if start < existing_end and end > existing_start:
				return True
		return False