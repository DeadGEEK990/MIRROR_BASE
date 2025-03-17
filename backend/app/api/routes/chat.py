from fastapi import APIRouter, HTTPException, Depends, Request, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
import os
from datetime import timedelta, datetime

from ...models import Message, Chat
from ...errors import Duplicate, Missing
from ..deps import unauthed, oauth2_dep, get_db
from ...settings import TEMPLATES as templates
from sqlalchemy.orm import Session

from backend.app.service import message as service_messages
from backend.app.service import chats as service_chats
from backend.app.service import users as service_users


router = APIRouter(prefix = "/chats")


@router.get("/all")
async def get_all_chats(request : Request, token = Depends(oauth2_dep), db : Session = Depends(get_db)):
    return service_chats.get_all(db)


@router.post("/create")
async def create_chat(request : Request, chat : Chat, db : Session = Depends(get_db)):
    return service_chats.create(db, chat)


@router.patch("/send")
async def send_message(request : Request, chat_id : int, content : str, token = Depends(oauth2_dep), db : Session = Depends(get_db)):
    try:
        username = service_users.get_current_user(db, token)
        in_chat:bool = service_chats.check_user_in_chat(db,chat_id,username)
        if in_chat:
            message = Message(content = content, username = username, chat_id = chat_id)
            service_chats.add_message_to_chat(db, message)
            chat:Chat = service_chats.get_one(db, chat_id)
            return chat
        else:
            return {'detail':'Ты не приглашен на эту вечеринку :('}
    except Exception as ex:
        raise HTTPException(status_code = 404, detail='Ops...')