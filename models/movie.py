from sqlalchemy import Column, Integer, String

from .base import Base


class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    genres = Column(String)

    def __init__(self, id: int, title: str, genres: str):
        self.id = id
        self.title = title
        self.genres = genres

    def to_dict(self):
        return {
            "movieId": self.id,
            "title": self.title,
            "genres": self.genres,
        }
