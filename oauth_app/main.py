from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.orm import Session
from oauth_app import database
from oauth_app.database import SessionLocal
from .exceptions import GlobalException
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

# Exception handler
@app.exception_handler(GlobalException)
async def exception_handler(request: Request, exc: GlobalException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error,
            "error_description": exc.error_description,
        },
    )

@app.post("/clients/", response_model=schemas.Client)
async def create_client(req: Request, db: Session = Depends(get_db)):
    client = None

    try:
        if req.headers['Content-Type'] in ['application/x-www-form-urlencoded', 'multipart/form-data']:
            client = schemas.ClientCreate(** await req.form())
        elif req.headers['Content-Type'] == 'application/json':
            client = schemas.ClientCreate(** await req.json())
        else:
            raise GlobalException(status_code=400, error="Bad Request", error_description="Content-Type not supported")
    except ValidationError:
        raise GlobalException(status_code=400, error="Bad Request", error_description="Invalid request body")

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
            raise GlobalException(status_code=400, error="Bad Request", error_description="Content-Type not supported")
    except ValidationError:
        raise GlobalException(status_code=400, error="Bad Request", error_description="Invalid request body")

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
            raise GlobalException(status_code=400, error="Bad Request", error_description="Content-Type not supported")
    except ValidationError:
        raise GlobalException(status_code=400, error="Bad Request", error_description="Invalid request body")

    return crud.create_user_token(db, o_auth_request=o_auth_request)

@app.post("/oauth/resource", response_model=schemas.UserResource)
async def get_user_resource(req: Request, db: Session = Depends(get_db)):
    raw_access_token = req.headers.get('Authorization', None)
    if raw_access_token is None:
        raise GlobalException(status_code=401, error="Unauthorized", error_description="Missing Authorization header")
    elif raw_access_token.split(' ')[0] != 'Bearer':
        raise GlobalException(status_code=401, error="Unauthorized", error_description="Invalid Authorization header token type")

    access_token = raw_access_token.split(' ')[1]

    user_resource = crud.get_user_resource(db, access_token=access_token)

    return user_resource