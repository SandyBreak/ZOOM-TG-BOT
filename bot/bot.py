#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from aiogram import Bot, Dispatcher
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import BotCommand

import logging
import asyncio

from dotenv import load_dotenv
from handlers.commands import register_handlers_commands
from handlers.create_new_meeting import register_handlers_create_meeting
from handlers.get_planned_meetings import register_handlers_get_planned_meetings

from database.create_db import create_db


from helper_classes.assistant import MinorOperations

logger = logging.getLogger(__name__)


async def set_commands(bot: Bot) -> None:
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
			),
      BotCommand(
        command="/meetings",
        description="Получить список запланированных конференций на дату"
      )
    ]

    await bot.set_my_commands(commands)

async def main():
  await create_db()
  helper = MinorOperations()
  bot = Bot(token=await helper.get_token())
  dp = Dispatcher(bot, storage=MemoryStorage())
  dp.middleware.setup(LoggingMiddleware())
  
	#Регистрация команд и обработчиков событий
  await set_commands(bot)
  await register_handlers_commands(dp)
  await register_handlers_create_meeting(dp)
  await register_handlers_get_planned_meetings(dp)
  await dp.skip_updates()
  print('Bot STARTED')
  await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())
