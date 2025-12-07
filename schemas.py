from pydantic import BaseModel, ConfigDict
from typing import List


class LoginSchema(BaseModel):
    username: str
    password: str


class UserSchema(BaseModel):
    username: str
    email: str
    password: str
    roles: List[str] = ["ROLE_USER"]


class UserDetailSchema(BaseModel):
    id: int
    username: str
    email: str
    roles: List[str]

    model_config = ConfigDict(from_attributes=True)


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
