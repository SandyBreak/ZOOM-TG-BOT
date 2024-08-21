# -*- coding: UTF-8 -*-

from aiogram.types import FSInputFile
from typing import Optional, Tuple
from aiogram import Bot

import logging
import json
import os


from dotenv import set_key


class AdminOperations:
    def __init__(self) -> None:
        self.auth_client = None
    
    
    async def get_manager_password(self) -> str:
        """
        Получение пароля админа бота
        """
        return os.environ.get('MANAGER_PASSWORD_HASH')
    
    
    def get_attempts_enter_wrong_password(self) -> str:
        """
        Получение количества оставшихся попыток ввода пароля
        """
        return os.environ.get('MAX_ATTEMPTS')
    
    
    async def update_attempts_enter_wrong_password(self, remaining_attempts: dict) -> str:
        """
        Обновление количества оставшихся попыток ввода пароля
        """
        set_key('docker-compose.env', 'MAX_ATTEMPTS', str(remaining_attempts))
        return os.environ.get('MAX_ATTEMPTS')
    
    
    async def update_list_admin_users(self, list_users: dict) -> str:
        """
        Обновление количества оставшихся попыток ввода пароля
        """
        try:
            list_users = json.dumps(list_users)
            set_key('docker-compose.env', 'ADMIN_USERS', str(list_users))
        except Exception as e:
            logging.error(f"Error during update_list_admin_users: {e}")
    
    
    async def update_list_banned_users(self, list_users: dict) -> str:
        """
        Обновление количества оставшихся попыток ввода пароля
        """
        try:
            list_users = json.dumps(list_users)
            set_key('docker-compose.env', 'BANNED_USERS', str(list_users))
        except Exception as e:
            logging.error(f"Error during update_list_banned_users: {e}")
                

    async def parse_callback_data(self, data: str) -> Tuple[str, Optional[str], Optional[str]]:
        """
        Получение данных из строки callback.data
        """
        if ',' in data:
            parts = data.split(',')
            action = parts[0]
            user_id = parts[1] if len(parts) > 1 else None
            user_tg_addr = ','.join(parts[2:]) if len(parts) > 2 else None
            return action, user_id, user_tg_addr
        else:
            return data, None, None