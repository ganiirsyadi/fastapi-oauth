import logging

from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from logstash_async.handler import (AsynchronousLogstashHandler,
                                    LogstashFormatter)
from pydantic import ValidationError
from sqlalchemy.orm import Session

from oauth_app import database
from oauth_app.database import SessionLocal

from . import crud, models, schemas
from .exceptions import GlobalException
from .log import logger

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
    params = None
    try:
        if req.headers['Content-Type'] in ['application/x-www-form-urlencoded', 'multipart/form-data']:
            params = await req.form()
            client = schemas.ClientCreate(** params)
        elif req.headers['Content-Type'] == 'application/json':
            params = await req.json()
            client = schemas.ClientCreate(** params)
        else:
            logger.error(f"Client create request: error=Content-Type not supported, Content-Type={req.headers['Content-Type']}")
            raise GlobalException(status_code=400, error="Bad Request",
                                  error_description="Content-Type not supported")
    except ValidationError:
        params = await req.json()
        logger.error(f"Client create request: error=Invalid request body, params={params}")
        raise GlobalException(
            status_code=400, error="Bad Request", error_description="Invalid request body")

    res = crud.create_client(db, client=client, params=params)
    logger.info(f"Client create request: params={params}, response={res}")
    return res


@app.post("/users/", response_model=schemas.User)
async def create_user(req: Request, db: Session = Depends(get_db)):
    user = None
    params = None
    try:
        if req.headers['Content-Type'] in ['application/x-www-form-urlencoded', 'multipart/form-data']:
            params = await req.form()
            user = schemas.UserCreate(** params)
        elif req.headers['Content-Type'] == 'application/json':
            params = await req.json()
            user = schemas.UserCreate(** params)
        else:
            logger.error(f"User create request: error=Content-Type not supported, Content-Type={req.headers['Content-Type']}")
            raise GlobalException(status_code=400, error="Bad Request",
                                  error_description="Content-Type not supported")
    except ValidationError:
        params = await req.json()
        logger.error(f"User create request: error=Invalid request body, params={params}")
        raise GlobalException(
            status_code=400, error="Bad Request", error_description="Invalid request body")
    res = crud.create_user(db, user=user, params=params)
    logger.info(f"User create request: params={params}, response={res}")
    return res


@app.post("/oauth/token/", response_model=schemas.OAuthResponse)
async def create_user_token(req: Request, db: Session = Depends(get_db)):
    o_auth_request = None
    params = None
    try:
        if req.headers['Content-Type'] in ['application/x-www-form-urlencoded', 'multipart/form-data']:
            params = await req.form()
            o_auth_request = schemas.OAuthRequest(** params)
        elif req.headers['Content-Type'] == 'application/json':
            params = await req.json()
            o_auth_request = schemas.OAuthRequest(** params)
        else:
            logger.error(f"OAuth request: error=Content-Type not supported, Content-Type={req.headers['Content-Type']}")
            raise GlobalException(status_code=400, error="Bad Request",
                                  error_description="Content-Type not supported")
    except ValidationError:
        params = await req.json()
        logger.error(f"OAuth request: error=Invalid request body, params={params}")
        raise GlobalException(
            status_code=400, error="Bad Request", error_description="Invalid request body")
    res = crud.create_user_token(db, o_auth_request=o_auth_request, params=params)
    logger.info(f"OAuth request: params={params}, response={res}")
    return res


@app.post("/oauth/resource", response_model=schemas.UserResource)
async def get_user_resource(req: Request, db: Session = Depends(get_db)):
    headers = req.headers
    raw_access_token = headers.get('Authorization', None)
    if raw_access_token is None:
        logger.error(f"OAuth resource request: error=Authorization header not found, headers={headers}")
        raise GlobalException(status_code=401, error="Unauthorized",
                              error_description="Missing Authorization header")
    elif raw_access_token.split(' ')[0] != 'Bearer':
        logger.error(f"OAuth resource request: error=Authorization header not supported, headers={headers}")
        raise GlobalException(status_code=401, error="Unauthorized",
                              error_description="Invalid Authorization header token type")

    access_token = raw_access_token.split(' ')[1]

    res = crud.get_user_resource(db, access_token=access_token, params=headers)

    logger.info(f"OAuth resource request: headers={headers}, response={res}")

    return res
