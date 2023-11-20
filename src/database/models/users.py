import enum

from sqlalchemy import (Boolean, Column, DateTime, Enum, ForeignKey, Integer,
                        String, func)
from sqlalchemy.orm import relationship

from src.database.db import Base


class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", backref="posts")


class Roles(enum.Enum):
    admin: str = "admin"
    moderator: str = "moderator"
    user: str = "user"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    roles = Column("role", Enum(Roles), default=Roles.user)
    created_at = Column(DateTime, default=func.now())
    refresh_token = Column(String(255), nullable=True)
    confirmed = Column(Boolean, default=False)
    description = Column(String(500), nullable=True)
