# -*- coding: UTF-8 -*-

from sqlalchemy import Column, String, Integer, Float, Boolean, ARRAY, TIMESTAMP, BigInteger, JSON

from .base import Base


class TemporaryConferenceData(Base):
    __tablename__ = 'temporary_conference_data'
    
    id = Column(Integer, primary_key=True)
    
    id_tg = Column(BigInteger, nullable=False)

    date = Column(String(length=320), nullable=True)
    choosen_zoom = Column(Integer, nullable=True)
    start_time = Column(String(length=320), nullable=True)
    duration_meeting = Column(Float, nullable=True)
    autorecord_flag = Column(String(length=320), nullable=True)
    illegal_intervals = Column(JSON, default=[])