from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Union, Optional
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

#########Модели BaseModel###############
class User(BaseModel):
    username : str
    email : EmailStr
    password: str
    about: str = ""


class PublicUserData(User):
    password: str = None 

    class Config:
        fields = {'password': {'exclude': True}}


class LoginUser(BaseModel):
    username : str
    password: str


class ChatContent(BaseModel):
    sender : PublicUserData
    datetime : datetime


class Message(ChatContent):
    text_message : str


class Chat(BaseModel):
    chat_name : str
    owner : PublicUserData
    users : list[PublicUserData]
    content : list[Union[Message]]


##########Модели PostgreSQL###################


Base = declarative_base()


class UserBase(Base):
    __tablename__ = 'users'
    
    username = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    about = Column(Text, default=None)
    
    # Связь с таблицей Post (один ко многим)
    #posts = relationship("Post", back_populates="author")

    def __init__(self, username, email, password, about=None):
        self.username = username
        self.email = email
        self.password = password
        self.about = about

    def dict(self):
        return {
            "username": self.username,
            "email": self.email,
            "password": self.password,
            "about": self.about
        }
