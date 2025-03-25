from fastapi import APIRouter, HTTPException, Depends, Request, Form, WebSocket, WebSocketDisconnect, WebSocketException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
import os
from datetime import timedelta, datetime

from ...models import Message, Chat, ChatCreateRequest
from ...errors import Duplicate, Missing
from ..deps import unauthed, oauth2_dep, get_db, websocket_token
from ...settings import TEMPLATES as templates
from ...settings import logger
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from backend.app.service import message as service_messages
from backend.app.service import chats as service_chats
from backend.app.service import users as service_users


router = APIRouter(prefix = "/chats")

active_connections = {}


@router.websocket("/ws/{username}")
async def websocket_endpoint(
        username: str,
        websocket: WebSocket,
        db: Session = Depends(get_db),
        token: str = Depends(websocket_token)
):
    await websocket.accept()

    try:
        user = service_users.get_current_user(db, token).username

        if user != username:
            raise WebSocketException(
                code=WS_1008_POLICY_VIOLATION,
                reason="Username mismatch"
            )

        active_connections[user] = websocket
        logger.info(f"WebSocket connected for user: {user}")

        try:
            while True:
                data = await websocket.receive_text()
                logger.debug(f"Heartbeat from {user}: {data}")

        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected for user: {user}")

    except WebSocketException as ex:
        logger.error(f"WebSocket error: {ex}")
        raise  # Переподнимаем исключение для закрытия соединения

    except Exception as ex:
        logger.error(f"Unexpected error: {ex}")
        raise WebSocketException(
            code=WS_1011_INTERNAL_ERROR,
            reason="Internal server error"
        )

    finally:
        if user in active_connections:
            del active_connections[user]


@router.get("/")
async def chat_page(request: Request, token = Depends(oauth2_dep), db: Session = Depends(get_db)):
    try:
        user = service_users.get_current_user(db=db, token=token)
        username = user.username
        chats = service_chats.all_chats_by_user(db=db, username=username)
        result =  {
            "user":username,
            "chats":chats
        }
        response = templates.TemplateResponse("chat_page.html", {"request": request, "response":result})
        return response
    except Exception as ex:
        raise HTTPException(status_code = 500, detail = f'Ops... {ex}')


@router.get("/all")
async def get_all_chats(request: Request, token = Depends(oauth2_dep), db: Session = Depends(get_db)):
    try:
        return service_chats.get_all(db)
    except Exception as ex:
        raise HTTPException(status_code = 500, detail = f'Ops... {ex.msg}')


@router.get("/{chat_id}")
async def get_chat(chat_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_dep)):
    try:
        user = service_users.get_current_user(db=db, token=token)
        if service_chats.check_user_in_chat(db=db, chat_id=chat_id, username=user.username):
            chat = service_chats.get_one(db, chat_id)
            if not chat:
                raise HTTPException(status_code=404, detail="Chat not found")
            return chat
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))


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


@router.post("/send")
async def send_message(
        request: Request,
        db: Session = Depends(get_db),
        token: str = Depends(oauth2_dep)
):
    try:
        data = await request.json()
        chat_id = data.get('chat_id')
        content = data.get('content')

        if not chat_id or not content:
            raise HTTPException(status_code=400, detail="Не указан ID чата или содержание сообщения")

        user = service_users.get_current_user(db, token)
        username = user.username

        if not service_chats.check_user_in_chat(db, chat_id, username):
            raise HTTPException(status_code=403, detail="Вы не участник этого чата")

        # Создаем и сохраняем сообщение
        message = Message(
            content=content,
            username=username,
            chat_id=chat_id
        )

        db_message = service_chats.add_message_to_chat(db=db, message_pydantic=message)

        db.add(db_message)
        db.commit()
        db.refresh(db_message)

        # Формируем данные для рассылки
        message_data = {
            "type": "new_message",
            "chat_id": chat_id,
            "message": {
                "content": db_message.content,
                "username": db_message.username,
                "timestamp": db_message.timestamp.isoformat(),
                "chat_id": db_message.chat_id
            }
        }

        # Рассылаем сообщения
        send_errors = []
        for recipient, ws in list(active_connections.items()):
            try:
                if recipient != username:
                    await ws.send_json(message_data)
            except Exception as e:
                logger.error(f"Failed to send to {recipient}: {e}")
                send_errors.append(recipient)

        # Удаляем неактивные соединения
        for recipient in send_errors:
            try:
                del active_connections[recipient]
            except KeyError:
                pass

        return {
            "status": "message_sent",
            "message": message_data["message"]
        }

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Ошибка базы данных")
    except Exception as ex:
        logger.error(f"Unexpected error: {ex}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.delete("/delete")
async def delete_chat(request: Request, chat_id: int, token: str = Depends(oauth2_dep), db: Session = Depends(get_db)):
    pass
