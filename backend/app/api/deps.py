from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
from jose import JWTError


def unauthed():
    raise HTTPException(status_code=302, detail="Redirecting to registration", headers={"Location": "/registration"})

from fastapi import Depends, HTTPException, Request
from jose import jwt  # Если вы используете JWT токены
from ..settings import SECRET_KEY, ALGORITHM

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