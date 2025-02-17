from pydantic import BaseModel, EmailStr
from datetime import datetime


class User(BaseModel):
    username : str
    email : EmailStr
    password: str
    about: str = ""


class PublicUserData(User):
    password: str = None 

    class Config:
        fields = {'password': {'exclude': True}}


class LoginUser(BaseModel):
    username : str
    password: str


class Message(BaseModel):
    sender : PublicUserData
    text_message : str
    datetime: datetime


class Chat(BaseModel):
    owner : PublicUserData
    users : list[PublicUserData]
