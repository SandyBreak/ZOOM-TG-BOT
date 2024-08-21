# -*- coding: UTF-8 -*-

from aiogram.fsm.state import State, StatesGroup


class CreateMeetingStates(StatesGroup):
    """
    Состояния для создания новой конференции
    """
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
