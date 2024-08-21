# -*- coding: UTF-8 -*-

from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta
from aiogram import Router, F, Bot
import logging


from data_storage.states import CreateMeetingStates
from helper_classes.assistant import MinorOperations
from database.mongodb.interaction import Interaction
from zoom_api.zoom import create_and_get_meeting_link
from database.mongodb.check_data import CheckData
from data_storage.keyboards import  Keyboards
from exceptions import *


mongodb_interface = Interaction()
helper = MinorOperations()
bank_of_keys = Keyboards()
router = Router()

    


@router.message(Command(commands=['create', 'reset']))
async def start_create_new_meeting(message: Message, state: FSMContext) -> None:
    """
    Инициализация пользователя
    """
    await state.clear()
    await mongodb_interface.init_user(message.from_user.id, message.from_user.username, message.from_user.full_name)
    await mongodb_interface.delete_user_meeting_data(message.from_user.id)
    
    calendar_keyboard = await bank_of_keys.calendar_keyboard()
    await message.answer("Введите дату конференции:", reply_markup=calendar_keyboard.as_markup(resize_keyboard=True, one_time_keyboard=True))
    
    await state.set_state(CreateMeetingStates.get_date)



@router.message(F.text, StateFilter(CreateMeetingStates.get_date))
async def get_date(message: Message, state: FSMContext) -> None:
    """
    Получение даты конференции
    """
    try:
        await message.answer("⏳ Ищу свободные временные интервалы...")
        illegal_intervals = await CheckData(message.from_user.id).checking_the_date_for_accuracy(message.text)
        start_time_keyboard = await bank_of_keys.start_time_keyboard(message.from_user.id, illegal_intervals)
        await message.answer("Теперь выберите время начала конфренции:", reply_markup=start_time_keyboard.as_markup(resize_keyboard=True, one_time_keyboard=True))
            
        await state.set_state(CreateMeetingStates.get_start_time)  
    except DataInputError:
        await message.answer("Кажется вы ввели данные в неправильном формате, попробуйте еще раз!")


@router.message(F.text, StateFilter(CreateMeetingStates.get_start_time))
async def get_start_time(message: Message, state: FSMContext) -> None:
    """
    Получение времени начала конференции
    """

    if message.text == "Вернуться назад":
        calendar_keyboard = await bank_of_keys.calendar_keyboard()
        await message.answer("Введите дату конференции:", reply_markup =calendar_keyboard.as_markup(resize_keyboard=True, one_time_keyboard=True))
        await state.set_state(CreateMeetingStates.get_date)
    else:
        
        try:
            response = await CheckData(message.from_user.id).checking_the_start_time_for_accuracy(message.text)
            duration_keyboard = await bank_of_keys.duration_keyboard(message.from_user.id)
            await message.answer("Выберите продолжительность вашей конференции", reply_markup=duration_keyboard.as_markup(resize_keyboard=True, one_time_keyboard=True))
            await state.set_state(CreateMeetingStates.get_duration)
        except DataInputError:
            await message.answer("Кажется вы ввели данные в неправильном формате, попробуйте еще раз!")
        except HalfTimeInputError:
            await message.answer("Началом конференции может являтся время которое кратно 30 минутам, напрмер 10:00 или 10:30")
        except LongTimeInputError:
            await message.answer("Ваше время начала пересекается с другой конференцией")


@router.message(F.text, StateFilter(CreateMeetingStates.get_duration))
async def get_duration_meeting(message: Message, state: FSMContext) -> None:
    """
    Получение продолжительности конференции
    """

    if message.text == "Вернуться назад":
        entered_date = await mongodb_interface.get_data(message.from_user.id, 'date')
        illegal_intervals = await mongodb_interface.get_data(message.from_user.id, 'illegal_intervals')
        start_time_keyboard = await bank_of_keys.start_time_keyboard(message.from_user.id, illegal_intervals)
        await message.answer("Теперь выберите время начала. Ниже могут представлены недоступные вам временные интервалы уже запланированных конференций на введенную вами дату.", reply_markup=start_time_keyboard.as_markup(resize_keyboard=True, one_time_keyboard=True))
        await state.set_state(CreateMeetingStates.get_start_time)
    else:
        try:
            record_keyboard = await bank_of_keys.ultimate_keyboard('record')
            await CheckData(message.from_user.id).checking_the_duration_meeting_for_accuracy(message.text)
            await message.answer("Вам нужно автоматически записывать вашу конференцию?:", reply_markup=record_keyboard.as_markup(resize_keyboard=True, one_time_keyboard=True))
            await state.set_state(CreateMeetingStates.get_auto_recording)
        except LongTimeInputError:
            await message.answer("Ваша конференция пересекается с другой, введите значение поменьше")
        except DataInputError:
            await message.answer("Кажется вы ввели данные в неправильном формате, попробуйте еще раз!")
        except HalfTimeInputError:
            await message.answer("Количество минут должно быть кратным 15")


@router.message(F.text, StateFilter(CreateMeetingStates.get_auto_recording))
async def get_auto_recording(message: Message, state: FSMContext) -> None:
    """
    Получение значения автоматической записи конференции
    """

    if message.text == "Вернуться назад":
        duration_keyboard = await bank_of_keys.duration_keyboard(message.from_user.id)
        await message.answer("Выберите продолжительность вашей конференции", reply_markup=duration_keyboard.as_markup(resize_keyboard=True, one_time_keyboard=True))
        await state.set_state(CreateMeetingStates.get_duration)
    else:
        try:
            await CheckData(message.from_user.id).check_record_for_accuracy(message.text)
            back_to_record_keyboard = await bank_of_keys.ultimate_keyboard('back_to_record')
            await message.answer("Введите название вашей конференции:", reply_markup=back_to_record_keyboard.as_markup(resize_keyboard=True, one_time_keyboard=True))
            await state.set_state(CreateMeetingStates.get_name_create_meeting)
        except DataInputError:
            await message.answer("Пожалуйста дайте ответ, используя кнопки предложенной клавиатуры")
        

@router.message(F.text, StateFilter(CreateMeetingStates.get_name_create_meeting))
async def get_name_create_meeting(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Создание конференции и вывод ссылок на конференцию
    """
    if message.text == "Вернуться назад":
        record_keyboard = await bank_of_keys.ultimate_keyboard('record')
        await message.answer("Вам нужно автоматически записывать вашу конференцию?:", reply_markup=record_keyboard.as_markup(resize_keyboard=True, one_time_keyboard=True))
        await state.set_state(CreateMeetingStates.get_auto_recording)
    else:    
        await message.answer("Ваша конференция создается...")
        meeting_data = await helper.fill_meeting_data_credits(message.from_user.id, message.text)
        account = await helper.fill_account_credits(meeting_data[2])
        try:
            try:

                answer = await create_and_get_meeting_link(account, meeting_data[0])
                await message.answer(f"Конференция создана:\nНазвание: {meeting_data[0].topic}\nДата и время начала: {(meeting_data[0].start_time + timedelta(hours=3)).strftime('%d.%m.%Y %H:%M')}\nПродолжительность: {meeting_data[0].duration} минут\n\nПригласительная ссылка: {answer[1]}\nИдентификатор конференции: {answer[2]}\nКод доступа: {meeting_data[1]}", reply_markup=ReplyKeyboardRemove(), disable_web_page_preview=True)
                await mongodb_interface.update_data_about_created_conferences(message.from_user.username, (datetime.now()+timedelta(hours=3)).strftime('%Y-%m-%d %H:%M'))
            except Exception as e:
                logging.error(f"Error during create meeting: {e}")
                await bot.send_message(chat_id='5890864355', text=f'Неизвестная ошибка бота!!!\nID пользователя: {message.from_user.id}\n{e}')
            await state.clear()
        except CreateMeetingError:
          await message.answer("Неудалось создать конференцию, обратитесь в техническую поддержку")
          await state.clear()
