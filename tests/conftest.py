import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import os

from models.base import Base
from models.movie import Movie
from models.link import Link
from models.rating import Rating
from models.tag import Tag
from main import app
import main


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test using a file-based database."""
    # Clean up any existing test database
    if os.path.exists("test.db"):
        os.remove("test.db")
    
    engine = create_engine("sqlite:///test.db")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Replace the global session in main module
    original_session = main.session
    main.session = session
    
    yield session
    
    session.close()
    engine.dispose()
    
    # Restore original session
    main.session = original_session
    
    # Clean up test database
    if os.path.exists("test.db"):
        os.remove("test.db")


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with a fresh database."""
    return TestClient(app)


@pytest.fixture
def movie_fixtures(db_session):
    """Create test movie fixtures."""
    movies = [
        Movie(id=1, title="The Shawshank Redemption", genres="Drama"),
        Movie(id=2, title="The Dark Knight", genres="Action|Crime|Drama"),
        Movie(id=3, title="Inception", genres="Action|Sci-Fi|Thriller"),
    ]
    db_session.add_all(movies)
    db_session.commit()
    return movies


@pytest.fixture
def link_fixtures(db_session):
    """Create test link fixtures."""
    links = [
        Link(id=1, imdbId=111161, tmdbId=278),
        Link(id=2, imdbId=468569, tmdbId=155),
        Link(id=3, imdbId=1375666, tmdbId=27205),
    ]
    db_session.add_all(links)
    db_session.commit()
    return links


@pytest.fixture
def rating_fixtures(db_session):
    """Create test rating fixtures."""
    ratings = [
        Rating(userId=1, movieId=1, rating=5.0, timestamp=1000000000),
        Rating(userId=2, movieId=1, rating=4.5, timestamp=1000000001),
        Rating(userId=1, movieId=2, rating=4.0, timestamp=1000000002),
    ]
    db_session.add_all(ratings)
    db_session.commit()
    return ratings


@pytest.fixture
def tag_fixtures(db_session):
    """Create test tag fixtures."""
    tags = [
        Tag(userId=1, movieId=1, tag="masterpiece", timestamp=1000000000),
        Tag(userId=2, movieId=1, tag="excellent", timestamp=1000000001),
        Tag(userId=1, movieId=2, tag="superhero", timestamp=1000000002),
    ]
    db_session.add_all(tags)
    db_session.commit()
    return tags
