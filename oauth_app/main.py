from fastapi import FastAPI, Depends, HTTPException, Request
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

    if req.headers['Content-Type'] in ['application/x-www-form-urlencoded', 'multipart/form-data']:
        client = schemas.ClientCreate(** await req.form())
    elif req.headers['Content-Type'] == 'application/json':
        client = schemas.ClientCreate(** await req.json())

    db_client = crud.get_client_by_client_id(db, client_id=client.client_id)
    if db_client:
        raise HTTPException(status_code=400, detail="Client already registered")
    return crud.create_client(db, client=client)

@app.post("/users/", response_model=schemas.User)
async def create_user(req: Request, db: Session = Depends(get_db)):
    user = None

    if req.headers['Content-Type'] in ['application/x-www-form-urlencoded', 'multipart/form-data']:
        user = schemas.UserCreate(** await req.form())
    elif req.headers['Content-Type'] == 'application/json':
        user = schemas.UserCreate(** await req.json())

    db_client = crud.get_client_by_client_id(db, client_id=user.client_id)
    if db_client.client_secret != sha256(user.client_secret.encode()).hexdigest():
        raise HTTPException(status_code=400, detail="Client secret is invalid")

    db_user = crud.get_user_by_email(db, email=user.email)

    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db, user=user)