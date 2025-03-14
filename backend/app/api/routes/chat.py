from fastapi import APIRouter, HTTPException, Depends, Request, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
import os
from datetime import timedelta, datetime

from ...models import Message
from ...errors import Duplicate, Missing
from ..deps import unauthed, oauth2_dep, get_db
from ...settings import TEMPLATES as templates
from sqlalchemy.orm import Session

from backend.app.service import message as service_messages


router = APIRouter(prefix = "/chats")


@router.get("/")
def get_chats(request : Request, chat_id : int, token = Depends(oauth2_dep), db : Session = Depends(get_db)):
    pass