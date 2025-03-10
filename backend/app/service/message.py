from ..models import Message, MessageBase
from ..data import messages_postgre as data
from ..errors import Missing, Duplicate
from sqlalchemy.orm import Session
from typing import List, Dict, Any


def get_one(db: Session, message_id: int) -> Message:
    return data.get_one(db, message_id)


def get_all(db: Session) -> list[Message]:
    return data.get_all(db)


def create(db: Session, message: Message) -> Message:
    return data.create(db, message)


def delete(db: Session, message_id: int) -> bool:
    return data.delete(db, message_id)


def find_messages_by_sender_in_chat(db: Session, sender_name: str, chat_id: int) -> list[Message]:
    filters: List[Dict[str, Any]] = []
    filters.append({'chat_id':chat_id})
    filters.append({'username':sender_name})
    return data.get_messages_by_filter(db=db, filters=filters)


def find_all_messages_by_sender(db: Session, sender_name: str) -> list[Message]:
    filters: List[Dict[str, Any]] = []
    filters.append({'username': sender_name})
    return data.get_messages_by_filter(db=db, filters=filters)


def find_message_by_content_in_chat(db: Session, content: str, chat_id: int) -> list[Message]:
    filters: List[Dict[str, Any]] = []
    filters.append({'content': content})
    filters.append({'chat_id': chat_id})
    return data.get_messages_by_filter(db=db, filters=filters)