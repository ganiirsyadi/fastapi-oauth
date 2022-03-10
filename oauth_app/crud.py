import datetime
from http import client
from fastapi import HTTPException
from sqlalchemy.orm import Session
from hashlib import sha256

from oauth_app.utils import generate_random_string
from . import models, schemas

def get_client_by_client_id(db: Session, client_id: str):
    return db.query(models.OAuthClient).filter(models.OAuthClient.client_id == client_id).first()

def create_client(db: Session, client: schemas.ClientCreate):
    db_client = get_client_by_client_id(db, client_id=client.client_id)

    if db_client:
        raise HTTPException(status_code=400, detail="Client already registered")

    hashed_secret = sha256(client.client_secret.encode()).hexdigest()
    db_client = models.OAuthClient(client_id=client.client_id, client_secret=hashed_secret, scope=client.scope)
    
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    db_client = get_client_by_client_id(db, client_id=user.client_id)

    if not db_client:
        raise HTTPException(status_code=400, detail="Client not registered")

    if db_client.client_secret != sha256(user.client_secret.encode()).hexdigest():
        raise HTTPException(status_code=400, detail="Client secret is invalid")

    db_user = get_user_by_username(db, username=user.username)

    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = sha256(user.password.encode()).hexdigest()
    db_user = models.User(
        username=user.username, 
        hashed_password=hashed_password, 
        client_id=user.client_id,
        full_name=user.full_name,
        npm=user.npm
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_user_token(db: Session, o_auth_request: schemas.OAuthRequest):

    if o_auth_request.grant_type != "password":
        raise HTTPException(status_code=400, detail="Grant type only support password")

    db_client = get_client_by_client_id(db, client_id=o_auth_request.client_id)

    if not db_client:
        raise HTTPException(status_code=400, detail="Client not registered")

    if db_client.client_secret != sha256(o_auth_request.client_secret.encode()).hexdigest():
        raise HTTPException(status_code=400, detail="Client secret is invalid")

    db_user = get_user_by_username(db, username=o_auth_request.username)

    if not db_user:
        raise HTTPException(status_code=400, detail="User not registered")

    if db_user.hashed_password != sha256(o_auth_request.password.encode()).hexdigest():
        raise HTTPException(status_code=400, detail="Password is invalid")

    access_token = models.Token(
        access_token= generate_random_string(length=40),
        refresh_token= generate_random_string(length=40),
        token_expiration= datetime.datetime.utcnow() + datetime.timedelta(minutes=5), 
        user_id= db_user.id
    )

    db.add(access_token)
    db.commit()
    db.refresh(access_token)

    o_auth_response = schemas.OAuthResponse(
        access_token= access_token.access_token,
        token_type= "Bearer",
        expires_in= 5 * 60,
        refresh_token= access_token.refresh_token,
        scope= db_client.scope
    )

    return o_auth_response

def get_user_resource(db: Session, access_token: str):
    db_token = db.query(models.Token).filter(models.Token.access_token == access_token).first()

    if not db_token:
        raise HTTPException(status_code=400, detail="Token not found")

    if db_token.token_expiration < datetime.datetime.utcnow():
        raise HTTPException(status_code=400, detail="Token expired")

    db_user = db.query(models.User).filter(models.User.id == db_token.user_id).first()

    if not db_user:
        raise HTTPException(status_code=400, detail="User not found")

    user_resource = schemas.UserResource(
        user_id= db_user.username,
        full_name= db_user.full_name,
        npm= db_user.npm,
        access_token= access_token,
        refresh_token= db_token.refresh_token,
        expires= db_user.expires,
        client_id= db_user.client_id
    )


    return user_resource