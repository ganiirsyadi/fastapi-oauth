from sqlalchemy.orm import Session
from hashlib import sha256
from . import models, schemas

def get_client_by_client_id(db: Session, client_id: str):
    return db.query(models.OAuthClient).filter(models.OAuthClient.client_id == client_id).first()

def create_client(db: Session, client: schemas.ClientCreate):
    hashed_secret = sha256(client.client_secret.encode()).hexdigest()
    db_client = models.OAuthClient(client_id=client.client_id, client_secret=hashed_secret, scope=client.scope)
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = sha256(user.password.encode()).hexdigest()
    db_user = models.User(email=user.email, hashed_password=hashed_password, client_id=user.client_id)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
    

