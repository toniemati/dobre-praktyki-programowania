from fastapi import FastAPI
from pandas import read_csv

from models.link import Link
from models.movie import Movie
from models.rating import Rating
from models.tag import Tag

app = FastAPI()


@app.get("/")
def read_root():
    return {"hello": "world"}


@app.get('/movies')
def read_movies():
    file = read_csv('./database/movies.csv')

    movies = []

    for row in file.itertuples(index=False):
        m = Movie(row.movieId, row.title, row.genres)

        movies.append(m.__dict__())

    return movies[0:10]
    return movies


@app.get('/links')
def read_links():
    file = read_csv('./database/links.csv')

    links = []

    for row in file.itertuples(index=False):
        l = Link(row.movieId, row.imdbId, row.tmdbId)

        links.append(l.__dict__())

    return links[0:10]
    return links


@app.get('/ratings')
def read_ratings():
    file = read_csv('./database/ratings.csv')

    ratings = []

    for row in file.itertuples(index=False):
        r = Rating(row.userId, row.movieId, row.rating, row.timestamp)

        ratings.append(r.__dict__())

    return ratings[0:10]
    return ratings


@app.get('/tags')
def read_tags():
    file = read_csv('./database/tags.csv')

    tags = []

    for row in file.itertuples(index=False):
        t = Tag(row.userId, row.movieId, row.tag, row.timestamp)

        tags.append(t.__dict__())

    return tags[0:10]
    return tags
