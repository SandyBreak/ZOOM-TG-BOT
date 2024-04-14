# -*- coding: UTF-8 -*-

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from datetime import datetime, timedelta

from data_storage.data_storage_classes import GetPlannedMeetingStates
from helper_classes.assistant import MinorOperations
from database.initialization import Initialization
from database.interaction import Interaction
from database.check_data import CheckData


from data_storage.keyboards import  Keyboards

from zoom_api.zoom import get_list_meeting

from exceptions import *


async def register_handlers_get_planned_meetings(dp: Dispatcher):
    dp.register_message_handler(get_zoom, state=GetPlannedMeetingStates.get_zoom)
    dp.register_message_handler(get_date_and_get_planned_meetings, state=GetPlannedMeetingStates.get_date_and_get_planned_meetings)

helper = MinorOperations()
db = Interaction(
	user= helper.get_login(),
	password= helper.get_password()
)


async def get_planned_meetings(message: types.Message, state: FSMContext) -> None:
    """
    Старт заполнения данных
    """
    await state.finish()
    user = Initialization(message.from_user.id)
    keyboard = Keyboards(message.from_user.id)
    await user.init_user()
    await user.delete_user_meeting_data()
    await message.answer("Выберите аккаунт zoom:", reply_markup=await keyboard.ultimate_keyboard('zoom'))
    await state.set_state(GetPlannedMeetingStates.get_zoom.state)


async def get_zoom(message: types.Message, state: FSMContext) -> None:
    """
    Выбор zoom аккаунта
    """
    control = CheckData(message.from_user.id)
    keyboard = Keyboards(message.from_user.id)
    try:
      response = await control.check_zoom_for_accuracy(message.text)
      await message.answer(f"Выбран zoom №{message.text}: {response}", reply_markup=types.ReplyKeyboardRemove())
      await message.answer("Введите дату для которой хотите посмотреть запланированные конференции:", reply_markup = await keyboard.calendar_keyboard())
      await state.set_state(GetPlannedMeetingStates.get_date_and_get_planned_meetings.state)
    except DataInputError:
      await message.answer("Введены данные неправильного формата, пожалйста выберите zoom используя клавиатуру ниже" )

   
async def get_date_and_get_planned_meetings(message: types.Message, state: FSMContext) -> None:
    """
    Получение даты и вывод запланированных на нее конференций
    """
    control = CheckData(message.from_user.id)

    try:
        response = await control.checking_the_date_for_accuracy(message.text)
        await message.answer("Получение данных...", reply_markup=types.ReplyKeyboardRemove())
        try:
            account = await helper.fill_account_credits(message.from_user.id)
            meeting_list = await get_list_meeting(account, response)
            conf_log = 0
            for meeting in meeting_list['meetings']:
                start_time = meeting['start_time'].split('T')[0]
                if start_time == response:
                    topic = meeting['topic']
                    start_time = datetime.strptime(meeting['start_time'], '%Y-%m-%dT%H:%M:%SZ')
                    end_time = start_time + timedelta(minutes= meeting['duration'])
                    meeting_id = meeting['id']
                    conf_log = 1
                    await message.answer(f"Название: {topic},\nВремя начала: {(start_time+timedelta(hours=3)).strftime('%H:%M')},\nВремя окончания: {(end_time+timedelta(hours=3)).strftime('%H:%M')}\nID: {meeting_id}")
                await state.finish()
            if not(conf_log):
                await message.answer("На введенную вами дату конференции не запланированы")
                await state.finish()
        except GetListMeetingError:
             await message.answer("Неудалось получить список конференций, обратитесь в техническую поддержку")
    
    except DataInputError:
      await message.answer("Кажется вы ввели данные в неправильном формате, попробуйте еще раз!")
    

        
        



