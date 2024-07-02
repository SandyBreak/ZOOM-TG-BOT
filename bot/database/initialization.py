# -*- coding: UTF-8 -*-

from bson import ObjectId
from database.interaction import Interaction
from helper_classes.assistant import MinorOperations



helper = MinorOperations()
db = Interaction(
			user= helper.get_login(),
			password= helper.get_password()
		)

class Initialization:
	def __init__(self, user_id: int) -> None:
		self.user_id = user_id

	async def init_user(self) -> str:
		"""
		Инициализация юзера в ячейке хранения данных
		"""
		document = await db.find_data({"_id": ObjectId("65f7110e4e9a3762bba43801")})
		quantity_users = len(document['users'])
		user_log = 0

		for users in range(quantity_users):
			is_user_log_in= document['users'][users]['tg_id']
			if is_user_log_in == self.user_id:# Поиск ячейки хранения данных для пользователя
				user_log = 1
				break

		if not(user_log):
			new_user = {
	        'tg_id': self.user_id,
	        'date': '',
					'choosen_zoom': 0,
	        'start_time': '',
	        'duration_meeting': 0,
					'autorecord_flag': '',
					'illegal_intervals': []
	    }

			update = {'$push': {'users': new_user}}
			await db.update_data(document, update)

			quantity_users = await helper.determining_end_word(quantity_users)
			print(f"Added new user: {self.user_id}\nTotal number of users: {quantity_users[:-3]}")
			
			return quantity_users


	async def delete_user_meeting_data(self) -> None:
		"""
		Обнуление массива с данными о создаваемой конференции в данный момент 
		"""
		filter_by_id = {'users.tg_id': self.user_id}
		delete_data = {'$set': {'users.$.date': '', 'users.$.choosen_zoom': 0, 'users.$.start_time': '', 'users.$.duration_meeting': 0, 'users.$.autorecord_flag': '', 'users.$.illegal_intervals': []}}

		await db.update_data(filter_by_id, delete_data)
	async def update_data_about_created_conferences(self, tg_addr, current_date) -> None:
		document = await db.find_data({"_id": ObjectId("65f7110e4e9a3762bba43801")})
		new_meeting = {
			"creator": tg_addr,
			"date_of_creation": current_date
		}
		update = {'$push': {'created_meetings': new_meeting}}
		await db.update_data(document, update)


	





