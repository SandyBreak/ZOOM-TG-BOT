# -*- coding: UTF-8 -*-

from aiogram import types
from datetime import datetime, timedelta

from database.interaction import Interaction
from helper_classes.assistant import MinorOperations

helper = MinorOperations()

db = Interaction(
			user= helper.get_login(),
			password= helper.get_password()
		)



class Keyboards:
    def __init__(self, user_id) -> None:
        self.user_id = user_id


    async def ultimate_keyboard(self, type_keyboard: str) -> types.ReplyKeyboardMarkup:
        """
        Клавиатура выбора zoom аккаунта, типа записи конфы и кнопки назад для возвращения из состояния именовании конфы к типу записи конфы
        """
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = []

        if type_keyboard == 'zoom':
            buttons = ["1", "2", "3"]

        elif type_keyboard == 'record':
            keyboard.add("Вернуться назад")
            buttons = ["Да", "Нет"]

        elif type_keyboard == 'back_to_record':
            keyboard.add("Вернуться назад")

        if buttons:
            keyboard.add(*buttons)

        return keyboard


    async def calendar_keyboard(self) -> types.ReplyKeyboardMarkup:
        """
        Клавиатура с календарем
        """ 
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

        buttons = []
        keyboard.add("Вернуться назад")

        now = datetime.now()

        current_month = now.month

        keyboard.add(datetime.now().strftime('%B'))

        for i in range(0, 5*7*3+int(now.isoweekday())):
            day = now + timedelta(days=i)
            buttons.append(day.strftime('%d.%m'))

            if day.strftime('%A') == 'Sunday':

                if len(buttons) != 7 and len(buttons) != 0:

                    for a in range(0, 7 - len(buttons)):
                        buttons.insert(0, "----")

                keyboard.row(*buttons)
                buttons = []

            if day.month != current_month:
            if buttons:  # Проверка на пустой список
                buttons.pop()

            if len(buttons) != 7 and len(buttons) != 0:
                for a in range(0, 7 - len(buttons)):
                    buttons.append("----")

                keyboard.row(*buttons)
                keyboard.add(day.strftime('%B'))
                buttons = []
                buttons.append(day.strftime('%d.%m'))
                current_month = day.month

        if len(buttons) != 7 and len(buttons) != 0:
                    for a in range(0, 7 - len(buttons)):
                        buttons.append("----")

        keyboard.row(*buttons)
        keyboard.add("Ввести другое значение")

        return keyboard


    async def start_time_keyboard(self, no_access_intervals: dict) -> types.ReplyKeyboardMarkup:
        """
        Клавиатура с временем начала конференции
        """
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = []
        keyboard.add("Вернуться назад")

        entered_date = await db.get_data(self.user_id, 'date')

        time_slots = []
        start_time = datetime.strptime(entered_date + "09:00", '%Y-%m-%d%H:%M')
        end_time = datetime.strptime(entered_date + "19:00", '%Y-%m-%d%H:%M')

        current_slot_start = start_time

        while current_slot_start < end_time:
            current_slot_end = current_slot_start + timedelta(minutes=30)
            time_slots.append(current_slot_start)
            current_slot_start = current_slot_end

        available_time_slots = []
        response_logs = []

        if no_access_intervals:
          for slot in time_slots:
              for start, end in no_access_intervals:
                  if not(start <= slot < end) and (slot > datetime.now()):
                      response_logs.append('True')
                  else:
                      response_logs.append('False')
              if 'False' in response_logs:
                  response_logs = []
              else:
                  available_time_slots.append(slot)
                  response_logs = []
        else:
          for slot in time_slots:
              if (slot > datetime.now()):
                available_time_slots.append(slot)

        for ctr in range(0, len(available_time_slots)-1, 2):
            buttons.append(available_time_slots[ctr].strftime('%H:%M'))
            buttons.append(available_time_slots[ctr+1].strftime('%H:%M'))
            keyboard.row(*buttons)
            buttons=[]

        return keyboard



    async def duration_keyboard(self) -> types.ReplyKeyboardMarkup:
        """
        Клавиатура с длительностью конференции
        """
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = []
        keyboard.add("Вернуться назад")
        
        start_time = await db.get_data(self.user_id, 'start_time')
        entered_date = await db.get_data(self.user_id, 'date')
        illegal_intervals = await db.get_data(self.user_id, 'illegal_intervals')
    
        start_time = datetime.strptime(entered_date + start_time, '%Y-%m-%d%H:%M')
        end_meeting = datetime.strptime(entered_date + "19:00", '%Y-%m-%d%H:%M')
    
        for start, end in illegal_intervals:
            if (start > start_time):
                end_meeting = start
                break
            
        current_slot_start = start_time

        while current_slot_start < end_meeting:
            current_slot_end = current_slot_start + timedelta(minutes=30)
            duration = current_slot_end-start_time
            buttons.append(str(duration)[:-3])
            current_slot_start = current_slot_end
        
        keyboard.add(*buttons)

        return keyboard
