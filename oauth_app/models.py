from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base


class OAuthClient(Base):
    __tablename__ = "oauth_clients"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    client_id = Column(String(255), unique=True, nullable=False, index=True)
    client_secret = Column(String(255), unique=False, nullable=False, index=True)
    scope = Column(String(255), unique=False, nullable=True, index=True)

    users = relationship("User", back_populates="client")

    def __str__(self):
        return str({
            "id": self.id,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": self.scope
        })

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

    def __str__(self) -> str:
        return str({
            "id": self.id,
            "username": self.username,
            "full_name": self.full_name,
            "npm": self.npm,
            "client_id": self.client_id
        })

class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    access_token = Column(String(255), unique=True, nullable=False, index=True)
    refresh_token = Column(String(255), unique=True, nullable=False, index=True)
    token_expiration = Column(DateTime, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="tokens")

    def __str__(self) -> str:
        return str({
            "id": self.id,
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "token_expiration": self.token_expiration,
            "user_id": self.user_id
        })