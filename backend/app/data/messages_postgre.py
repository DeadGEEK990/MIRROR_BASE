from sqlalchemy.orm import Session
from ..models import Message, MessageBase, pydantic_to_sqlalchemy, sqlalchemy_to_pydantic
from ..errors import Duplicate, Missing
from sqlalchemy.exc import IntegrityError
from typing import List, Dict, Any
from sqlalchemy.orm.query import Query
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound


def get_one(db: Session, message_id: int) -> Message:
    message = db.query(MessageBase).filter(MessageBase.id == message_id).first()
    if message:
        return sqlalchemy_to_pydantic(message, Message)
    else:
        raise Missing(msg=f"Message id={message_id} not found")


def get_all(db: Session) -> list[Message]:
    messagebase_list = db.query(MessageBase).all()
    return [sqlalchemy_to_pydantic(messagebase, Message) for messagebase in messagebase_list]


def create(db: Session, message: Message) -> Message:
    messagebase = pydantic_to_sqlalchemy(message, MessageBase)
    try:
        db.add(messagebase)
        db.commit()
        db.refresh(messagebase)
        return sqlalchemy_to_pydantic(messagebase, Message)
    except IntegrityError:
        db.rollback()
        raise Duplicate(msg=f"Message with id={message.id} already exists")


def get_messages_by_filter(db: Session, filters: List[Dict[str, Any]]) -> List[Message]:
    query: Query = db.query(MessageBase)
    try:
        for filter_item in filters:
            column = list(filter_item.keys())[0]
            value = filter_item[column]
            query = query.filter(getattr(MessageBase, column) == value)

        messagebase_list = query.all()
    except SQLAlchemyError as e:
        raise Missing(msg=f"Database error occurred: {str(e)}")
    except NoResultFound:
        raise Missing(msg="No messages found")
    except Exception as e:
        raise Missing(msg=f"An unexpected error occurred: {str(e)}")
    return [sqlalchemy_to_pydantic(messagebase, Message) for messagebase in messagebase_list]


def delete(db: Session, message_id: int) -> None:
    existing_messagebase = db.query(MessageBase).filter(MessageBase.id == message_id).first()
    if not existing_messagebase:
        raise Missing(msg=f"Message id={message_id} not found")
    db.delete(existing_messagebase)
    db.commit()
    return None