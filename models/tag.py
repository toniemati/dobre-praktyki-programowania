from sqlalchemy import Column, Integer, String

from .base import Base


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    userId = Column(Integer)
    movieId = Column(Integer)
    tag = Column(String)
    timestamp = Column(Integer)

    def __init__(self, userId: int, movieId: int, tag: str, timestamp: int):
        self.userId = userId
        self.movieId = movieId
        self.tag = tag
        self.timestamp = timestamp

    def to_dict(self):
        return {
            "userId": self.userId,
            "movieId": self.movieId,
            "tag": self.tag,
            "timestamp": self.timestamp,
        }
