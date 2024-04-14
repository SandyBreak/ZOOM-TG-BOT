# -*- coding: UTF-8 -*-

from aiogram.dispatcher.filters.state import State, StatesGroup
from dataclasses import dataclass

class CreateMeetingStates(StatesGroup):
    """
    Состояния для создания новой конференции
    """
    get_zoom = State()
    get_date = State()
    get_start_time = State()
    get_duration = State()
    get_auto_recording = State()
    get_name_create_meeting = State()
    
class GetPlannedMeetingStates(StatesGroup):
    """
    Состояния для просмотра запланированных конференций
    """
    get_zoom = State()
    get_date_and_get_planned_meetings = State()

@dataclass
class ZoomAccount:
    """
    ID и токены аккаунтов
    """
    name: str
    account_id: str
    client_id: str
    client_secret: str

@dataclass
class MeetingData:
    """
    Данные о создаваемой конференции
    """
    topic: str
    type: int
    start_time: str
    duration: int
    password: str | None
    timezone: str
    password_required: bool
    auto_recording: str