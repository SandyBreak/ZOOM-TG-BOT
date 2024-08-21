# -*- coding: UTF-8 -*-
from aiogram.types import Message, ReplyKeyboardRemove

from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram import Router


from database.mongodb.interaction import Interaction


mongodb_interface = Interaction()
router = Router()


@router.message(Command(commands=['start', 'cancel']))
async def bot_menu_and_start_message(message: Message, state: FSMContext) -> None:
    await state.clear()

    await mongodb_interface.init_user(message.from_user.id, message.from_user.username, message.from_user.full_name)
    
    await mongodb_interface.delete_user_meeting_data(message.from_user.id)
    
    menu_message = """
С помощью этого бота вы можете создать нужную вам конференцию в Zoom.
Для этого необходимо:

1. Выбрать дату проведения конференции
2. Выбрать время начала
3. Указать длительность конференции
4. Выбрать тип записи в облако
5. Дать имя конференции
      
Если вы используете бота впервые, то возможно вам будет необходимо ознакомиться c разделом помощи, доступной по команде /help
      
Для комфортного использования ознакомьтесь с командами бота, которые перечислены в боковом меню
		"""
    await message.answer(menu_message, reply_markup=ReplyKeyboardRemove())

    
@router.message(Command(commands=['help']))
async def bot_help(message: Message, state: FSMContext) -> None:
    help_message = """
Бот позволяет вводить все необходимые данные с предлагаемой клавиатуры, однако если вы хотите вводить данные вручную придерживайтесь следующих указаний:

1. Дата конференции вводится в формате ДД.ММ. Разрешено создавать конференции до конца текущего года.

2. Время начала должно либо равняться точному часу либо половине этого часа, например 10:00 или 9:30 соответственно.

3. Минимальная продолжительность конференции 15 минут. Максимальная - 9 часов.

4. Продолжительность конференции должна быть кратной 15 минутам. Например: 0:30, 1:00, 1:15, 2:45 и т.д.

7. Название конференции может быть любое

Если бот внезапно перестал работать, пожайлуста сообщите об этом по этому адресу: @velikiy_ss"
"""

    await  message.answer(help_message, reply_markup=ReplyKeyboardRemove())
    await state.clear()