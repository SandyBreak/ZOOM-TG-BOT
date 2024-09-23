# -*- coding: UTF-8 -*-

from sqlalchemy import Column, Integer, ForeignKey, String, Boolean, TIMESTAMP
from sqlalchemy.orm import relationship
from .base import Base

class CreatedConferences(Base):
    __tablename__ = 'created_conferences'
    
    id = Column(Integer, primary_key=True, nullable=False)
    creator_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="created_conferences")

    date_creation = Column(TIMESTAMP, nullable=False) 
    name = Column(String(length=320), nullable=False)
    account = Column(String(length=320), nullable=False)
    start_time = Column(TIMESTAMP, nullable=False)
    duration = Column(String(length=320), nullable=False)
    autorecord = Column(Boolean, nullable=False)
