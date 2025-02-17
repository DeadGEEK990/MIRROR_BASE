from backend.app.models import User
from jose import jwt, JWTError
from datetime import timedelta, datetime
from fastapi import Request
from backend.app.errors import Duplicate, Missing
import os 
import sys

from backend.app.tests.fake.data import users as data

from passlib.context import CryptContext
from backend.app.settings import SECRET_KEY, ALGORITHM

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../..')))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")


def verify_password(plain : str, hash : str) -> bool:
    """Хеширование строки и сравнение её с базой данных"""
    return pwd_context.verify(plain, hash)


def get_hash(plain : str) -> str:
    return pwd_context.hash(plain)


def get_jwt_username(token : str) -> str | None:
    """Возврат имени пользователя из jwt доступа"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        if not (username := payload.get("sub")):
            return None
        return username
    except JWTError:
        return None
    


def get_curret_user(token : str) -> User | None:
    """Декодирование токена доступа и возврат объекта User"""
    if not (username := get_jwt_username(token)):
        return None
    if (user := lookup_user(username)):
        return user
    return None


def lookup_user(username : str) -> User | None:
    """Возврат совподающего пользователя из базы данных для строки name"""
    try:
        if (user := data.get_one(username)):
            return user
    except Missing:
        return None
    

def auth_user(username : str, plain : str) -> User | None:
    """Аутентификация пользователя name и plain пароль"""
    if not (user := lookup_user(username = username)):
        return None
    if not verify_password(plain, user.password):
        return None
    return user


def create_access_token(data: dict, expires: timedelta | None = None):
    """Возвращение токена доступа"""
    src = data.copy()
    now = datetime.utcnow()
    if not expires:
        expires = timedelta(minutes=15)
    src.update({"exp":now + expires})
    encoded_jwt = jwt.encode(src, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_one(username : str) -> User:
    return data.get_one(username)

    
def get_all() -> list[User]:
    return data.get_all()


def create(user : User) -> User:
    return data.create(user)


def modify(user : User) -> User:
    return data.modify(user)


def delete(user : User) -> bool:
    return data.delete()