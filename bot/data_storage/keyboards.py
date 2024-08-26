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
        Клавиатура с генерации календаря
        """ 
        builder = ReplyKeyboardBuilder()
        buttons = []
        builder.row(KeyboardButton(text="Вернуться назад"))

        now = datetime.now()

        current_month = now.month

        builder.row(KeyboardButton(text=datetime.now().strftime('%B')))# Кнопка с текущим месяцем

        for i in range(0, 5*7*3+int(now.isoweekday())):
            day = now + timedelta(days=i)# Вычисляем дату
            buttons.append(KeyboardButton(text=day.strftime('%d.%m')))# Добавляем кнопку с датой
            
            # Если день - воскресенье, добавляем строку кнопок
            if day.strftime('%A') == 'Sunday':

                if len(buttons) != 7 and len(buttons) != 0:
                    # Заполняем пустые кнопки до 7
                    for a in range(0, 7 - len(buttons)):
                        buttons.insert(0, KeyboardButton(text=f'----'))

                builder.row(*buttons)  # Добавляем строку в клавиатуру
                buttons = []  # Очищаем список кнопок

            # Проверка на смену месяца
            if day.month != current_month:
                if buttons:  # Если есть кнопки, удаляем последнюю
                    buttons.pop()

                if len(buttons) != 7 and len(buttons) != 0:
                    # Заполняем пустые кнопки до 7
                    for a in range(0, 7 - len(buttons)):
                        buttons.append(KeyboardButton(text=f"----"))

                builder.row(*buttons)# Добавляем строку в клавиатуру 
                builder.row(KeyboardButton(text=day.strftime('%B')))# Кнопка с новым месяцем
                buttons = []# Очищаем список кнопок
                buttons.append(KeyboardButton(text=day.strftime('%d.%m')))  # Добавляем кнопку с первой датой нового месяца
                current_month = day.month  # Обновляем текущий месяц

        # Завершение добавления кнопок
        if len(buttons) != 7 and len(buttons) != 0:
            for a in range(0, 7 - len(buttons)):
                buttons.append(KeyboardButton(text="----"))  # Заполняем пустые кнопки до 7

        builder.row(*buttons)  # Добавляем последнюю строку кнопок

        return builder  # Возвращаем построенную клавиатуру



    async def start_time_keyboard(self, user_id: int, illegal_intervals: dict) -> ReplyKeyboardBuilder:
        """
        Клавиатура с доступными временными интервалами для начала конференции.
        """
        builder = ReplyKeyboardBuilder()
        buttons = []
        builder.row(KeyboardButton(text="Вернуться назад")) # Кнопка для возврата назад

        # Получаем введенную дату из базы данных
        entered_date = await mongodb_interface.get_data(user_id, 'date')
        available_time_slots = [] # Список доступных временных интервалов
        response_logs = []  # Логи ответов для проверки интервалов
        
        if illegal_intervals:   # Если есть недопустимые интервалы
            for account_intervals in illegal_intervals: # Делаем проверку для каждого аккаунтав которомуже есть недопустимые интервалы для создания конференций
                time_slots = []
                start_time = datetime.strptime(entered_date + "09:00", '%Y-%m-%d%H:%M')  # Начало рабочего дня
                end_time = datetime.strptime(entered_date + "19:00", '%Y-%m-%d%H:%M')  # Конец рабочего дня
        
                current_slot_start = start_time # Текущий временной интервал

                # Генерация временных слотов по 30 минут
                while current_slot_start < end_time:
                    current_slot_end = current_slot_start + timedelta(minutes=30)
                    time_slots.append(current_slot_start)  # Добавляем слот
                    current_slot_start = current_slot_end  # Переходим к следующему слоту

                # Проверка временных слотов на пересечение с недопустимыми интервалами
                for slot in time_slots:
                    for start, end in account_intervals:
                        if not(start <= slot < end) and (slot > datetime.now()):
                            response_logs.append('True')
                        else:
                            response_logs.append('False')
                    if 'False' in response_logs:  # Если есть пересечение, очищаем логи
                        response_logs = []
                    else: # Если пересечений нету
                        available_time_slots.append(slot)  # Добавляем доступный слот
                        response_logs = []  # Очищаем логи для проверки следующего слота
        else:
            # Если нет недопустимых интервалов, добавляем сразу все слоты
            for slot in time_slots:
                if (slot > datetime.now()):
                  available_time_slots.append(slot)
        
        # Удаляем дубликаты и сортируем доступные временные слоты
        sorted_available_time_slots = list(set(available_time_slots))
        sorted_available_time_slots = sorted(sorted_available_time_slots, key=lambda x: x)
        
        # Формируем кнопки для клавиатуры
        for ctr in range(0, len(sorted_available_time_slots)-1, 2):
            buttons.append(KeyboardButton(text=sorted_available_time_slots[ctr].strftime('%H:%M')))  # Кнопка с временем 1
            buttons.append(KeyboardButton(text=sorted_available_time_slots[ctr + 1].strftime('%H:%M')))  # Кнопка с временем 2
            builder.row(*buttons)  # Добавляем строку кнопок в клавиатуру
            buttons = []  # Очищаем список кнопок

        return builder  # Возвращаем построенную клавиатуру


    async def duration_keyboard(self, user_id: int) -> ReplyKeyboardBuilder:
        """
        Клавиатура генерации доступной длительности конференции
        """
        builder = ReplyKeyboardBuilder()  # Инициализация строителя клавиатуры
        buttons = []  # Список для кнопок
        builder.row(KeyboardButton(text="Вернуться назад"))  # Кнопка для возврата назад
        
        # Получение данных о времени начала, дате и недопустимых интервалах из базы данных
        start_time = await mongodb_interface.get_data(user_id, 'start_time')
        entered_date = await mongodb_interface.get_data(user_id, 'date')
        illegal_intervals = await mongodb_interface.get_data(user_id, 'illegal_intervals')
        
        # Преобразование строкового представления времени в объект datetime
        start_time = datetime.strptime(entered_date + start_time, '%Y-%m-%d%H:%M')
        end_meeting = datetime.strptime(entered_date + "19:00", '%Y-%m-%d%H:%M')  # Конец рабочего дня
        
        
        # Определение времени окончания встречи с учетом недопустимых интервалов
        for account_intervals in illegal_intervals:
            for start, end in account_intervals:
                if start > start_time:  # Если начало недопустимого интервала позже времени начала
                    end_meeting = start  # Устанавливаем новое время окончания встречи
                    break
    
        current_slot_start = start_time  # Начало текущего временного слота
        quantity_buttons = 0  # Счетчик кнопок для формирования строк

        # Генерация кнопок с длительностями конференции
        while current_slot_start < end_meeting:
            current_slot_end = current_slot_start + timedelta(minutes=30)  # Увеличиваем слот на 30 минут
            duration = current_slot_end - start_time  # Вычисляем длительность

            buttons.append(KeyboardButton(text=str(duration)[:-3]))  # Добавляем кнопку с длительностью

            quantity_buttons += 1  # Увеличиваем счетчик кнопок
            current_slot_start = current_slot_end  # Переходим к следующему слоту
            
            # Если добавлено 2 кнопки, формируем строку и сбрасываем счетчик
            if quantity_buttons == 2:
                builder.row(*buttons)  # Добавляем строку кнопок в клавиатуру
                buttons = []  # Очищаем список кнопок
                quantity_buttons = 0  # Сбрасываем счетчик

        # Добавляем оставшиеся кнопки, если они есть
        if buttons:
            builder.row(*buttons)

        return builder  # Возвращаем построенную клавиатуру
