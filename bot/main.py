#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import asyncio
import logging

from aiogram.types.bot_command import BotCommand
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from routers import commands, create_new_meeting, registration, actions
from admin import admin_panel
from config import TELEGRAM_TOKEN


async def set_commands_and_description(bot: Bot) -> None:
    commands = [
    BotCommand(
        command="/create",
		description="Создать новую конференцию"
		),
    BotCommand(
        command="/reset",
        description="Начать заполнение данных о создаваемой конференции заново"
		),
    BotCommand(
        command="/cancel",
		description="Отменить создание конференции"
		),
    BotCommand(
        command="/help",
        description="Помощь"
		)
    ]
    long_description_one = f""
    short_description = f""
    
    await bot.set_my_description(description=long_description_one)
    await bot.set_my_short_description(short_description=short_description)
    await bot.set_my_commands(commands)
  
    
async def main():
    load_dotenv()
    
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%m %H:%M')
    
    bot = Bot(token=TELEGRAM_TOKEN)
    dp = Dispatcher()
    
    await set_commands_and_description(bot)
    
    dp.include_router(commands.router)
    dp.include_router(create_new_meeting.router)
    dp.include_router(admin_panel.router)
    dp.include_router(registration.router)
    dp.include_router(actions.router)
    
    logging.warning("BOT STARTED")
    await dp.start_polling(bot)
    
if __name__ == "__main__":
    asyncio.run(main())
    