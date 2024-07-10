# -*- coding: UTF-8 -*-

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from datetime import datetime, timedelta
import logging
import asyncio
from aiogram.utils import exceptions
from data_storage.data_storage_classes import CreateMeetingStates
from helper_classes.assistant import MinorOperations
from database.initialization import Initialization
from database.interaction import Interaction
from database.check_data import CheckData

from data_storage.keyboards import  Keyboards

from zoom_api.zoom import create_and_get_meeting_link

from exceptions import *



async def register_handlers_create_meeting(dp: Dispatcher) -> None:
    dp.register_message_handler(get_zoom, state=CreateMeetingStates.get_zoom)
    dp.register_message_handler(get_date, state=CreateMeetingStates.get_date)
    dp.register_message_handler(get_start_time, state=CreateMeetingStates.get_start_time)
    dp.register_message_handler(get_duration_meeting, state=CreateMeetingStates.get_duration)
    dp.register_message_handler(get_auto_recording, state=CreateMeetingStates.get_auto_recording)
    dp.register_message_handler(get_name_create_meeting, state=CreateMeetingStates.get_name_create_meeting)


helper = MinorOperations()
db = Interaction(
	user= helper.get_login(),
	password= helper.get_password()
)


async def start_create_new_meeting(message: types.Message, state: FSMContext) -> None:
    """
    Инициализация пользователя
    """
    await state.finish()
    user = Initialization(message.from_user.id)
    keyboard = Keyboards(message.from_user.id)
    await user.init_user()
    await user.delete_user_meeting_data()
    await message.answer("Выберите аккаунт zoom:", reply_markup=await keyboard.ultimate_keyboard('zoom'))
    await state.set_state(CreateMeetingStates.get_zoom.state)


async def get_zoom(message: types.Message, state: FSMContext) -> None:
    """
    Выбор зума для конференции
    """
    control = CheckData(message.from_user.id)
    keyboard = Keyboards(message.from_user.id)
    try:
      response = await control.check_zoom_for_accuracy(message.text)
      await message.answer(f"Выбран zoom №{message.text}: {response}", reply_markup=types.ReplyKeyboardRemove())
      await message.answer("Введите дату конференции:", reply_markup = await keyboard.calendar_keyboard())
      await state.set_state(CreateMeetingStates.get_date.state)
    except DataInputError:
      await message.answer("Введены данные неправильного формата, пожалйста выберите zoom используя клавиатуру ниже" )



async def get_date(message: types.Message, state: FSMContext) -> None:
    """
    Получение даты конференции
    """
    control = CheckData(message.from_user.id)
    keyboard = Keyboards(message.from_user.id)
    if message.text == "Вернуться назад":
      await message.answer("Выберите аккаунт zoom:", reply_markup=await keyboard.ultimate_keyboard('zoom'))
      await state.set_state(CreateMeetingStates.get_zoom.state)
    else:
      try:
          response = await control.checking_the_date_for_accuracy(message.text)
          illegal_intervals = await control.get_available_time_for_meeting(response)
          await message.answer("Теперь выберите время начала. Ниже в сообщении могут представлены недоступные вам временные интервалы уже запланированных конференций на введенную вами дату.", reply_markup= await keyboard.start_time_keyboard(illegal_intervals))
          if illegal_intervals:
          	for start, end in illegal_intervals:
                    await message.answer(f"{start.strftime('%H:%M')}-{end.strftime('%H:%M')}")
          await state.set_state(CreateMeetingStates.get_start_time.state)  

      except DataInputError:
          await message.answer("Кажется вы ввели данные в неправильном формате, попробуйте еще раз!")
					
					

            
     


async def get_start_time(message: types.Message, state: FSMContext) -> None:
    """
    Получение времени начала конференции
    """
    control = CheckData(message.from_user.id)
    keyboard = Keyboards(message.from_user.id)
    if message.text == "Вернуться назад":
      await message.answer("Введите дату конференции:", reply_markup = await keyboard.calendar_keyboard())
      await state.set_state(CreateMeetingStates.get_date.state)
    else:
      try:
          response = await control.checking_the_start_time_for_accuracy(message.text)
          await message.answer("Выберите продолжительность вашей конференции", reply_markup=await keyboard.duration_keyboard())
          await state.set_state(CreateMeetingStates.get_duration.state)
      except DataInputError:
          await message.answer("Кажется вы ввели данные в неправильном формате, попробуйте еще раз!")
      except HalfTimeInputError:
         await message.answer("Началом конференции может являтся время которое кратно 30 минутам, напрмер 10:00 или 10:30")
      except LongTimeInputError:
          await message.answer("Ваше время начала пересекается с другой конференцией")



async def get_duration_meeting(message: types.Message, state: FSMContext) -> None:
    """
    Получение продолжительности конференции
    """
    control = CheckData(message.from_user.id)
    keyboard = Keyboards(message.from_user.id)
    if message.text == "Вернуться назад":
        entered_date = await db.get_data(message.from_user.id, 'date')
        illegal_intervals = await db.get_data(message.from_user.id, 'illegal_intervals')
        await message.answer("Теперь выберите время начала. Ниже могут представлены недоступные вам временные интервалы уже запланированных конференций на введенную вами дату.", reply_markup= await keyboard.start_time_keyboard(illegal_intervals))
        await state.set_state(CreateMeetingStates.get_start_time.state)
    else:
        try:
            await control.checking_the_duration_meeting_for_accuracy(message.text)
            await message.answer("Вам нужно автоматически записывать вашу конференцию?:", reply_markup=await keyboard.ultimate_keyboard('record'))
            await state.set_state(CreateMeetingStates.get_auto_recording.state)
        except LongTimeInputError:
            await message.answer("Ваша конференция пересекается с другой, введите значение поменьше")
        except DataInputError:
            await message.answer("Кажется вы ввели данные в неправильном формате, попробуйте еще раз!")
        except HalfTimeInputError:
            await message.answer("Количество минут должно быть кратным 15")



async def get_auto_recording(message: types.Message, state: FSMContext) -> None:
    """
    Получение значения автоматической записи конференции
    """
    control = CheckData(message.from_user.id)
    keyboard = Keyboards(message.from_user.id)
    if message.text == "Вернуться назад":
        await message.answer("Выберите продолжительность вашей конференции", reply_markup=await keyboard.duration_keyboard())
        await state.set_state(CreateMeetingStates.get_duration.state)
    else:
        try:
            await control.check_record_for_accuracy(message.text)
            await message.answer("Введите название вашей конференции:", reply_markup=await keyboard.ultimate_keyboard('back_to_record'))
            await state.set_state(CreateMeetingStates.get_name_create_meeting.state)
        except DataInputError:
             await message.answer("Пожалуйста дайте ответ, используя кнопки предложенной клавиатуры")
        

            
async def get_name_create_meeting(message: types.Message, state: FSMContext) -> None:
    """
    Создание конференции и вывод ссылок на конференцию
    """
    keyboard = Keyboards(message.from_user.id)

    if message.text == "Вернуться назад":
        await message.answer("Вам нужно автоматически записывать вашу конференцию?:", reply_markup=await keyboard.ultimate_keyboard('record'))
        await state.set_state(CreateMeetingStates.get_auto_recording.state)
    else:    
        await message.answer("Ваша конференция создается...")
        meeting_data = await helper.fill_meeting_data_credits(message.from_user.id, message.text)
        account = await helper.fill_account_credits(message.from_user.id)
        try:
            try:
                logging.info('OK1')
                user = Initialization(message.from_user.id)
                logging.info('OK2')
                answer = await create_and_get_meeting_link(account, meeting_data[0])
                logging.info('OK3')
                
                #text1 = (
                #    f"Конференция создана:\nНазвание: {meeting_data[0].topic}\n"
                #    f"Дата и время начала: {(meeting_data[0].start_time + timedelta(hours=3)).strftime('%d.%m.%Y %H:%M')}"
                #)
                #await message.answer(text1, disable_web_page_preview=True)
                #await asyncio.sleep(1)
                #logging.info('OK4')
                #logging.info(answer[1])
                
                #text2 = (
                #    f"Продолжительность: {meeting_data[0].duration} минут\n\n"
                #    f"Пригласительная ссылка: {answer[1]}"
                #)
                #await message.answer(text2, disable_web_page_preview=True)
                #await asyncio.sleep(1)
                #logging.info('OK5')
                
                #text3 = (
                #    f"Идентификатор конференции: {answer[2]}\n"
                #    f"Код доступа: {meeting_data[1]}"
                #)
                #await message.answer(text3, disable_web_page_preview=True)
                #logging.info('OK6')
                await message.answer(f"Конференция создана:\nНазвание: {meeting_data[0].topic}\nДата и время начала: {(meeting_data[0].start_time + timedelta(hours=3)).strftime('%d.%m.%Y %H:%M')}\nПродолжительность: {meeting_data[0].duration} минут\n\nПригласительная ссылка: {answer[1]}\nИдентификатор конференции: {answer[2]}\nКод доступа: {meeting_data[1]}", reply_markup=types.ReplyKeyboardRemove, disable_web_page_preview=True)
                await user.update_data_about_created_conferences(message.from_user.username, (datetime.now()+timedelta(hours=3)).strftime('%Y-%m-%d %H:%M'))
                logging.info('OK4')
            except Exception as e:
                logging.error(f"Ошибка: {e}")
                #if 'Peer_flood' in e:
                #    await message.answer("Извините, слишком быстро отправляю сообщения. Попробуйте позже.")
                #else:
                #    raise e

            #await message.answer(f"Конференция создана:\nCсылка для организатора {answer[0]}", disable_web_page_preview=True)
            #await message.answer(f"Конференция создана:\nНазвание: {meeting_data[0].topic}\nДата и время начала: {meeting_data[0].start_time.strftime('%d.%m.%Y %H:%M')}\nПродолжительность: {meeting_data[0].duration} минут\n\nПригласительная ссылка: {answer[1]}\nИдентификатор конференции: {answer[2]}\nКод доступа: {meeting_data[1]}", disable_web_page_preview=True)
            await state.finish()
        except CreateMeetingError:
          await message.answer("Неудалось создать конференцию, обратитесь в техническую поддержку")
          await state.finish()
