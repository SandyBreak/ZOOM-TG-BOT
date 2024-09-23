# -*- coding: UTF-8 -*-

from dataclasses import dataclass


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