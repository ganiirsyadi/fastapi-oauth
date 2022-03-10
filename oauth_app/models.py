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
    username = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String)
    full_name = Column(String(255), unique=False, nullable=False, index=True)
    npm = Column(String(255), unique=True, nullable=False, index=True)
    expires = Column(DateTime, nullable=True)
    client_id = Column(Integer, ForeignKey("oauth_clients.id"), nullable=False)

    client = relationship("OAuthClient", back_populates="users")
    tokens = relationship("Token", back_populates="user")

class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    access_token = Column(String(255), unique=True, nullable=False, index=True)
    refresh_token = Column(String(255), unique=True, nullable=False, index=True)
    token_expiration = Column(DateTime, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="tokens")