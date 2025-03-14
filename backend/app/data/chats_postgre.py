from sqlalchemy.orm import Session
from ..models import ChatBase, Chat, pydantic_to_sqlalchemy, sqlalchemy_to_pydantic
from ..errors import Duplicate, Missing
from sqlalchemy.exc import IntegrityError
from typing import List, Dict, Any
from sqlalchemy.orm.query import Query
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound


def get_one(db : Session, chat_id : int) -> Chat:
    chat = db.query(ChatBase).filter(ChatBase.id == chat_id).first()
    if chat:
        return sqlalchemy_to_pydantic(chat, Chat)
    else:
        raise Missing(msg=f"Message id={chat_id} not found")


def get_all(db: Session) -> list[Chat]:
    chatbase_list = db.query(ChatBase).all()
    return [sqlalchemy_to_pydantic(chatbase, Chat) for chatbase in chatbase_list]


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
    existing_chatbase = db.query(ChatBase).filter(ChatBase.id == chat_id).first()
    if not existing_chatbase:
        raise Missing(msg=f"Message id={chat_id} not found")
    db.delete(existing_chatbase)
    db.commit()
    return None