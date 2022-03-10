from fastapi import FastAPI, Depends, HTTPException, Request
from pydantic import ValidationError
from sqlalchemy.orm import Session
from oauth_app import database
from oauth_app.database import SessionLocal
from hashlib import sha256
from . import crud, models, schemas

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/clients/", response_model=schemas.Client)
async def create_client(req: Request, db: Session = Depends(get_db)):
    client = None

    try:
        if req.headers['Content-Type'] in ['application/x-www-form-urlencoded', 'multipart/form-data']:
            client = schemas.ClientCreate(** await req.form())
        elif req.headers['Content-Type'] == 'application/json':
            client = schemas.ClientCreate(** await req.json())
        else:
            raise HTTPException(status_code=400, detail="Content-Type not supported")
    except ValidationError:
        raise HTTPException(status_code=400, detail="Invalid request body")

    return crud.create_client(db, client=client)

@app.post("/users/", response_model=schemas.User)
async def create_user(req: Request, db: Session = Depends(get_db)):
    user = None

    try:
        if req.headers['Content-Type'] in ['application/x-www-form-urlencoded', 'multipart/form-data']:
            user = schemas.UserCreate(** await req.form())
        elif req.headers['Content-Type'] == 'application/json':
            user = schemas.UserCreate(** await req.json())
        else:
            raise HTTPException(status_code=400, detail="Content-Type not supported")
    except ValidationError:
        raise HTTPException(status_code=400, detail="Invalid request body")

    return crud.create_user(db, user=user)

@app.post("/oauth/token/", response_model=schemas.OAuthResponse)
async def create_user_token(req: Request, db: Session = Depends(get_db)):
    o_auth_request = None

    try:
        if req.headers['Content-Type'] in ['application/x-www-form-urlencoded', 'multipart/form-data']:
            o_auth_request = schemas.OAuthRequest(** await req.form())
        elif req.headers['Content-Type'] == 'application/json':
            o_auth_request = schemas.OAuthRequest(** await req.json())
        else:
            raise HTTPException(status_code=400, detail="Content-Type not supported")
    except ValidationError:
        raise HTTPException(status_code=400, detail="Invalid request body")

    return crud.create_user_token(db, o_auth_request=o_auth_request)

@app.post("/oauth/resource", response_model=schemas.UserResource)
async def get_user_resource(req: Request, db: Session = Depends(get_db)):
    raw_access_token = req.headers.get('Authorization', None)
    if raw_access_token is None:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    elif raw_access_token.split(' ')[0] != 'Bearer':
        raise HTTPException(status_code=401, detail="Invalid Authorization header token type")

    access_token = raw_access_token.split(' ')[1]

    user_resource = crud.get_user_resource(db, access_token=access_token)

    return user_resource