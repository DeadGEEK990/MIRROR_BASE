from ..models import Message, MessageBase, Chat, ChatBase, ChatCreated, PublicUserData, ChatCreateRequest
from ..data import chats_postgre as data
from backend.app.service import users as service_users
from ..errors import Missing, Duplicate
from backend.app.settings import logger
from backend.app.data import users_postgre as data_user
from sqlalchemy.orm import Session
from typing import List, Dict, Any


def get_one(db: Session, chat_id: int) -> Message:
    return data.get_one(db, chat_id)


def get_all(db: Session) -> list[Chat]:
    return data.get_all(db)


def create(db: Session, chat: ChatCreateRequest, token: str) -> Chat:
    try:
        # Получаем текущего пользователя (владельца чата)
        owner = service_users.get_current_user(db=db, token=token)
        if not owner:
            raise ValueError("Владелец чата не найден")

        # Получаем список пользователей
        users = []
        for username in chat.users:
            user = service_users.get_one(db=db, username=username)
            if not user:
                raise ValueError(f"Пользователь {username} не найден")
            users.append(user)

        # Преобразуем SQLAlchemy объекты в Pydantic объекты
        owner_pydantic = owner.to_public_data()
        users_pydantic = [user.to_public_data() for user in users]

        # Создаем объект ChatCreated
        chat_created = ChatCreated(
            title=chat.chat_title,
            chat_owner=owner_pydantic,
            users=users_pydantic
        )

        # Создаем чат в базе данных
        return data.create(db=db, chat=chat_created)
    except Exception as ex:
        logger.error(f"Service cant create chat: {ex}")
        raise ex


def all_chats_by_user(db: Session, username: str) -> list[Chat]:
    return data.get_all_chats_by_user(db=db, username=username)


def delete(db: Session, chat_id: int) -> bool:
    return data.delete(db, chat_id)


def check_user_in_chat(db : Session, chat_id : int, username : str) -> bool:
    return data.check_user_in_chat(db, chat_id, username)


def add_user_to_chat(db: Session, chat_id: int, username: str) -> bool:
    return data.add_user_to_chat(db,chat_id,username)


def remove_user_from_chat(db: Session, chat_id: int, username: str) -> bool:
    return data.remove_user_from_chat(db,chat_id,username)


def add_message_to_chat(db: Session,message_pydantic: Message) -> bool:
    return data.add_message_to_chat(db, message_pydantic)


def delete_message_from_chat(db: Session, message_id: int) -> bool:
    return data.delete_message_from_chat(db, message_id)


