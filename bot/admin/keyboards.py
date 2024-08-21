# -*- coding: UTF-8 -*-
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

from database.mongodb.interaction import Interaction

mongodb_interface = Interaction()

from data_storage.emojis_chats import Emojis

emojis = Emojis()

class AdminKeyboards:
    def __init__(self) -> None:
        pass

    
    async def ban_or_access_keyboard(self, user_id: int) -> InlineKeyboardBuilder:
        """
        Бан или добавление пользователя в админы
        """
        builder = InlineKeyboardBuilder(
            markup=[
                [
                    InlineKeyboardButton(text="Забанить", callback_data=f'BAN,{user_id}')
                ],
                [
                    InlineKeyboardButton(text="Добавить в админы", callback_data=f'ACCESS,{user_id}')
                ]
            ]
        )
        return builder
    
    
    async def keyboard_for_adding_users_in_targeted_newsletter(self, added_users: dict) -> InlineKeyboardBuilder:
        '''
        Клавиатура с выбором пользователей для точечной рассылки
        '''
        builder = InlineKeyboardBuilder()
        users = await mongodb_interface.get_users_id_and_tg_adreses()
        if added_users:
            for user in users:
                user_id = user[0]
                user_tg_addr = user[1]
                for added_user in added_users:
                    added_user_id = added_user[0]
                    added_user_tg_addr = added_user[1]
                    if user_id == added_user_id and user_tg_addr == added_user_tg_addr:        
                        builder.row(InlineKeyboardButton(text=f'{emojis.SUCCESS} {added_user_id} {added_user_tg_addr}', callback_data=f'ADD,{added_user_id},{added_user_tg_addr}'))
                        break
                else:
                    builder.row(InlineKeyboardButton(text=f'{emojis.FAIL} {user_id} {user_tg_addr}', callback_data=f'ADD,{user_id},{user_tg_addr}'))
            
        else:        
            for user in users:
                user_id = user[0]
                user_tg_addr = user[1]
                builder.row(InlineKeyboardButton(text=f'{emojis.FAIL} {user_id} {user_tg_addr}', callback_data=f'ADD,{user_id},{user_tg_addr}'))

        builder.row(InlineKeyboardButton(text=f'Отправить выбраным пользователям', callback_data=f'accept_newsletter'))
        
        return builder
    
    
    async def possibilities_keyboard(self) -> InlineKeyboardBuilder:
        """
        Основная клавиатура админа
        """
        builder = InlineKeyboardBuilder(
            markup=[
                [
                    InlineKeyboardButton(text="РУКОВОДСТВО АДМИН ПАНЕЛИ", callback_data=f'manual')
                ],
                [
                    InlineKeyboardButton(text="Запустить рассылку", callback_data=f'newsletter')
                ],
                [
                    InlineKeyboardButton(text="Посмотреть список активных/не активных пользователей", callback_data=f'view_active_users')
                ],
                [
                    InlineKeyboardButton(text="Заново отправить сообщение с действиями", callback_data='menu')
                ]
            ]
        )
        return builder
    
    
    async def newsletter_keyboard(self) -> InlineKeyboardBuilder:
        '''
        Клавиатура для рассылки
        '''
        builder = InlineKeyboardBuilder(
            markup=[
                [
                    InlineKeyboardButton(text='Запустить глобальную рассылку', callback_data=f'global')
                ],
                [
                    InlineKeyboardButton(text='Запустить точечную рассылку', callback_data=f'targeted')
                ],
                [
                    InlineKeyboardButton(text='Удалить это сообщение', callback_data=f'cancel_newsletter')
                ]
            ]
        )
        return builder