from fastapi import APIRouter, HTTPException, Depends, Request, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
import os
from datetime import timedelta, datetime

from ...models import User
from ...errors import Duplicate, Missing
from ..deps import unauthed, oauth2_dep, get_db
from ...settings import TEMPLATES as templates
from sqlalchemy.orm import Session

if os.getenv("MIRROR_TESTS"):
    from ...tests.fake.service import users as service
else:
    from ...service import users as service


ACCESS_TOKEN_EXPIRE_MINUTES = 30


router = APIRouter(prefix="/users")


@router.post("/token")
async def create_access_token(form_data : OAuth2PasswordRequestForm = Depends()):
    user = service.auth_user(form_data.username, form_data.password)
    if not user:
        unauthed()
    expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = service.create_access_token(data={"sub":user.username}, expires=expires)
    return {"access_token":access_token, "token_type":"bearer"}


@router.get("/token")
async def get_access_token(token : str = Depends(oauth2_dep)) -> dict:
    return {"token" : token}


@router.get("/")
async def get_all(db: Session = Depends(get_db)):
    return service.get_all(db=db)


@router.get("/{username}")
async def user_page(request: Request, username:str, token:str = Depends(oauth2_dep), db: Session = Depends(get_db)):
    try:
        user = service.get_one(db, username)
        can_edit = service.get_current_user(db, token) == user

        return templates.TemplateResponse("user_page.html", {
            "request": request,  # Это нужно для работы Jinja2
            "username": user.username,
            "email": user.email,
            "about": user.about,
            "can_edit": can_edit
        })
    except Missing as ex:
        raise HTTPException(status_code = 404, detail = ex.msg)
    except Exception as ex:
        raise HTTPException(status_code=404, detail=f"Oops... Fuck me.")
    

@router.delete("/{username}")
async def user_page_delete(request: Request, username:str, token:str = Depends(oauth2_dep)):
    pass