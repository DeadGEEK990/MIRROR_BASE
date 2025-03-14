from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Union, Optional, TypeVar, Type
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

######### Вспомогательные функции ###########
Base = declarative_base()

# Создаём универсальный тип для функции
T = TypeVar('T', bound=Base)
P = TypeVar('P', bound=BaseModel)  # Pydantic модели

def sqlalchemy_to_pydantic(db_instance: T, pydantic_model: Type[BaseModel]) -> BaseModel:
    """
    Преобразует SQLAlchemy объект в Pydantic модель.

    :param db_instance: Экземпляр SQLAlchemy модели
    :param pydantic_model: Pydantic модель для сериализации
    :return: Экземпляр Pydantic модели с данными из SQLAlchemy
    """
    # Преобразуем SQLAlchemy объект в словарь
    return pydantic_model(
        **{column.name: getattr(db_instance, column.name) for column in db_instance.__table__.columns})


def pydantic_to_sqlalchemy(pydantic_model: P, sqlalchemy_model: Type[T]) -> T:
    """
    Преобразует Pydantic модель в SQLAlchemy модель.

    :param pydantic_model: Экземпляр Pydantic модели
    :param sqlalchemy_model: SQLAlchemy модель
    :return: Экземпляр SQLAlchemy модели
    """
    # Получаем данные из Pydantic модели в виде словаря
    pydantic_dict = pydantic_model.dict()

    # Передаем этот словарь в конструктор SQLAlchemy модели
    return sqlalchemy_model(**pydantic_dict)


######### Модели BaseModel ###############
class User(BaseModel):
    username : str
    email : EmailStr
    password: str
    about: str = ""


class PublicUserData(User):
    password: str = None


class LoginUser(BaseModel):
    username : str
    password: str


class Message(BaseModel):
    id: int
    content: str
    timestamp: datetime
    username: int
    chat_id: int
    author: Optional[str] = None
    chat: Optional[int] = None

    class Config:
        from_attributes = True


class Chat(BaseModel):
    id : int
    title: str
    users : list[User]
    messages: list[Message]


##########Модели PostgreSQL###################


class UserBase(Base):
    __tablename__ = 'users'
    
    username = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    about = Column(Text, default=None)

    chats = relationship('ChatBase', secondary='chat_users', back_populates='users')
    messages = relationship('MessageBase', back_populates='author')

    def __init__(self, username, email, password, about=None):
        self.username = username
        self.email = email
        self.password = password
        self.about = about


class ChatBase(Base):
    #user1 = User(name="Alice")
    #session.add(user1)
    #session.commit()
    #chat1 = Chat(title="General Chat")
    #session.add(chat1)
    #session.commit()
    # Добавление пользователей в чаты
    #chat1.users = [user1, user2]
    __tablename__ = 'chats'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)

    users = relationship('UserBase', secondary='chat_users', back_populates='chats')
    messages = relationship('MessageBase', back_populates='chat')


class MessageBase(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(Text, nullable=False)  # Текст сообщения
    timestamp = Column(DateTime, default=datetime.utcnow)  # Время отправки
    username = Column(String, ForeignKey('users.username', ondelete='CASCADE'))  # Пользователь, отправивший сообщение
    chat_id = Column(Integer, ForeignKey('chats.id', ondelete='CASCADE'))  # Чат, в который отправлено сообщение

    # Связи с пользователем и чатом
    author = relationship('UserBase', back_populates='messages')
    chat = relationship('ChatBase', back_populates='messages')


##############Промежуточные таблицы############################

class ChatUser(Base):
    __tablename__ = 'chat_users'

    chat_id = Column(Integer, ForeignKey('chats.id', ondelete='CASCADE'), primary_key=True)
    username = Column(String, ForeignKey('users.username', ondelete='CASCADE'), primary_key=True)