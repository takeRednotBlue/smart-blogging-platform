import enum

from sqlalchemy import Column, Integer, String, DateTime, func, Enum, Table
from sqlalchemy.orm import relationship
from src.database.db import Base
from sqlalchemy.sql.schema import ForeignKey
from datetime import datetime


posts_tags = Table(
    "posts_tags",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("post_id", Integer, ForeignKey("posts.id", ondelete="CASCADE")),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE")),
)


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    text = Column(String)
    created_at = Column(DateTime, default=datetime.now())
    tags = relationship("Tag", secondary=posts_tags, backref="posts")


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    name = Column(String(25), nullable=False, unique=True)
    # posts = relationship("Post", secondary=posts_tags, back_populates="tags")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True)
    comment = Column(String)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"))
    post = relationship("Post", backref="comments")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)


class Roles(enum.Enum):
    admin: str = "admin"
    moderator: str = "moderator"
    user: str = "user"
