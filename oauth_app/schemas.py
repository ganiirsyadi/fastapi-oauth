from typing import Optional
from pydantic import BaseModel


class ClientBase(BaseModel):
    client_id: str
    scope: Optional[str] = None

class ClientCreate(ClientBase):
    client_secret: str

class Client(ClientBase):
    id: int
    class Config:
        orm_mode = True

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str
    client_id: str
    client_secret: str

class User(UserBase):
    id: int
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    scope: Optional[str]
    refresh_token: str

