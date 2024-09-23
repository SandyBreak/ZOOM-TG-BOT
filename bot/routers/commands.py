# -*- coding: UTF-8 -*-

from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram import Router, Bot

from models.long_messages import HELP_MESSAGE, MENU_MESSAGE

router = Router()

@router.message(Command('cancel'))
async def bot_menu_and_start_message(message: Message, state: FSMContext, bot: Bot) -> None:
    await bot.delete_message(chat_id=message.chat.id, message_id=(await state.get_data()).get('message_id'))
    
    await message.answer(MENU_MESSAGE, reply_markup=ReplyKeyboardRemove())
    await state.clear()

    
@router.message(Command('help'))
async def bot_help(message: Message, state: FSMContext, bot: Bot) -> None:
    await bot.delete_message(chat_id=message.chat.id, message_id=(await state.get_data()).get('message_id'))
    
    await  message.answer(HELP_MESSAGE, reply_markup=ReplyKeyboardRemove())
    await state.clear()