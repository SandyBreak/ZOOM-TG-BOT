# -*- coding: UTF-8 -*-

class DataInputError(Exception):
	"""
	Ввод данных неправильного формата
	"""
	pass


class LongTimeInputError(Exception):
	"""
	Ввод времени которое пересекается с другими конференциями
	"""
	pass


class HalfTimeInputError(Exception):
	"""
	Неправильное количество минут у длительности и начала
	"""
	pass


class CreateMeetingError(Exception):
	"""
	Ошибка создания конференции
	"""
	pass


class GetListMeetingError(Exception):
	"""
	Ошибка получения списка конференций
	"""
	pass

