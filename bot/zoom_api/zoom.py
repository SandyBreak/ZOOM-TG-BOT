# -*- coding: UTF-8 -*-

from zoomus import ZoomClient
import logging


from exceptions import CreateMeetingError, GetListMeetingError
from data_storage.dataclasses import ZoomAccount, MeetingData


async def create_and_get_meeting_link(account: ZoomAccount, meeting_data: MeetingData) -> dict:
	"""
	Создание конференции
	"""
	client = ZoomClient(
     	account.client_id,
		account.client_secret,
		account.account_id
  )
	response = client.meeting.create(
		topic=meeting_data.topic,
		type=meeting_data.type,
		start_time=meeting_data.start_time,
		duration=meeting_data.duration,
		password=meeting_data.password,
		settings={
  	    	'password': meeting_data.password_required,
			'auto_recording': meeting_data.auto_recording
    	},
		user_id='me'
	)

	if response:
		try:
			meeting_id = response.json()['id']  # получить идентификатор только что созданной встречи
			meeting_info = client.meeting.get(id=meeting_id)  # получить информацию о встрече с помощью метода get()
			join_url = meeting_info.json()['join_url']  # получить пригласительную ссылку на встречу
			json_data = response.json()
			start_url = json_data.get('start_url')
			if start_url and join_url:
				return 'short_start_url', join_url, meeting_id
		except Exception as e:
			logging.error(f"Error during create meeting: {e}")
			raise CreateMeetingError
	else:
		logging.error(f"Error during create meeting:response is NULL: {e}")
		raise CreateMeetingError


async def get_list_meeting(account: ZoomAccount, date:str)-> dict:
	"""
	Получение списка конференций для введенной даты
	"""
	client = ZoomClient(
    	account.client_id,
		account.client_secret,
		account.account_id
	)
	try:
		response = client.meeting.list(user_id='me', type='upcoming', from_=date, to=date)
		meeting_list = response.json()
		if meeting_list:
			return meeting_list
	except Exception as e:
		logging.error("Error during get_list_meeting: {e}")
		raise GetListMeetingError    
