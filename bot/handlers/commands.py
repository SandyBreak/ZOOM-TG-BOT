# -*- coding: UTF-8 -*-

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

from handlers.create_new_meeting import start_create_new_meeting
from handlers.get_planned_meetings import get_planned_meetings

from database.initialization import Initialization


async def register_handlers_commands(dp: Dispatcher) -> None:
    dp.register_message_handler(bot_menu_and_start_message, commands="start", state="*")
    dp.register_message_handler(bot_help, commands="help", state="*")
    dp.register_message_handler(start_create_new_meeting, commands="create", state="*")
    dp.register_message_handler(start_create_new_meeting, commands="reset", state="*")
    dp.register_message_handler(bot_menu_and_start_message, commands="cancel", state="*")
    dp.register_message_handler(get_planned_meetings, commands="meetings", state="*")


async def bot_menu_and_start_message(message: types.Message, state: FSMContext) -> None:
    await state.finish()

    user = Initialization(message.from_user.id)

    response = await user.init_user()
    
    if response:
        await  message.answer(f"Вы {response} по счету человек, который начал пользоваться ботом!")
    await user.delete_user_meeting_data()
    
    menu_message = """
С помощью этого бота вы можете создать нужную вам конференцию на одном из трех корпоративных аккаунтов Zoom NBC.
Для этого необходимо:

1. Выбрать один из трех аккаунтов ZOOM
2. Выбрать дату проведения конференции
3. Выбрать время начала
4. Указать длительность конференции
5. Выбрать тип записи в облако
6. Дать имя конференции
      
Если вы используете бота впервые, то возможно вам будет необходимо ознакомиться c разделом помощи, доступной по команде /help
      
Для комфортного использования ознакомьтесь с командами бота, которые перечислены в боковом меню
		"""
    await message.answer(
        menu_message, 
        reply_markup=types.ReplyKeyboardRemove()
    )
    

async def bot_help(message: types.Message, state: FSMContext) -> None:
    help_message = """
Бот позволяет вводить все необходимые данные с предлагаемой клавиатуры, однако если вы хотите вводить данные вручную придерживайтесь следующих указаний:

1. Дата конференции вводится в формате ДД.ММ. Разрешено создавать конференции до конца текущего года.

2. Если для введенной вами даты нужное вам время занято другими конференциями, введите команду /reset или /create, чтобы выбрать другой ZOOM аккаунт.

3. Время начала должно либо равняться точному часу либо половине этого часа, например 10:00 или 9:30 соответственно.

4. Минимальная продолжительность конференции 15 минут. Максимальная - 9 часов.

5. Продолжительность конференции должна быть кратной 15 минутам. Например: 0:30, 1:00, 1:15, 2:45 и т.д.

6. Для получения записи конференции обратитесь к соответствующему сотруднику, предоставив ему почту zoom аккаунта, на котором была создана конференция

7. Название конференции может быть любое

Если бот внезапно перестал работать, пожайлуста сообщите об этом по этому адресу: @raptor_f_22"

		"""

    await state.finish()
    await  message.answer(
        help_message,
        reply_markup=types.ReplyKeyboardRemove()
    )