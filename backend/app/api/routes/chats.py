from fastapi import APIRouter, HTTPException, Depends, Request, Form, WebSocket, WebSocketDisconnect
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
import os
from datetime import timedelta, datetime

from ...models import Message, Chat, ChatCreateRequest
from ...errors import Duplicate, Missing
from ..deps import unauthed, oauth2_dep, get_db
from ...settings import TEMPLATES as templates
from ...settings import logger
from sqlalchemy.orm import Session

from backend.app.service import message as service_messages
from backend.app.service import chats as service_chats
from backend.app.service import users as service_users


router = APIRouter(prefix = "/chats")


@router.get("/")
async def chat_page(request: Request, token = Depends(oauth2_dep), db: Session = Depends(get_db)):
    try:
        user = service_users.get_current_user(db=db, token=token)
        username = user.username
        chats = service_chats.all_chats_by_user(db=db, username=username)
        chats_dict:list[dict] = []
        for chat in chats:
            chat_dict = {
                "id":chat.id,
                "title":chat.title
            }
            chats_dict.append(chat_dict)

        response = {
            "chats_list":chats_dict
        }
        return response
    except Exception as ex:
        raise HTTPException(status_code = 500, detail = f'Ops... {ex}')


@router.get("/all")
async def get_all_chats(request: Request, token = Depends(oauth2_dep), db: Session = Depends(get_db)):
    try:
        return service_chats.get_all(db)
    except Exception as ex:
        raise HTTPException(status_code = 500, detail = f'Ops... {ex.msg}')


@router.get("/create")
async def get_frontend(request: Request):
    return templates.TemplateResponse("create_chat.html", {"request": request})


@router.post("/create")
async def create_chat(request: Request,
                      chat: ChatCreateRequest,  # Получаем данные из тела запроса
                      db: Session = Depends(get_db),
                      token = Depends(oauth2_dep)):
    try:
        chat_obj = service_chats.create(db=db, chat = chat, token=token)
        return {
            "message": "Чат успешно создан",
            "chat_title": chat.chat_title,
            "users": chat.users
        }
    except Exception as ex:
        logger.error(f"Получены данные для создания чата: Title = {chat.chat_title}, Users = {chat.users}")
        logger.error(f"Ошибка при создании чата: {str(ex)}")
        raise HTTPException(status_code=422, detail=f"Ops... {ex}")


@router.patch("/send")
async def send_message(request: Request, chat_id: int, content: str, token = Depends(oauth2_dep), db: Session = Depends(get_db)):
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


@router.delete("/delete")
async def delete_chat(request: Request, chat_id: int, token: str = Depends(oauth2_dep), db: Session = Depends(get_db)):
    pass
