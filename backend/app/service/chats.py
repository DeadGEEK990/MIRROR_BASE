from ..models import Message, MessageBase, Chat, ChatBase
from ..data import chats_postgre as data
from ..errors import Missing, Duplicate
from sqlalchemy.orm import Session
from typing import List, Dict, Any


def get_one(db: Session, chat_id: int) -> Message:
    return data.get_one(db, chat_id)


def get_all(db: Session) -> list[Chat]:
    return data.get_all(db)


def create(db: Session, chat: Chat) -> Message:
    return data.create(db, chat)


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


