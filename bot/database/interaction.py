# -*- coding: UTF-8 -*-

import motor.motor_asyncio
from typing import Union

class Interaction:
	def __init__(self, user:str, password: str) -> None:
		mongo_client = motor.motor_asyncio.AsyncIOMotorClient(f'mongodb://{user}:{password}@mongodb:27017')
		self.__db = mongo_client['zoom_tg_bot']
		self.__current_data = self.__db['current_data_f_new_meeting'] # Коллекция с данны
	
	async def find_data(self, filter: dict) -> dict:

		return await self.__current_data.find_one(filter)


	async def update_data(self, filter: int, update: int) -> None:
		
		await self.__current_data.update_one(filter, update)


	async def get_data(self, user_id: int, type_data: str) -> Union[int, str, float, dict]:#!~~~!!!!!
		filter_by_id = {'tg_id': user_id}
		result = await self.__current_data.find_one({'users': {'$elemMatch': filter_by_id}},{'users.$': 1})

		return result['users'][0][f'{type_data}']
