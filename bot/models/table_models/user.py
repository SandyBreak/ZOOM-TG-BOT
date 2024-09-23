# -*- coding: UTF-8 -*-

from sqlalchemy import Column, Integer, BigInteger, String, DateTime
from sqlalchemy.orm import relationship

from .user_chat import UserChat
from .created_conferences import CreatedConferences

from .base import Base


class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, nullable=False)
    id_tg = Column(BigInteger, nullable=False)
    nickname = Column(String(length=320), nullable=False)
    fullname = Column(String(length=320), nullable=False)
    fio = Column(String(length=320), nullable=False)
    date_reg = Column(DateTime, nullable=False)
    number_created_conferences = Column(Integer, nullable=True)

    user_chats = relationship("UserChat", back_populates="user")
    created_conferences = relationship("CreatedConferences", back_populates="user")
