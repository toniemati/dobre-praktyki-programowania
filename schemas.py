from pydantic import BaseModel


class MovieSchema(BaseModel):
    id: int
    title: str
    genres: str


class LinkSchema(BaseModel):
    id: int
    imdbId: int
    tmdbId: int


class RatingSchema(BaseModel):
    userId: int
    movieId: int
    rating: float
    timestamp: int


class TagSchema(BaseModel):
    userId: int
    movieId: int
    tag: str
    timestamp: int
