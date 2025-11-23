from sqlalchemy import Column, Integer

from .base import Base


class Link(Base):
    __tablename__ = "links"

    id = Column(Integer, primary_key=True)
    imdbId = Column(Integer)
    tmdbId = Column(Integer)

    def __init__(self, id: int, imdbId: int, tmdbId: int):
        self.id = id
        self.imdbId = imdbId
        self.tmdbId = tmdbId

    def to_dict(self):
        return {
            "id": self.id,
            "imdbId": self.imdbId,
            "tmdbId": self.tmdbId,
        }
