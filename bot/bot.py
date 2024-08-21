#!/usr/bin/env python

# -*- coding: UTF-8 -*-

from aiogram.types.bot_command import BotCommand
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

import asyncio
import logging

from admin import admin_panel

from helper_classes.assistant import MinorOperations
from database.mongodb.mongo_init import create_db
from routers import commands, create_new_meeting


helper = MinorOperations()


async def set_commands_and_description(bot: Bot) -> None:
    commands = [
    BotCommand(
        command="/help",
        description="Помощь"
		),
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
		)
    ]
    long_description_one = f""""""
    short_description = f""
    
    await bot.set_my_description(description=long_description_one)
    await bot.set_my_short_description(short_description=short_description)
    await bot.set_my_commands(commands)
    
    
async def main():
    load_dotenv()#Потом убрать надо
    
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%m %H:%M')
    
    bot = Bot(token=await helper.get_tg_token())
    dp = Dispatcher()
    
    await set_commands_and_description(bot)
    dp.include_router(commands.router)
    dp.include_router(create_new_meeting.router)
    dp.include_router(admin_panel.router)

    await create_db()
    logging.warning("BOT STARTED")
    await dp.start_polling(bot)
    

if __name__ == "__main__":
    asyncio.run(main())
    