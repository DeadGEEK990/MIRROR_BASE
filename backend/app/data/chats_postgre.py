from sqlalchemy.orm import Session
from ..models import ChatBase, Chat, pydantic_to_sqlalchemy, sqlalchemy_to_pydantic, User, UserBase, Message, MessageBase
from ..errors import Duplicate, Missing
from sqlalchemy.exc import IntegrityError
from typing import List, Dict, Any
from sqlalchemy.orm.query import Query
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound
from datetime import datetime


def check_user_in_chat(db: Session, chat_id: int, username: str) -> bool:
    try:
        # Ищем чат по chat_id
        chat = db.query(ChatBase).filter(ChatBase.id == chat_id).first()
        # Ищем пользователя по username
        user = db.query(UserBase).filter(UserBase.username == username).first()

        # Если чат или пользователь не найдены, возвращаем False
        if not chat or not user:
            return False

        # Проверяем, есть ли пользователь в списке пользователей чата
        if user in chat.users:
            return True

        return False
    except SQLAlchemyError:
        db.rollback()
        return False



def add_user_to_chat(db: Session, chat_id: int, username: str) -> bool:
    try:
        chat = db.query(ChatBase).filter(ChatBase.id == chat_id).first()
        user = db.query(UserBase).filter(UserBase.username == username).first()
        if not chat or not user:
            return False
        if user not in chat.users:
            chat.users.append(user)
            db.commit()
            return True
        return False
    except SQLAlchemyError:
        db.rollback()
        return False


def remove_user_from_chat(db: Session, chat_id: int, username: str) -> bool:
    try:
        chat = db.query(ChatBase).filter(ChatBase.id == chat_id).first()
        user = db.query(UserBase).filter(UserBase.username == username).first()
        if not chat or not user:
            return False
        if user in chat.users:
            chat.users.remove(user)
            db.commit()
            return True
        return False
    except SQLAlchemyError:
        db.rollback()
        return False


def add_message_to_chat(db: Session, message_pydantic: Message) -> bool:
    try:
        username = Message.username
        chat_id = Message.chat_id
        chat = db.query(ChatBase).filter(ChatBase.id == chat_id).first()
        user = db.query(UserBase).filter(UserBase.username == username).first()
        if not chat or not user:
            return False
        message = pydantic_to_sqlalchemy(message_pydantic, MessageBase)
        db.add(message)
        db.commit()
        return True
    except SQLAlchemyError:
        db.rollback()
        return False


def delete_message_from_chat(db: Session, message_id: int) -> bool:
    try:
        message = db.query(MessageBase).filter(MessageBase.id == message_id).first()
        if message:
            db.delete(message)
            db.commit()
            return True
        return False
    except SQLAlchemyError:
        db.rollback()
        return False


def get_one(db : Session, chat_id : int) -> Chat:
    chat = db.query(ChatBase).filter(ChatBase.id == chat_id).first()
    if chat:
        return sqlalchemy_to_pydantic(chat, Chat)
    else:
        raise Missing(msg=f"Message id={chat_id} not found")


def get_all(db: Session) -> list[Chat]:
    try:
        chatbase_list = db.query(ChatBase).all()
        return [sqlalchemy_to_pydantic(chatbase, Chat) for chatbase in chatbase_list]
    except SQLAlchemyError as e:
        raise Missing(msg=f"Database error occurred: {str(e)}")
    except NoResultFound:
        raise Missing(msg="No chat found")
    except Exception as e:
        raise Missing(msg=f"An unexpected error occurred: {str(e)}")


def create(db: Session, chat: Chat) -> Chat:
    chatbase = pydantic_to_sqlalchemy(chat, ChatBase)
    try:
        db.add(chatbase)
        db.commit()
        db.refresh(chatbase)
        return sqlalchemy_to_pydantic(chatbase, Chat)
    except IntegrityError:
        db.rollback()
        raise Duplicate(msg=f"Message with id={chat.id} already exists")
    except SQLAlchemyError as e:
        raise Missing(msg=f"Database error occurred: {str(e)}")


def get_chats_by_filter(db: Session, filters: List[Dict[str, Any]]) -> List[Chat]:
    query: Query = db.query(ChatBase)
    try:
        for filter_item in filters:
            column = list(filter_item.keys())[0]
            value = filter_item[column]
            query = query.filter(getattr(ChatBase, column) == value)

        chatbase_list = query.all()
    except SQLAlchemyError as e:
        raise Missing(msg=f"Database error occurred: {str(e)}")
    except NoResultFound:
        raise Missing(msg="No messages found")
    except Exception as e:
        raise Missing(msg=f"An unexpected error occurred: {str(e)}")
    return [sqlalchemy_to_pydantic(chatbase, Chat) for chatbase in chatbase_list]


def delete(db: Session, chat_id: int) -> None:
    try:
        existing_chatbase = db.query(ChatBase).filter(ChatBase.id == chat_id).first()
        if not existing_chatbase:
            raise Missing(msg=f"Chat id={chat_id} not found")
        db.delete(existing_chatbase)
        db.commit()
        return None
    except SQLAlchemyError as e:
        raise Missing(msg=f"Database error occurred: {str(e)}")
    except NoResultFound:
        raise Missing(msg="No chat found")
    except Exception as e:
        raise Missing(msg=f"An unexpected error occurred: {str(e)}")