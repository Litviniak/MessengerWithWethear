from pydantic import BaseModel
from datetime import datetime


class MessageBase(BaseModel):
    content: str
    author_id: int


class MessageCreate(MessageBase):
    class Config:
        orm_mode = True


class Message(MessageBase):
    id: int
    reciver_id: int
    is_recived: bool
    date: datetime

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    login: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True


