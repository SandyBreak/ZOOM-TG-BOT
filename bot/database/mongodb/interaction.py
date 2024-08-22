# -*- coding: UTF-8 -*-

from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from typing import Union
import logging
import os


class Interaction:
	def __init__(self) -> None:
		"""
		Строка подключения для локального запуска
		"""
		#mongo_client = AsyncIOMotorClient(f'mongodb://localhost:27017')
		
		"""
		Строка подключения для запуска на сервере
		"""
		login = os.environ.get('MONGO_INITDB_ROOT_USERNAME')
		password = os.environ.get('MONGO_INITDB_ROOT_PASSWORD')
		mongo_client = AsyncIOMotorClient(f'mongodb://{login}:{password}@mongodb:27017')
		
		self.__db = mongo_client['zoom_tg_bot']
		self.__current_data = self.__db['current_data_f_new_meeting'] # Коллекция с данными


	async def find_data(self, filter: dict) -> dict:
     
		return await self.__current_data.find_one(filter)


	async def update_data(self, filter: int, update: int) -> None:
		
		await self.__current_data.update_one(filter, update)


	async def get_data(self, user_id: int, type_data: str) -> Union[int, str, float, dict]:
		filter_by_id = {'tg_id': user_id}
		result = await self.__current_data.find_one({'users': {'$elemMatch': filter_by_id}},{'users.$': 1})

		return result['users'][0][f'{type_data}']


	async def init_user(self, user_id: int, user_addr: str, user_name: str) -> str:
		"""
		Инициализация юзера в ячейке хранения данных
		"""
		document = await self.find_data({"_id": ObjectId("65f7110e4e9a3762bba43801")})
		quantity_users = len(document['users'])
		user_log = 0

		for users in range(quantity_users):
			is_user_log_in= document['users'][users]['tg_id']
			if is_user_log_in == user_id:# Поиск ячейки хранения данных для пользователя
				user_log = 1
				break

		if not(user_log):
			new_user = {
	        'tg_id': user_id,
			'tg_addr': f'@{user_addr}',
			'full_name': user_name,
	        'date': '',
			'choosen_zoom': 0,
	        'start_time': '',
	        'duration_meeting': 0,
			'autorecord_flag': '',
			'illegal_intervals': []
	    	}

			update = {'$push': {'users': new_user}}
			await self.update_data(document, update)

			logging.warning(f"Added new user: {user_id} Total number of users: {quantity_users[:-3]}")


	async def delete_user_meeting_data(self, user_id: int) -> None:
		"""
		Обнуление массива с данными о создаваемой конференции в данный момент 
		"""
		filter_by_id = {'users.tg_id': user_id}
		delete_data = {'$set': {'users.$.date': '', 'users.$.choosen_zoom': 0, 'users.$.start_time': '', 'users.$.duration_meeting': 0, 'users.$.autorecord_flag': '', 'users.$.illegal_intervals': []}}

		await self.update_data(filter_by_id, delete_data)
  
  
	async def update_data_about_created_conferences(self, tg_addr: str, current_date: str) -> None:
		document = await self.find_data({"_id": ObjectId("65f7110e4e9a3762bba43801")})
		new_meeting = {
			"creator": f'@{tg_addr}',
			"date_of_creation": current_date
		}
		update = {'$push': {'created_meetings': new_meeting}}
		await self.update_data(document, update)
  

	async def get_users_id_and_tg_adreses(self) -> dict:
		'''
		Получение массива id пользователей для отправки рассылки
  		'''
		document = await self.find_data({'_id': ObjectId('65f7110e4e9a3762bba43801')})
		quantity_users = len(document['users'])
		users_data = []
		for users in range(quantity_users):
			user_id = document['users'][users]['tg_id']
			tg_addr = document['users'][users]['tg_addr']
			users_data.append([str(user_id),tg_addr])
		
		return users_data
