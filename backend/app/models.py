from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Union, Optional, TypeVar, Type, List
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from backend.app.settings import logger
from sqlalchemy.orm import Session


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
    pydantic_dict = pydantic_model.dict(exclude={"id"})  # исключаем поле 'id'

    # Передаем этот словарь в конструктор SQLAlchemy модели
    return sqlalchemy_model(**pydantic_dict)


######### Модели BaseModel ###############
class User(BaseModel):
    username : str
    email : EmailStr
    password: str
    about: str = ""

    def to_public_data(self) -> 'PublicUserData':
        """
        Преобразует модель User в Pydantic модель PublicUserData.
        """
        return PublicUserData(
            username=self.username,
            email=self.email,
            about=self.about
        )


class PublicUserData(BaseModel):
    username: str
    email: str
    about: str = ""


class LoginUser(BaseModel):
    username : str
    password: str


class Message(BaseModel):
    id: Optional[int] = None
    content: str
    timestamp: Optional[datetime] = None
    username: int
    chat_id: int

    class Config:
        from_attributes = True


class ChatCreateRequest(BaseModel):
    chat_title: str
    users: list[str]


class ChatCreated(BaseModel):
    id: Optional[int] = None
    title: str
    chat_owner: PublicUserData
    users: List[PublicUserData] = []

class Chat(BaseModel):
    id: Optional[int] = None
    title: str
    chat_owner: str
    owner: PublicUserData  # Владелец чата
    users: Optional[list[PublicUserData]] = None  # Список пользователей
    messages: list[Message] = []  # Список сообщений

    class Config:
        from_attributes = True


##########Модели PostgreSQL###################


class UserBase(Base):
    __tablename__ = 'users'

    username = Column(String, primary_key=True)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)
    about = Column(String, default="")

    # Отношения
    chats = relationship('ChatBase', secondary='chat_users', back_populates='users')
    messages = relationship('MessageBase', back_populates='author')

    def to_pydantic(self) -> 'PublicUserData':
        """
        Преобразует SQLAlchemy модель UserBase в Pydantic модель PublicUserData.
        """
        return PublicUserData(
            username=self.username,
            email=self.email,
            about=self.about
        )


class ChatBase(Base):
    __tablename__ = 'chats'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)

    owner_username = Column(String, ForeignKey('users.username'), nullable=False)
    owner = relationship('UserBase', backref='owned_chats', lazy=True)

    users = relationship('UserBase', secondary='chat_users', back_populates='chats')
    messages = relationship('MessageBase', back_populates='chat')

    def __init__(self, title: str, owner: UserBase, users: list[UserBase] = None, messages: list[str] = None):
        """
        Инициализация объекта ChatBase.

        :param title: Название чата
        :param owner: Владелец чата (объект UserBase)
        :param users: Список пользователей чата (объекты UserBase)
        :param messages: Список сообщений в чате (объекты MessageBase)
        """
        self.title = title
        self.owner = owner
        self.owner_username = owner.username  # Устанавливаем owner_username

        # Инициализация списка пользователей
        self.users = users if users is not None else []
        if owner not in self.users:
            self.users.append(owner)  # Добавляем владельца в список пользователей, если его там нет

        # Инициализация списка сообщений
        self.messages = messages if messages is not None else []

    @classmethod
    def from_pydantic(cls, chat_created: ChatCreated, db: Session) -> 'ChatBase':
        """
        Преобразует Pydantic модель ChatCreated в SQLAlchemy модель ChatBase.
        """
        try:
            # Получаем владельца чата из базы данных
            owner = db.query(UserBase).filter(UserBase.username == chat_created.chat_owner.username).first()
            if not owner:
                raise ValueError(f"Владелец чата {chat_created.chat_owner.username} не найден")

            # Получаем список пользователей из базы данных
            users = []
            for user_data in chat_created.users:
                user = db.query(UserBase).filter(UserBase.username == user_data.username).first()
                if not user:
                    raise ValueError(f"Пользователь {user_data.username} не найден")
                users.append(user)

            # Создаем объект ChatBase
            return cls(
                title=chat_created.title,
                owner=owner,
                users=users
            )
        except Exception as ex:
            logger.error(f"Convert from pydantic error: {ex}")
            raise ex

    def to_pydantic(self) -> 'Chat':
        """
        Преобразует SQLAlchemy модель ChatBase в Pydantic модель Chat.
        """
        # Преобразуем владельца чата в Pydantic модель
        owner_pydantic = PublicUserData(
            username=self.owner.username,
            email=self.owner.email,
            about=self.owner.about
        )

        # Преобразуем список пользователей в Pydantic модель
        users_pydantic = [
            PublicUserData(
                username=user.username,
                email=user.email,
                about=user.about
            )
            for user in self.users
        ]

        # Преобразуем список сообщений в Pydantic модель
        messages_pydantic = [
            Message(
                id=message.id,
                content=message.content,
                timestamp=message.timestamp,
                username=message.username,
                chat_id=message.chat_id
            )
            for message in self.messages
        ]

        # Создаем объект Pydantic модели Chat
        return Chat(
            id=self.id,
            title=self.title,
            chat_owner=owner_pydantic.username,
            owner=owner_pydantic,
            users=users_pydantic,
            messages=messages_pydantic
        )


    def __str__(self):
        return f"Title: {self.title}\nOwner: {self.owner}\nowner_username: {self.owner_username}\nusers:{self.users}"


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