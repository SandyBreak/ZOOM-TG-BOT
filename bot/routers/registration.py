# -*- coding: UTF-8 -*-

from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import StateFilter, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from aiogram import Router, F, Bot

from admin.admin_logs import send_log_message

from services.postgres.user_service import UserService
from services.postgres.group_service import GroupService

from models.long_messages import MENU_MESSAGE
from models.emojis_chats import Emojis
from models.states import RegUserStates

from exceptions.errors import UserNotRegError, RegistrationError

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Начало регистрации
    """
    if (await state.get_data()).get('message_id'):
        await bot.delete_message(chat_id=message.chat.id, message_id=(await state.get_data()).get('message_id'))
    await state.clear()
    try:
        user_date_reg =  await UserService.check_user_exists(message.from_user.id)
        await message.answer((f"Вы уже зарегистрированы!\nДата регистрации: {user_date_reg.strftime('%d.%m.%Y %H:%M')}"))
    except UserNotRegError:
            delete_message = await message.answer("Введите ваше ФИО:", reply_markup=ReplyKeyboardRemove())
            
            await state.update_data(message_id=delete_message.message_id)
            await state.set_state(RegUserStates.get_fio)


@router.message(F.text, StateFilter(RegUserStates.get_fio))
async def get_city(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Получение ФИО
    """
    SUPER_GROUP_ID = await GroupService.get_group_id()
    try:
        await UserService.init_user(message.from_user.id, message.from_user.username, message.from_user.full_name, message.text)
        await bot.delete_message(chat_id=message.chat.id, message_id=(await state.get_data()).get('message_id'))
        
        new_topic = await bot.create_forum_topic(chat_id=SUPER_GROUP_ID, name=message.from_user.full_name)
        await GroupService.save_user_message_thread_id(message.from_user.id, new_topic.message_thread_id)
        
        fio = await UserService.get_user_fio(message.from_user.id)
        new_user_message = await bot.send_message(chat_id=SUPER_GROUP_ID, text=f'ID пользователя: {message.from_user.id}\nТелеграмм имя пользователя: {message.from_user.full_name}\nФИО: {fio}\nАдрес пользователя: @{message.from_user.username}\nID темы: {new_topic.message_thread_id}', reply_to_message_id=new_topic.message_thread_id)
        await bot.pin_chat_message(chat_id=SUPER_GROUP_ID, message_id=new_user_message.message_id)
        
        await message.answer("Поздравляю! Вы успешно прошли регистрацию!")
        await message.answer(MENU_MESSAGE, ParseMode.HTML)
    except RegistrationError:
        message_log = await message.answer(f"{Emojis.FAIL} Ошибка регистрации! {Emojis.FAIL}")
    await state.clear()
    if message_log: await send_log_message(message, bot, message_log)