# -*- coding: UTF-8 -*-

from datetime import datetime, timedelta
from typing import Optional
import json 

from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from googletrans import Translator

from services.postgres.create_meeting_service import CreateMeetingService

from utils.assistant import MinorOperations


class UserKeyboards:
    def __init__(self) -> None:
        pass
    
    @staticmethod
    async def ultimate_keyboard(type_keyboard: Optional[str] = None) -> InlineKeyboardBuilder:
        """
            Клавиатура выбора типа записи конфы и кнопки назад для возвращения из состояния именовании конфы к типу записи конфы

        Args:
            type_keyboard (Optional[str], optional): Defaults to None. Если record то создается клавиатура с типом записи, если None то просто клавиатура с кнопкой назад.

        Returns:
            InlineKeyboardBuilder: Клавиатура записи конференции
        """
        builder = InlineKeyboardBuilder()
        buttons = []
        
        builder.row(InlineKeyboardButton(text="Вернуться назад", callback_data=json.dumps({'key': 'back'}))) # Кнопка для возврата назад
        if type_keyboard == 'record':           
            buttons.append(InlineKeyboardButton(text="Да", callback_data=json.dumps({'key': 'choice', 'value': 'cloud'})))
            buttons.append(InlineKeyboardButton(text="Нет", callback_data=json.dumps({'key': 'choice', 'value': 'none'})))
            builder.row(*buttons)
        return builder


    @staticmethod
    async def calendar_keyboard(month_shift: int) -> InlineKeyboardBuilder:
        """
            Клавиатура для генерации календаря

        Args:
            month_shift (int): Значение смещения месяца относительно текущего

        Returns:
            InlineKeyboardBuilder: Клавиатура с календарем
        """
        builder = InlineKeyboardBuilder()
        buttons = []
        today = datetime.now()
        
        if month_shift:
            next_month = today.month + month_shift # Переходим к следующему месяцу
            if next_month > 12:
                next_month %= 12
                if not(next_month):
                    next_month = 1
                next_year = today.year +1
            else:
                next_year = today.year  # Год остается тем же     
            first_day = datetime(next_year, next_month, 1)
        else:
            first_day = today
            
        if first_day.month == 12:
            last_day_of_month = datetime(first_day.year + 1, 1, 1)
        else:
            last_day_of_month = datetime(first_day.year, first_day.month + 1, 1)
        
        # Фикс ошибки перевода
        if first_day.strftime('%B') == 'March':
            builder.row(InlineKeyboardButton(text='Март' + f" {first_day.strftime('%Y')}", callback_data=json.dumps({'key': None})))
        elif first_day.strftime('%B') == 'May':
            builder.row(InlineKeyboardButton(text='Май' + f" {first_day.strftime('%Y')}", callback_data=json.dumps({'key': None})))
        else:
            builder.row(InlineKeyboardButton(text=Translator().translate(first_day.strftime('%B'), src='en', dest='ru').text + f" {first_day.strftime('%Y')}", callback_data=json.dumps({'key': None})))
        
        
        week_days_ru = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС']
        for day in week_days_ru:
            buttons.append(InlineKeyboardButton(text=day, callback_data=json.dumps({'key': None})))
        builder.row(*buttons)
        buttons = []
        
        intermediate_date = first_day
        
        while intermediate_date < last_day_of_month:
            buttons.append(InlineKeyboardButton(text=intermediate_date.strftime('%d'), callback_data=json.dumps({'key': 'date', 'value':f"{intermediate_date.strftime('%d.%m')}"})))
            
            # Если день - воскресенье, добавляем строку кнопок
            if intermediate_date.strftime('%A') == 'Sunday':

                if len(buttons) != 7 and len(buttons) != 0:
                    # Заполняем пустые кнопки до 7
                    for a in range(0, 7 - len(buttons)):
                        buttons.insert(0, InlineKeyboardButton(text=f'----', callback_data=json.dumps({'key': None})))

                builder.row(*buttons)  # Добавляем строку в клавиатуру
                buttons = []  # Очищаем список кнопок
            intermediate_date += timedelta(days=1)  # Переходим к следующему дню

        # Завершение добавления кнопок        
        first_day_last_week = int(datetime(first_day.year, first_day.month, int((buttons[0]).text)).strftime('%u'))
        if (first_day_last_week - 1) != 0:
            for a in range(0, first_day_last_week-1):
                buttons.insert(0, InlineKeyboardButton(text=f'----', callback_data=json.dumps({'key': None})))
            
        if len(buttons) != 7 and len(buttons) != 0:
            for a in range(0, 7 - len(buttons)):
                buttons.append(InlineKeyboardButton(text="----", callback_data=json.dumps({'key': None})))  # Заполняем пустые кнопки до 7
            
        builder.row(*buttons)  # Добавляем последнюю строку кнопок
        buttons=[]
        
        if first_day == today:
            builder.row(InlineKeyboardButton(text="След. месяц", callback_data=json.dumps({'key': 'month_shift', 'value': month_shift+1})))# Заполняем пустые кнопки до 7
        else:
            buttons.append(InlineKeyboardButton(text="Пред. месяц", callback_data=json.dumps({'key': 'month_shift', 'value': month_shift-1})))
            buttons.append(InlineKeyboardButton(text="След. месяц", callback_data=json.dumps({'key': 'month_shift', 'value': month_shift+1})))
            builder.row(*buttons)  # Добавляем навигацию
        
        
        return builder


    @staticmethod
    async def start_time_keyboard(user_id: int) -> InlineKeyboardBuilder:
        """
            Клавиатура с доступными временными интервалами для начала конференции.

        Args:
            user_id (int): callback.from_user.id Телеграмм id аккаунта пользователя.

        Returns:
            InlineKeyboardBuilder: Клавиатура с возможным временем начала конфреренции
        """
        builder = InlineKeyboardBuilder()
        buttons = []
        builder.row(InlineKeyboardButton(text="Вернуться назад", callback_data=json.dumps({'key': 'back'}))) # Кнопка для возврата назад

        entered_date = await CreateMeetingService.get_data(user_id, 'date')
        illegal_intervals = await CreateMeetingService.get_data(user_id, 'illegal_intervals')
                
        available_time_slots = [] # Список доступных временных интервалов
        
        time_slots = await MinorOperations.create_worktime_slots(entered_date)
        
        
        if illegal_intervals:# Если есть недопустимые интервалы
            for account_intervals in illegal_intervals.values(): # Делаем проверку для каждого аккаунта в которомуже есть недопустимые интервалы для создания конференций
                for slot in time_slots: # Проверка временных слотов на пересечение с недопустимыми интервалами
                    if await MinorOperations.is_slot_valid(slot, account_intervals):  # Если пересечений нету добавляем слот
                        available_time_slots.append(slot)
                    else: # Если есть пересечение переходим к следующему слоту
                        continue
        else:# Если нет недопустимых интервалов, добавляем сразу все слоты
            for slot in time_slots:
                if (slot > datetime.now()):
                  available_time_slots.append(slot)
        
        # Удаляем дубликаты и сортируем доступные временные слоты
        sorted_available_time_slots = list(set(available_time_slots))
        sorted_available_time_slots = sorted(sorted_available_time_slots, key=lambda x: x)
        
        # Формируем кнопки для клавиатуры
        for ctr in range(0, len(sorted_available_time_slots)-1, 2):
            #Создаем и добавляем кнопки
            buttons.append(InlineKeyboardButton(text=sorted_available_time_slots[ctr].strftime('%H:%M'), callback_data=json.dumps({'key': 'start_time', 'value': sorted_available_time_slots[ctr].strftime('%H:%M')}) ))  # Кнопка с временем 1
            buttons.append(InlineKeyboardButton(text=sorted_available_time_slots[ctr + 1].strftime('%H:%M'), callback_data=json.dumps({'key': 'start_time', 'value': sorted_available_time_slots[ctr + 1].strftime('%H:%M')}) ))  # Кнопка с временем 1))  # Кнопка с временем 2
            builder.row(*buttons)  # Добавляем строку из 2 кнопок в клавиатуру
            buttons = []  # Очищаем список кнопок

        return builder
    
    
    @staticmethod
    async def duration_keyboard(user_id: int) -> InlineKeyboardBuilder:
        """
            Генерация клавиатуры c доступной длительностью конференции
            
        Args:
            user_id (int): callback.from_user.id Телеграмм id аккаунта пользователя.

        Returns:
            InlineKeyboardBuilder: Клавиатура c доступной длительностью конференции
        """
        builder = InlineKeyboardBuilder()
        buttons = []
        
        builder.row(InlineKeyboardButton(text="Вернуться назад", callback_data=json.dumps({'key': 'back'}))) # Кнопка для возврата назад
        
        start_time = await CreateMeetingService.get_data(user_id, 'start_time')
        start_date = await CreateMeetingService.get_data(user_id, 'date')
        
        conference_start = datetime.strptime(start_date + start_time, '%Y-%m-%d%H:%M')
        
        illegal_intervals = await CreateMeetingService.get_data(user_id, 'illegal_intervals')
        
        end_meeting = max([await MinorOperations.max_duration_for_account(account, conference_start) for account in illegal_intervals.values()]) # Максимально возможная длительность конференции
        
        quantity_buttons = 0  # Счетчик кнопок для формирования строк
        current_slot_start = conference_start  # Начало текущего временного слота

        # Генерация кнопок с длительностями конференции
        while current_slot_start < end_meeting:
            current_slot_end = current_slot_start + timedelta(minutes=30)  # Увеличиваем длительность на 30 минут
            duration = current_slot_end - conference_start  # Вычисляем длительность
            
            if conference_start + duration <= datetime.strptime(start_date + "21:00", '%Y-%m-%d%H:%M'): # Если конец конференции меньше чем 7 часов добавляем кнопку и обновляем счетчик
                buttons.append(InlineKeyboardButton(text=str(duration)[:-3], callback_data=json.dumps({'key': 'duration', 'value':str(duration)[:-3]})))
                quantity_buttons += 1
            
            current_slot_start = current_slot_end  # Переходим к следующему слоту
            
            if quantity_buttons == 2: # Если добавлено 2 кнопки, формируем строку и сбрасываем счетчик
                builder.row(*buttons)
                buttons = []
                quantity_buttons = 0

        # Добавляем оставшиеся кнопки, если их было нечетное количество
        if buttons:
            builder.row(*buttons)

        return builder

