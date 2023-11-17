import enum 

from sqlalchemy import Column, Integer, Enum
from sqlalchemy.sql.schema import ForeignKey

from src.database.db import Base
from src.database.models.users import User
# import Post model


# Delete this model
class Post(Base):
    __tablename__ = 'post'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(User.id, ondelete="CASCADE"))



class RatingTypes(enum.Enum):
    LIKE ='LIKE'
    DISLIKE='DISLIKE'


class Rating(Base):
    __tablename__ = 'rating'
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey(Post.id, ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey(User.id, ondelete="CASCADE"))
    type = Column(Enum(RatingTypes))

   
