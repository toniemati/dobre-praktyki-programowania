from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from starlette.requests import Request
from pandas import read_csv
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.sql import text
from datetime import timedelta

from models.base import Base
from models.link import Link
from models.movie import Movie
from models.rating import Rating
from models.tag import Tag
from models.user import User
from schemas import (
    MovieSchema, LinkSchema, RatingSchema, TagSchema,
    LoginSchema, UserSchema, UserDetailSchema
)
from auth import (
    hash_password, verify_password, create_access_token, verify_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

engine = create_engine("sqlite:///example.db", echo=True)

Base.metadata.create_all(engine)

SessionLocal = sessionmaker(bind=engine)


app = FastAPI()
security = HTTPBearer()


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Dependency to verify JWT token
async def get_current_user(request: Request) -> dict:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing or invalid authorization header",
        )
    
    token = auth_header.split(" ")[1]
    try:
        payload = verify_token(token)
        return payload
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


# Dependency to check for ROLE_ADMIN
async def get_admin_user(current_user: dict = Depends(get_current_user)) -> dict:
    roles = current_user.get("roles", [])
    if "ROLE_ADMIN" not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource"
        )
    return current_user


@app.get("/")
def read_root():
    return {"hello": "world"}


# ! AUTH ENDPOINTS

@app.post("/login")
def login(login_data: LoginSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == login_data.username).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    if not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.username,
            "user_id": user.id,
            "email": user.email,
            "roles": user.roles
        },
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/users")
def create_user(user_data: UserSchema, admin_user: dict = Depends(get_admin_user), db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this username or email already exists"
        )
    
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        roles=user_data.roles
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return {
        "id": db_user.id,
        "username": db_user.username,
        "email": db_user.email,
        "roles": db_user.roles
    }


@app.get("/users")
def get_all_users(admin_user: dict = Depends(get_admin_user), db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "roles": user.roles
        }
        for user in users
    ]


@app.get("/user_details")
def get_user_details(current_user: dict = Depends(get_current_user)):
    return {
        "user_id": current_user.get("user_id"),
        "username": current_user.get("sub"),
        "email": current_user.get("email"),
        "roles": current_user.get("roles", [])
    }


# ! MOVIES


@app.get('/movies')
def read_movies(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    movies = db.query(Movie).order_by(desc(Movie.id)).all()
    return movies


@app.post('/movies')
def store_movie(movie: MovieSchema, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    db_movie = Movie(id=movie.id, title=movie.title, genres=movie.genres)
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie


@app.get('/movies/{movie_id}')
def read_movie(movie_id: int, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        return {"error": "Movie not found"}
    return movie


@app.put('/movies/{movie_id}')
def update_movie(movie_id: int, movie_data: MovieSchema, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        return {"error": "Movie not found"}

    movie.title = movie_data.title
    movie.genres = movie_data.genres
    db.commit()
    db.refresh(movie)
    return movie


@app.delete('/movies/{movie_id}')
def destroy_movie(movie_id: int, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        return {"error": "Movie not found"}
    db.delete(movie)
    db.commit()
    return {"message": "Movie deleted successfully"}


# ! LINKS

@app.get('/links')
def read_links(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    links = db.query(Link).order_by(desc(Link.id)).all()
    return links


@app.post('/links')
def store_link(link: LinkSchema, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    db_link = Link(id=link.id, imdbId=link.imdbId, tmdbId=link.tmdbId)
    db.add(db_link)
    db.commit()
    db.refresh(db_link)
    return db_link


@app.get('/links/{link_id}')
def read_link(link_id: int, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    link = db.query(Link).filter(Link.id == link_id).first()
    if not link:
        return {"error": "Link not found"}
    return link


@app.put('/links/{link_id}')
def update_link(link_id: int, link_data: LinkSchema, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    link = db.query(Link).filter(Link.id == link_id).first()
    if not link:
        return {"error": "Link not found"}

    link.imdbId = link_data.imdbId
    link.tmdbId = link_data.tmdbId
    db.commit()
    db.refresh(link)
    return link


@app.delete('/links/{link_id}')
def destroy_link(link_id: int, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    link = db.query(Link).filter(Link.id == link_id).first()
    if not link:
        return {"error": "Link not found"}
    db.delete(link)
    db.commit()
    return {"message": "Link deleted successfully"}


# ! RATINGS

@app.get('/ratings')
def read_ratings(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    ratings = db.query(Rating).order_by(desc(Rating.id)).all()
    return ratings


@app.post('/ratings')
def store_rating(rating: RatingSchema, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    db_rating = Rating(userId=rating.userId, movieId=rating.movieId, rating=rating.rating, timestamp=rating.timestamp)
    db.add(db_rating)
    db.commit()
    db.refresh(db_rating)
    return db_rating


@app.get('/ratings/{rating_id}')
def read_rating(rating_id: int, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    rating = db.query(Rating).filter(Rating.id == rating_id).first()
    if not rating:
        return {"error": "Rating not found"}
    return rating


@app.put('/ratings/{rating_id}')
def update_rating(rating_id: int, rating_data: RatingSchema, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    rating = db.query(Rating).filter(Rating.id == rating_id).first()
    if not rating:
        return {"error": "Rating not found"}

    rating.userId = rating_data.userId
    rating.movieId = rating_data.movieId
    rating.rating = rating_data.rating
    rating.timestamp = rating_data.timestamp
    db.commit()
    db.refresh(rating)
    return rating


@app.delete('/ratings/{rating_id}')
def destroy_rating(rating_id: int, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    rating = db.query(Rating).filter(Rating.id == rating_id).first()
    if not rating:
        return {"error": "Rating not found"}
    db.delete(rating)
    db.commit()
    return {"message": "Rating deleted successfully"}


# ! TAGS

@app.get('/tags')
def read_tags(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    tags = db.query(Tag).order_by(desc(Tag.id)).all()
    return tags


@app.post('/tags')
def store_tag(tag: TagSchema, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    db_tag = Tag(userId=tag.userId, movieId=tag.movieId, tag=tag.tag, timestamp=tag.timestamp)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag


@app.get('/tags/{tag_id}')
def read_tag(tag_id: int, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        return {"error": "Tag not found"}
    return tag


@app.put('/tags/{tag_id}')
def update_tag(tag_id: int, tag_data: TagSchema, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        return {"error": "Tag not found"}

    tag.userId = tag_data.userId
    tag.movieId = tag_data.movieId
    tag.tag = tag_data.tag
    tag.timestamp = tag_data.timestamp
    db.commit()
    db.refresh(tag)
    return tag


@app.delete('/tags/{tag_id}')
def destroy_tag(tag_id: int, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        return {"error": "Tag not found"}
    db.delete(tag)
    db.commit()
    return {"message": "Tag deleted successfully"}
