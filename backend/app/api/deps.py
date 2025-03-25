from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import APIRouter, HTTPException, Depends, Request, WebSocket, WebSocketException
from fastapi.responses import RedirectResponse
from jose import JWTError

from sqlalchemy.orm import Session
from ..db.init_postgre import SessionLocal
from typing import Generator

from fastapi import Depends, HTTPException, Request
from jose import jwt  # Если вы используете JWT токены
from ..settings import SECRET_KEY, ALGORITHM


def unauthed():
    raise HTTPException(status_code=302, detail="Redirecting to registration", headers={"Location": "/registration"})


# Зависимость для получения токена из cookies
def get_token_from_cookies(request: Request) -> str:
    token = request.cookies.get("access_token")  # Извлекаем токен из cookies
    if not token:
        unauthed()
    return token

# Зависимость для проверки токена
def oauth2_dep(token: str = Depends(get_token_from_cookies)):
    try:
        # Здесь ваша логика проверки токена, например, декодирование JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        username = payload.get("sub")  # Обычно в JWT токене хранится имя пользователя в поле "sub"
        if not username:
            unauthed()
        return token
    except JWTError:
        unauthed()


async def websocket_token(websocket: WebSocket):
    # Пробуем получить токен из:
    # 1. Cookies
    # 2. Query параметров (?token=...)

    token = websocket._cookies.get("access_token")
    if not token:
        token = websocket.query_params.get("token")

    if not token:
        await websocket.close(code=WS_1008_POLICY_VIOLATION)
        raise WebSocketException(
            code=WS_1008_POLICY_VIOLATION,
            reason="Missing authentication token"
        )

    return token


def get_db() -> Generator[Session, None, None]:
    """Предоставляет сессию базы данных на время жизненного цикла запроса."""
    db = SessionLocal()
    try:
        yield db  # Выдаем сессию в функцию, которая вызывает зависимость
    finally:
        db.close()