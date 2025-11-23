from sqlalchemy import Column, Float, Integer

from .base import Base


class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    userId = Column(Integer)
    movieId = Column(Integer)
    rating = Column(Float)
    timestamp = Column(Integer)

    def __init__(self, userId: int, movieId: int, rating: float, timestamp: int):
        self.userId = userId
        self.movieId = movieId
        self.rating = rating
        self.timestamp = timestamp

    def to_dict(self):
        return {
            "userId": self.userId,
            "movieId": self.movieId,
            "rating": self.rating,
            "timestamp": self.timestamp,
        }
