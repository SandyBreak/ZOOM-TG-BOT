# -*- coding: UTF-8 -*-

from datetime import timedelta
import logging
import json

from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, StateFilter
from aiogram import Router, F, Bot, suppress
from aiogram.fsm.context import FSMContext

from admin.admin_logs import send_log_message

from services.postgres.create_meeting_service import CreateMeetingService
from services.postgres.user_service import UserService

from services.zoom_api.zoom import create_and_get_meeting_link

from models.user_keyboards import  UserKeyboards
from models.states import CreateMeetingStates
from models.emojis_chats import Emojis

from utils.meeting_data_validator import CheckData
from utils.assistant import MinorOperations

from exceptions.errors import DataInputError, LongTimeInputError, CreateMeetingError, UserNotRegError


router = Router()


@router.message(Command(commands=['create', 'reset']))
async def start_create_new_meeting(message: Message, state: FSMContext, bot: Bot) -> None:
    """
        Инициализация пользователя

    Args:
        message (Message): This object represents a message.
        state (FSMContext): Base class for all FSM storages
        bot (Bot): Bot class
    """
    with suppress(TelegramBadRequest):
        if (delete_message_id := (await state.get_data()).get('message_id')): await bot.delete_message(chat_id=message.chat.id, message_id=delete_message_id)
    await state.clear()
    try:
        
        await UserService.check_user_exists(message.from_user.id)
        await CreateMeetingService.delete_temporary_data(message.from_user.id)
        await CreateMeetingService.init_new_meeting(message.from_user.id)
        
        calendar_keyboard = await UserKeyboards.calendar_keyboard(0)
        delete_message = await message.answer(f"Введите дату конференции:", reply_markup=calendar_keyboard.as_markup(resize_keyboard=True))
        
        await state.update_data(message_id=delete_message.message_id)
        await state.set_state(CreateMeetingStates.get_date)
    except UserNotRegError:
        delete_message = await message.answer(f"{Emojis.ALLERT} Вы не зарегистрированы! {Emojis.ALLERT}\nДля регистрации введите команду /start", reply_markup=ReplyKeyboardRemove())
        await state.update_data(message_id=delete_message.message_id)


@router.callback_query(F.data, StateFilter(CreateMeetingStates.get_date))
async def get_date(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
        Получение даты конференции

    Args:
        callback (CallbackQuery): This object represents an incoming callback query from a callback button in an `inline keyboard
        state (FSMContext): Base class for all FSM storages
        bot (Bot): Bot class
    """
    data = json.loads(callback.data)
    
    if data['key'] == 'month_shift':
        calendar_keyboard = await UserKeyboards.calendar_keyboard(data['value'])
        await bot.edit_message_reply_markup(chat_id=callback.message.chat.id, message_id=callback.message.message_id, reply_markup=calendar_keyboard.as_markup(resize_keyboard=True))
    
    elif data['key'] == 'date':
        await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text='⏳ Ищу свободные временные интервалы...')
        await CheckData(callback.from_user.id).checking_the_date_for_accuracy(data['value'])
        
        start_time_keyboard = await UserKeyboards.start_time_keyboard(callback.from_user.id)
        await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text='Выберите время начала конфренции:', reply_markup=start_time_keyboard.as_markup(resize_keyboard=True))
        
        await state.set_state(CreateMeetingStates.get_start_time)
    elif not (data['key']):
        await callback.answer(text="Эта кнопка ничего не делает.", show_alert=True)
    

@router.callback_query(F.data, StateFilter(CreateMeetingStates.get_start_time))
async def get_start_time(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
        Получение времени начала конференции

    Args:
        callback (CallbackQuery): This object represents an incoming callback query from a callback button in an `inline keyboard
        state (FSMContext): Base class for all FSM storages
        bot (Bot): Bot class
    """
    data = json.loads(callback.data)

    message_log = False
    if data['key'] == 'back':
        
        calendar_keyboard = await UserKeyboards.calendar_keyboard(0)
        delete_message = await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text="Введите дату конференции:", reply_markup=calendar_keyboard.as_markup(resize_keyboard=True))
        
        await state.update_data(message_id=delete_message.message_id)
        await state.set_state(CreateMeetingStates.get_date)
    elif data['key'] == 'start_time':
        try:
            await CheckData(callback.from_user.id).checking_the_start_time_for_accuracy(data['value'])
            
            duration_keyboard = await UserKeyboards.duration_keyboard(callback.from_user.id)
            delete_message = await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text='Выберите продолжительность конференции', reply_markup=duration_keyboard.as_markup(resize_keyboard=True))
            
            await state.update_data(message_id=delete_message.message_id)
            await state.set_state(CreateMeetingStates.get_duration)
        except LongTimeInputError:
            message_log = await callback.message.answer("Ваше время начала пересекается с другой конференцией")
    if message_log: await send_log_message(callback, bot, message_log)


@router.callback_query(F.data, StateFilter(CreateMeetingStates.get_duration))
async def get_duration_meeting(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
        Получение продолжительности конференции

    Args:
        callback (CallbackQuery): This object represents an incoming callback query from a callback button in an `inline keyboard
        state (FSMContext): Base class for all FSM storages
        bot (Bot): Bot class
    """
    data = json.loads(callback.data)
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
    user_id = callback.from_user.id
    message_log = False
    if data['key'] == 'back':
        
        start_time_keyboard = await UserKeyboards.start_time_keyboard(user_id)
        delete_message = await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text='Выберите время начала конфренции:', reply_markup=start_time_keyboard.as_markup(resize_keyboard=True))
        
        await state.update_data(message_id=delete_message.message_id)
        await state.set_state(CreateMeetingStates.get_start_time)
    elif data['key'] == 'duration':
        try:
            await CheckData(user_id).checking_the_duration_meeting_for_accuracy(data['value'])
            
            record_keyboard = await UserKeyboards.ultimate_keyboard('record')
            delete_message = await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text='Вам нужно автоматически записывать вашу конференцию?:', reply_markup=record_keyboard.as_markup(resize_keyboard=True))
            
            await state.update_data(message_id=delete_message.message_id)
            await state.set_state(CreateMeetingStates.get_auto_recording)
        except LongTimeInputError:
            message_log = await callback.message.answer("Ваша конференция пересекается с другой, выберите значение поменьше")
        except DataInputError:
            message_log = await callback.message.answer("Кажется вы ввели данные в неправильном формате, попробуйте еще раз!")
    if message_log: await send_log_message(callback, bot, message_log)


@router.callback_query(F.data, StateFilter(CreateMeetingStates.get_auto_recording))
async def get_auto_recording(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
        Получение значения автоматической записи конференции
    Args:
        callback (CallbackQuery): CallbackQuery class
        state (FSMContext): FSMContext class
        bot (Bot): Bot class
    """
    data = json.loads(callback.data)
    if data['key'] == 'back':        
        duration_keyboard = await UserKeyboards.duration_keyboard(callback.from_user.id)
        delete_message = await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text='Выберите продолжительность конференции', reply_markup=duration_keyboard.as_markup(resize_keyboard=True))
        
        await state.update_data(message_id=delete_message.message_id)
        await state.set_state(CreateMeetingStates.get_duration)
    elif data['key'] == 'choice':
        await CheckData(callback.from_user.id).check_record_for_accuracy(data['value'])
        
        back_to_record_keyboard = await UserKeyboards.ultimate_keyboard()
        delete_message = await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text='Введите название вашей конференции:', reply_markup=back_to_record_keyboard.as_markup(resize_keyboard=True))
        
        await state.update_data(message_id=delete_message.message_id)
        await state.set_state(CreateMeetingStates.get_name_create_meeting)


@router.callback_query(F.data, StateFilter(CreateMeetingStates.get_name_create_meeting))
async def get_name_create_meeting(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
        Возврат назад к получению значения автоматической записи конференции

    Args:
        callback (CallbackQuery): CallbackQuery class
        state (FSMContext): FSMContext class
        bot (Bot): Bot class
    """
    data = json.loads(callback.data)
    if data['key'] == 'back':
        
        record_keyboard = await UserKeyboards.ultimate_keyboard('record')
        delete_message = await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text='Вам нужно автоматически записывать вашу конференцию?:', reply_markup=record_keyboard.as_markup(resize_keyboard=True))
        
        await state.update_data(message_id=delete_message.message_id)
        await state.set_state(CreateMeetingStates.get_auto_recording)
     
        
@router.message(F.text, StateFilter(CreateMeetingStates.get_name_create_meeting))
async def get_name_create_meeting(message: Message, state: FSMContext, bot: Bot) -> None:
    """
        Создание конференции и вывод ссылок на конференцию

    Args:
        message (Message): This object represents a message.
        state (FSMContext): FSMContext class
        bot (Bot): Bot class
    """
    
    load_message = await message.answer("Ваша конференция создается...")
    meeting_data = await MinorOperations.fill_meeting_data_credits(message.from_user.id, message.text)
    account = await MinorOperations.fill_account_credits(meeting_data[2])
    try:
        try:
            answer = await create_and_get_meeting_link(account, meeting_data[0])
            message_log = await message.answer(f"{Emojis.SUCCESS} Конференция создана {Emojis.SUCCESS}\n\nПочта аккаунта: {account.name}\nНазвание: {meeting_data[0].topic}\nДата и время начала: {(meeting_data[0].start_time + timedelta(hours=3)).strftime('%d.%m.%Y %H:%M')}\nПродолжительность: {meeting_data[0].duration} минут\n\nПригласительная ссылка: {answer[1]}\n\nИдентификатор конференции: {answer[2]}\nКод доступа: {meeting_data[1]}", reply_markup=ReplyKeyboardRemove(), disable_web_page_preview=True)
            
            await bot.delete_message(chat_id=message.chat.id, message_id=(await state.get_data()).get('message_id'))
            await bot.delete_message(chat_id=message.chat.id, message_id=load_message.message_id)
            
            await CreateMeetingService.save_created_conference(message.from_user.id, meeting_data[0], account.name)
            await UserService.update_number_created_conferences(message.from_user.id)
        except Exception as e:
            logging.error(f"Error during create meeting: {e}")
            await bot.send_message(chat_id='5890864355', text=f'Неизвестная ошибка бота!!!\nID пользователя: {message.from_user.id}\n{e}')
        await state.clear()
    except CreateMeetingError:
      await message.answer("Неудалось создать конференцию, обратитесь в техническую поддержку")
      await state.clear()
    if message_log: await send_log_message(message, bot, message_log)