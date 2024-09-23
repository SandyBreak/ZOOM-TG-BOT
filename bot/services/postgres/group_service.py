# -*- coding: UTF-8 -*-

import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select, update, insert

from services.postgres.database import get_async_session

from models.table_models.user import User
from models.table_models.admin_group import AdminGroup
from models.table_models.user_chat import UserChat


class GroupService:
    def __init__(self):
        pass

    @staticmethod
    async def group_init(id_group: int,  session: AsyncSession = get_async_session()) -> str:
        """
        Идентификация в группе
        """
        try:
            async for session in get_async_session():
                session.add(AdminGroup(group_id=id_group))
                
                await session.commit()
                
                await session.close()
        except Exception as e:  # Ловим все исключения
            logging.error(f"Ошибка при идентификации группы: {e}")
    
    
    @staticmethod
    async def group_reset(session: AsyncSession = get_async_session()) -> str:
        """
        Сброс группы
        """
        try:
            async for session in get_async_session():
                await session.execute(delete(AdminGroup))
                
                await session.commit()  # Подтверждаем изменения
        except Exception as e:
            await session.rollback()  # Откатываем изменения в случае ошибки
            logging.error(f"Ошибка при сбросе группы: {e}")
    
    
    @staticmethod
    async def get_group_id(session: AsyncSession = get_async_session()) -> str:
        """
        Получение ID группы
        """
        try:
            async for session in get_async_session():
                get_group_id = await session.execute(select(AdminGroup.group_id))
                id_group = get_group_id.scalar()
                if id_group:
                    await session.close()
                    return id_group
                else:
                    return None
        except Exception as e:
            logging.error(f"Ошибка при получении ID группы: {e}")
            
            
    @staticmethod
    async def get_user_message_thread_id(user_tg_id: int, session: AsyncSession = get_async_session()) -> bool:
        """
        Получает id чата с пользователем для группы.
        """
        try:
            async for session in get_async_session():
                subquery = select(User.id).where(User.id_tg == user_tg_id).scalar_subquery()
                get_user_message_thread_id = await session.execute(select(UserChat.id_topic_chat)
                    .select_from(UserChat)
                    .where(UserChat.user_id == subquery)
                )
                message_thread_id = get_user_message_thread_id.scalar()
                await session.close()
                return message_thread_id
        except Exception as e:
            logging.error(f"Ошибка при получении id чата пользователя в группе: {e}")
    
    
    @staticmethod
    async def update_user_message_thread_id(user_tg_id: int, message_thread_id: int, session: AsyncSession = get_async_session()) -> bool:
        """
        Получает id чата с пользователем для группы.
        """
        try:
            async for session in get_async_session():
                subquery = select(User.id).where(User.id_tg == user_tg_id).scalar_subquery()
                await session.execute(
                        update(UserChat)
                        .where(UserChat.user_id == subquery)
                        .values(id_topic_chat=message_thread_id)
                        )
                await session.commit()
                await session.close()
        except Exception as e:
            logging.error(f"Ошибка при обновлении id чата пользователя в группе: {e}")

    
    @staticmethod
    async def save_user_message_thread_id(user_tg_id: int, message_thread_id: int, session: AsyncSession = get_async_session()) -> bool:
        """
        Получает id чата с пользователем для группы.
        """
        try:
            async for session in get_async_session():
                subquery = select(User.id).where(User.id_tg == user_tg_id).scalar_subquery()
                await session.execute(
                        insert(UserChat)
                        .values(user_id=subquery, id_topic_chat=message_thread_id)
                        )
                await session.commit()
                await session.close()
        except Exception as e:
            logging.error(f"Ошибка при получении id чата пользователя в группе: {e}")