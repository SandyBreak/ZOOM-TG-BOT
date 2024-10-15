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


class EpmtyTableError(Exception):
    """
    Ошибка пустой таблицы при выгрузке данных
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


class UserNotRegError(Exception):
    """
    Ошибка из-за того, что пользователь не зарегистиррован в боте
    """
    pass


class RegistrationError(Exception):
    
    pass
    
    
class TelegramAddressNotValidError(Exception):
    """
    Пустой адрес телеграмм аккаунта пользователя
    """
    pass

