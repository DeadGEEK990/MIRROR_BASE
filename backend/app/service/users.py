from ..models import User
from jose import jwt, JWTError
from datetime import timedelta, datetime
from fastapi import Request
from ..errors import Duplicate, Missing
import os
from sqlalchemy.orm import Session

from ..data import users_postgre as data

from passlib.context import CryptContext
from ..settings import SECRET_KEY, ALGORITHM

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
    


def get_curret_user(db : Session, token : str) -> User | None:
    """Декодирование токена доступа и возврат объекта User"""
    if not (username := get_jwt_username(token)):
        return None
    if (user := lookup_user(db, username)):
        return user
    return None


def lookup_user(db : Session, username : str) -> User | None:
    """Возврат совподающего пользователя из базы данных для строки name"""
    try:
        if (user := data.get_one(db, username)):
            return user
    except Missing:
        return None
    

def auth_user(db : Session, username : str, plain : str) -> User | None:
    """Аутентификация пользователя name и plain пароль"""
    if not (user := lookup_user(db, username = username)):
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


def get_one(db : Session, username : str) -> User:
    return data.get_one(db, username)

    
def get_all(db : Session) -> list[User]:
    return data.get_all(db)


def create(db : Session, user : User) -> User:
    return data.create(db, user)


def modify(db : Session, user : User) -> User:
    return data.modify(db, user)


def delete(db : Session, user : User) -> bool:
    return data.delete(db, user)