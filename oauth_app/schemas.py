from typing import Optional
from click import password_option
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
    username: str

class UserCreate(UserBase):
    password: str
    full_name: str
    npm: str
    client_id: str
    client_secret: str

class User(UserBase):
    id: int
    full_name: str
    npm: str
    class Config:
        orm_mode = True

class OAuthRequest(BaseModel):
    username: str
    password: str
    grant_type: str
    client_id: str
    client_secret: str

class OAuthResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str
    scope: Optional[str]

class UserResource(BaseModel):
    access_token: str
    refresh_token: str
    client_id: str
    user_id: str
    full_name: str
    npm: str
    expires: Optional[str]
    