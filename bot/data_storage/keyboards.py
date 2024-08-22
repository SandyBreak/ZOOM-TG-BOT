# -*- coding: UTF-8 -*-

from aiogram.utils.keyboard import KeyboardButton, ReplyKeyboardBuilder
from datetime import datetime, timedelta


from database.mongodb.interaction import Interaction
from helper_classes.assistant import MinorOperations


mongodb_interface = Interaction()
helper = MinorOperations()


class Keyboards:
    def __init__(self) -> None:
        pass

    async def ultimate_keyboard(self, type_keyboard: str) -> ReplyKeyboardBuilder:
        """
        Клавиатура выбора типа записи конфы и кнопки назад для возвращения из состояния именовании конфы к типу записи конфы
        """
        keyboard = ReplyKeyboardBuilder()
        buttons = []
        keyboard.row(KeyboardButton(text="Вернуться назад"))
        if type_keyboard == 'record':           
            buttons.append(KeyboardButton(text="Да"))
            buttons.append(KeyboardButton(text="Нет"))
            keyboard.row(*buttons)
        return keyboard


    async def calendar_keyboard(self) -> ReplyKeyboardBuilder:
        """
        Клавиатура с календарем
        """ 
        builder = ReplyKeyboardBuilder()
        buttons = []
        builder.row(KeyboardButton(text="Вернуться назад"))

        now = datetime.now()

        current_month = now.month

        builder.row(KeyboardButton(text=datetime.now().strftime('%B')))

        for i in range(0, 5*7*3+int(now.isoweekday())):
            day = now + timedelta(days=i)
            buttons.append(KeyboardButton(text=day.strftime('%d.%m')))

            if day.strftime('%A') == 'Sunday':

                if len(buttons) != 7 and len(buttons) != 0:

                    for a in range(0, 7 - len(buttons)):
                        buttons.insert(0, KeyboardButton(text=f'----'))

                builder.row(*buttons)
                buttons = []
    
            if day.month != current_month:
                if buttons:  # Проверка на пустой список
                    buttons.pop()

                if len(buttons) != 7 and len(buttons) != 0:

                    for a in range(0, 7 - len(buttons)):
                        buttons.append(KeyboardButton(text=f"----"))

                builder.row(*buttons)
                builder.row(KeyboardButton(text=day.strftime('%B')))
                buttons = []
                buttons.append(KeyboardButton(text=day.strftime('%d.%m')))
                current_month = day.month

        if len(buttons) != 7 and len(buttons) != 0:
                    for a in range(0, 7 - len(buttons)):
                        buttons.append(KeyboardButton(text="----"))

        builder.row(*buttons)

        return builder



    async def start_time_keyboard(self, user_id: int, illegal_intervals: dict) -> ReplyKeyboardBuilder:
        """
        Клавиатура с временем начала конференции
        """
        builder = ReplyKeyboardBuilder()
        buttons = []
        builder.row(KeyboardButton(text="Вернуться назад"))

        entered_date = await mongodb_interface.get_data(user_id, 'date')
        available_time_slots = []
        response_logs = []
        
        if illegal_intervals:
            for account_intervals in illegal_intervals:
                time_slots = []
                start_time = datetime.strptime(entered_date + "09:00", '%Y-%m-%d%H:%M')
                end_time = datetime.strptime(entered_date + "19:00", '%Y-%m-%d%H:%M')
        
                current_slot_start = start_time
        
                while current_slot_start < end_time:
                    current_slot_end = current_slot_start + timedelta(minutes=30)
                    time_slots.append(current_slot_start)
                    current_slot_start = current_slot_end
        
                for slot in time_slots:
                    for start, end in account_intervals:
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
        
        
        sorted_available_time_slots = list(set(available_time_slots))
        sorted_available_time_slots = sorted(sorted_available_time_slots, key=lambda x: x)
        
        for slot in sorted_available_time_slots:
            print(slot, type(slot))
        for ctr in range(0, len(sorted_available_time_slots)-1, 2):
            buttons.append(KeyboardButton(text=sorted_available_time_slots[ctr].strftime('%H:%M')))
            buttons.append(KeyboardButton(text=sorted_available_time_slots[ctr+1].strftime('%H:%M')))    
            builder.row(*buttons)
            buttons=[]

        return builder



    async def duration_keyboard(self, user_id: int) -> ReplyKeyboardBuilder:
        """
        Клавиатура с длительностью конференции
        """
        builder = ReplyKeyboardBuilder()
        buttons = []
        builder.row(KeyboardButton(text="Вернуться назад"))
        
        start_time = await mongodb_interface.get_data(user_id, 'start_time')
        entered_date = await mongodb_interface.get_data(user_id, 'date')
        illegal_intervals = await mongodb_interface.get_data(user_id, 'illegal_intervals')
    
        start_time = datetime.strptime(entered_date + start_time, '%Y-%m-%d%H:%M')
        end_meeting = datetime.strptime(entered_date + "19:00", '%Y-%m-%d%H:%M')
        for account_intervals in illegal_intervals:
            for start, end in account_intervals:
                if (start > start_time):
                    end_meeting = start
                    break
            
        current_slot_start = start_time
        quantity_buttons = 0
        
        while current_slot_start < end_meeting:
            current_slot_end = current_slot_start + timedelta(minutes=30)
            duration = current_slot_end-start_time
            
            buttons.append(KeyboardButton(text=str(duration)[:-3]))
            
            quantity_buttons+=1
            current_slot_start = current_slot_end
            
            if quantity_buttons == 2:
                builder.row(*buttons)
                buttons = []
                quantity_buttons = 0
        
        builder.row(*buttons)

        return builder
