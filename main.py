from sqlalchemy.orm import declarative_base, sessionmaker
from fastapi import FastAPI
from pandas import read_csv
from sqlalchemy import create_engine

from models.link import Link
from models.movie import Movie
from models.rating import Rating
from models.tag import Tag
from models.base import Base

engine = create_engine("sqlite:///example.db", echo=True)

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

app = FastAPI()


@app.get("/")
def read_root():
    return {"hello": "world"}


@app.get('/movies')
def read_movies():
    movies = session.query(Movie).all()

    # return len(movies)
    return movies


@app.get('/links')
def read_links():
    links = session.query(Link).all()

    # return len(links)
    return links


@app.get('/ratings')
def read_ratings():
    ratings = session.query(Rating).all()

    # return len(ratings)
    return ratings


@app.get('/tags')
def read_tags():
    tags = session.query(Tag).all()

    # return len(tags)
    return tags





# ! adding into db
# data = []

# for row in file.itertuples(index=False):
#     d = Tag(row.userId, row.movieId, row.tag, row.timestamp)
#     data.append(d)

# session.add_all(data)
# session.commit()

# return {"msg": "added", "len": len(data)}
