from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey

from src.database.db import Base

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
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", backref="posts")
