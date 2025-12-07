from fastapi import FastAPI
from pandas import read_csv
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql import text

from models.base import Base
from models.link import Link
from models.movie import Movie
from models.rating import Rating
from models.tag import Tag
from schemas import MovieSchema, LinkSchema, RatingSchema, TagSchema

engine = create_engine("sqlite:///example.db", echo=True)

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

app = FastAPI()


@app.get("/")
def read_root():
    return {"hello": "world"}

# ! MOVIES


@app.get('/movies')
def read_movies():
    movies = session.query(Movie).order_by(desc(Movie.id)).all()

    return movies


@app.post('/movies')
def store_movie(movie: MovieSchema):
    db_movie = Movie(id=movie.id, title=movie.title, genres=movie.genres)
    session.add(db_movie)
    session.commit()
    session.refresh(db_movie)

    return db_movie


@app.get('/movies/{movie_id}')
def read_movie(movie_id: int):
    movie = session.query(Movie).filter(Movie.id == movie_id).first()

    if not movie:
        return {"error": "Movie not found"}

    return movie

@app.put('/movies/{movie_id}')
def update_movie(movie_id: int, movie_data: MovieSchema):
    movie = session.query(Movie).filter(Movie.id == movie_id).first()

    if not movie:
        return {"error": "Movie not found"}

    movie.title = movie_data.title
    movie.genres = movie_data.genres
    session.commit()
    session.refresh(movie)

    return movie
    return movie


@app.delete('/movies/{movie_id}')
def destroy_movie(movie_id: int):
    movie = session.query(Movie).filter(Movie.id == movie_id).first()

    if not movie:
        return {"error": "Movie not found"}
    session.delete(movie)
    session.commit()

    return {"message": "Movie deleted successfully"}


# ! LINKS

@app.get('/links')
def read_links():
    links = session.query(Link).order_by(desc(Link.id)).all()

    return links


@app.post('/links')
def store_link(link: LinkSchema):
    db_link = Link(id=link.id, imdbId=link.imdbId, tmdbId=link.tmdbId)
    session.add(db_link)
    session.commit()
    session.refresh(db_link)

    return db_link


@app.get('/links/{link_id}')
def read_link(link_id: int):
    link = session.query(Link).filter(Link.id == link_id).first()

    if not link:
        return {"error": "Link not found"}

    return link

@app.put('/links/{link_id}')
def update_link(link_id: int, link_data: LinkSchema):
    link = session.query(Link).filter(Link.id == link_id).first()

    if not link:
        return {"error": "Link not found"}

    link.imdbId = link_data.imdbId
    link.tmdbId = link_data.tmdbId
    session.commit()
    session.refresh(link)

    return link
    return link


@app.delete('/links/{link_id}')
def destroy_link(link_id: int):
    link = session.query(Link).filter(Link.id == link_id).first()

    if not link:
        return {"error": "Link not found"}
    session.delete(link)
    session.commit()

    return {"message": "Link deleted successfully"}


# ! RATINGS

@app.get('/ratings')
def read_ratings():
    ratings = session.query(Rating).order_by(desc(Rating.id)).all()

    return ratings


@app.post('/ratings')
def store_rating(rating: RatingSchema):
    db_rating = Rating(userId=rating.userId, movieId=rating.movieId, rating=rating.rating, timestamp=rating.timestamp)
    session.add(db_rating)
    session.commit()
    session.refresh(db_rating)

    return db_rating


@app.get('/ratings/{rating_id}')
def read_rating(rating_id: int):
    rating = session.query(Rating).filter(Rating.id == rating_id).first()

    if not rating:
        return {"error": "Rating not found"}

    return rating


@app.put('/ratings/{rating_id}')
def update_rating(rating_id: int, rating_data: RatingSchema):
    rating = session.query(Rating).filter(Rating.id == rating_id).first()

    if not rating:
        return {"error": "Rating not found"}

    rating.userId = rating_data.userId
    rating.movieId = rating_data.movieId
    rating.rating = rating_data.rating
    rating.timestamp = rating_data.timestamp
    session.commit()
    session.refresh(rating)

    return rating


@app.delete('/ratings/{rating_id}')
def destroy_rating(rating_id: int):
    rating = session.query(Rating).filter(Rating.id == rating_id).first()

    if not rating:
        return {"error": "Rating not found"}
    session.delete(rating)
    session.commit()

    return {"message": "Rating deleted successfully"}


# ! TAGS

@app.get('/tags')
def read_tags():
    tags = session.query(Tag).order_by(desc(Tag.id)).all()

    return tags


@app.post('/tags')
def store_tag(tag: TagSchema):
    db_tag = Tag(userId=tag.userId, movieId=tag.movieId, tag=tag.tag, timestamp=tag.timestamp)
    session.add(db_tag)
    session.commit()
    session.refresh(db_tag)
    return db_tag


@app.get('/tags/{tag_id}')
def read_tag(tag_id: int):
    tag = session.query(Tag).filter(Tag.id == tag_id).first()

    if not tag:
        return {"error": "Tag not found"}

    return tag

@app.put('/tags/{tag_id}')
def update_tag(tag_id: int, tag_data: TagSchema):
    tag = session.query(Tag).filter(Tag.id == tag_id).first()

    if not tag:
        return {"error": "Tag not found"}

    tag.userId = tag_data.userId
    tag.movieId = tag_data.movieId
    tag.tag = tag_data.tag
    tag.timestamp = tag_data.timestamp
    session.commit()
    session.refresh(tag)

    return tag
    return tag


@app.delete('/tags/{tag_id}')
def destroy_tag(tag_id: int):
    tag = session.query(Tag).filter(Tag.id == tag_id).first()

    if not tag:
        return {"error": "Tag not found"}
    session.delete(tag)
    session.commit()

    return {"message": "Tag deleted successfully"}


# ! adding into db
# data = []

# for row in file.itertuples(index=False):
#     d = Tag(row.userId, row.movieId, row.tag, row.timestamp)
#     data.append(d)

# session.add_all(data)
# session.commit()

# return {"msg": "added", "len": len(data)}
