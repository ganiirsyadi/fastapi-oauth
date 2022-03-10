from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base


class OAuthClient(Base):
    __tablename__ = "oauth_clients"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    client_id = Column(String(255), unique=True, nullable=False, index=True)
    client_secret = Column(String(255), unique=False, nullable=False, index=True)
    scope = Column(String(255), unique=True, nullable=True, index=True)

    users = relationship("User", back_populates="client")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String)
    token = Column(String(255), unique=True, nullable=True, index=True)
    token_expiration = Column(DateTime, nullable=True)
    client_id = Column(Integer, ForeignKey("oauth_clients.id"), nullable=False)

    client = relationship("OAuthClient", back_populates="users")

