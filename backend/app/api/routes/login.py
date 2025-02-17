import os
import sys
from fastapi import APIRouter, HTTPException, Request, Form, Depends
from fastapi.responses import RedirectResponse
from ...errors import Duplicate, Missing, MailDuplicate
from ...models import User
if os.getenv("MIRROR_TESTS"):
    from ...tests.fake.service import users as service
else:
    from ...service import users as service
from ...settings import TEMPLATES as templates
from ..deps import oauth2_dep, unauthed, get_token_from_cookies


router = APIRouter(tags=["login","registration"])


@router.get("/")
async def main_link(request : Request, token:str = Depends(oauth2_dep)):
    try:
        user = service.get_curret_user(token = token)
        response = RedirectResponse(url = f"/users/{user.username}")
        response.status_code = 302
        print(f"Redirecting to /users/{user.username}") 
        return response
    except Exception:
        unauthed()


@router.get("/registration")
async def registration_page(request : Request):
    try:
        if ((token := request.cookies.get("access_token")) and (user := service.get_curret_user(token=token))):
            response = RedirectResponse(url = f"/users/{user.username}")
            response.status_code = 302
        else:
            response = templates.TemplateResponse("registration_page.html", {"request":request})
        return response
    except Exception as ex:
        raise HTTPException(status_code=404, detail=f"Ooops... {ex}")
        


@router.post("/registration")
async def registration_user(request : Request, 
                      username: str = Form(...),
                      email:str = Form(...),
                      password:str = Form(...)):
    try:
        user = User(username=username, email=email, password=service.get_hash(password))
        service.create(user)
        response = RedirectResponse(url="/login")
        response.status_code = 302
        return response
    except Duplicate as ex:
        raise HTTPException(status_code=409, detail=ex.msg)
    except MailDuplicate as ex:
        raise HTTPException(status_code=409, detail="The mail is busy", headers={"Location": "/registration"})
    except Exception as ex:
        raise HTTPException(status_code=404, detail=f"Error {ex}")
    

@router.get("/login")
async def login_page(requets: Request):
    try:
        return templates.TemplateResponse("login_page.html", {"request":requets})
    except Exception as ex:
        raise HTTPException(status_code=404, detail=f"Error: {ex}")
    

@router.post("/login")
async def login_user(request : Request,
               username : str = Form(...),
               password : str = Form(...)):
    try:
        db_user = service.auth_user(username = username, plain=password)
    except Missing:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    access_token = service.create_access_token(data={"sub":username})
    response = RedirectResponse(url=f"/users/{username}")
    response.status_code = 302
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response

