from sqlalchemy import Column, Integer

from src.database.db import Base


class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
