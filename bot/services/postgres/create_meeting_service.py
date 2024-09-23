# -*- coding: UTF-8 -*-

from datetime import datetime
from typing import Union
import logging

from sqlalchemy import select, func, update, delete, insert
from sqlalchemy.exc import SQLAlchemyError

from models.table_models.temporary_conference_data import TemporaryConferenceData
from models.table_models.created_conferences import CreatedConferences
from models.table_models.user import User

from models.dataclasses import MeetingData


from services.postgres.database import get_async_session


class CreateMeetingService:
    def __init__(self):
        pass
    
    
    @staticmethod
    async def init_new_meeting(user_id: int) -> None:
        """
        Создание новой записи с данными о создаваемой конференции
        """
        async for session in get_async_session():
            try:
                new_meeting = TemporaryConferenceData(
                    id_tg=user_id
                )
                session.add(new_meeting)
                await session.commit()
            except SQLAlchemyError as e:
                logging.error(f"Ошибка инициализации новой конференции пользователя с id_tg {user_id}: {e}")


    @staticmethod
    async def save_created_conference(user_id: int, meeting_data: MeetingData, choosen_zoom: str) -> None:
        """
        Добавдение записи о созданной конфереции 
        """
        auto_recording = meeting_data.auto_recording == 'cloud'
        
        async for session in get_async_session():
            try:
                get_user_id = await session.execute(
                    select(User.id)
                    .where(User.id_tg == user_id)
                )
                creator_id = get_user_id.scalar()
                await session.execute(
                    insert(CreatedConferences)
                    .values(
                        creator_id=creator_id,
                        date_creation=datetime.now(),
                        name=meeting_data.topic,
                        account=choosen_zoom,
                        start_time=meeting_data.start_time,
                        duration=f'{meeting_data.duration} минут',
                        autorecord=auto_recording
                    )
                )
                await session.commit()
            except SQLAlchemyError as e:
                logging.error(f"Ошибка сохранения созданной конференции пользователя с id_tg {user_id}: {e}")
    
    
    @staticmethod
    async def delete_temporary_data(user_id: int) -> None:
        async for session in get_async_session():
            try:
                await session.execute(
                    delete(TemporaryConferenceData)
                    .where(TemporaryConferenceData.id_tg == user_id)
                )
                
                await session.commit()
            except SQLAlchemyError as e:
                logging.error(f"Ошибка удаления данных о создаваемой конференции пользователя с id_tg {user_id}: {e}")
            
            
    @staticmethod
    async def get_data(user_id: int, type_data: str) -> Union[int, str, dict]:
        """
        Получение данных о создаваемой конференции
        """
        async for session in get_async_session():
            try:
                get_temporary_data = await session.execute(
                    select(TemporaryConferenceData)
                    .where(TemporaryConferenceData.id_tg == user_id)
                )
                temporary_data = get_temporary_data.scalars().all()
                if type_data == 'all':
                    return temporary_data[0]

                data_mapping = {
                    'date': temporary_data[0].date,
                    'illegal_intervals': temporary_data[0].illegal_intervals,
                    'start_time': temporary_data[0].start_time,
                    'duration_meeting': temporary_data[0].duration_meeting,
                    'autorecord_flag': temporary_data[0].autorecord_flag,
                    'choosen_zoom': temporary_data[0].choosen_zoom,
                }
                
                return data_mapping.get(type_data)
            except SQLAlchemyError as e:
                logging.error(f"Ошибка получения '{type_data}': {e}")
    
    
    @staticmethod
    async def save_data(user_id: int, type_data: str, insert_value: Union[str, dict, list]) -> None:
        """
        Сохранение данных о создаваемой конференции
        """
        async for session in get_async_session():
            try:
                values_to_update = {}

                match type_data:
                    case 'duration_and_zoom_account':
                        values_to_update = {
                            'duration_meeting': insert_value[0],
                            'choosen_zoom': insert_value[1]
                        }
                    case _:
                        values_to_update[type_data] = insert_value

                await session.execute(
                    update(TemporaryConferenceData)
                    .where(TemporaryConferenceData.id_tg == user_id)
                    .values(**values_to_update)
                )
                await session.commit()
            except SQLAlchemyError as e:
                logging.error(f"Ошибка сохранения '{type_data}': {e}")
