from models.movie import Movie


class TestMovieGetAll:
    def test_read_movies_returns_all_movies(self, client, movie_fixtures):
        response = client.get("/movies")

        assert response.status_code == 200
        assert len(response.json()) == 3
        assert response.json()[0]["title"] in [
            "The Shawshank Redemption",
            "The Dark Knight",
            "Inception"
        ]

    def test_read_movies_returns_correct_count(self, client, movie_fixtures):
        response = client.get("/movies")
        movies = response.json()

        assert response.status_code == 200
        assert len(movies) == len(movie_fixtures)

    def test_read_movies_empty_database(self, client):
        response = client.get("/movies")

        assert response.status_code == 200
        assert response.json() == []


class TestMovieGetById:
    def test_read_movie_returns_correct_movie(self, client, movie_fixtures):
        response = client.get("/movies/1")
        movie = response.json()

        assert response.status_code == 200
        assert movie["id"] == 1
        assert movie["title"] == "The Shawshank Redemption"
        assert movie["genres"] == "Drama"

    def test_read_movie_with_different_ids(self, client, movie_fixtures):
        response1 = client.get("/movies/1")
        response2 = client.get("/movies/2")

        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response1.json()["title"] != response2.json()["title"]

    def test_read_movie_not_found(self, client, movie_fixtures):
        response = client.get("/movies/999")

        assert response.status_code == 200
        assert "error" in response.json()
        assert response.json()["error"] == "Movie not found"

    def test_read_movie_returns_expected_fields(self, client, movie_fixtures):
        response = client.get("/movies/1")
        movie = response.json()

        assert response.status_code == 200
        assert "id" in movie
        assert "title" in movie
        assert "genres" in movie


class TestMovieCreate:
    def test_store_movie_creates_new_movie(self, client, db_session):
        movie_data = {
            "id": 10,
            "title": "The Matrix",
            "genres": "Action|Sci-Fi"
        }
        response = client.post("/movies", json=movie_data)

        assert response.status_code == 200
        created_movie = response.json()
        assert created_movie["title"] == "The Matrix"
        assert created_movie["genres"] == "Action|Sci-Fi"

        # Verify in database
        db_movie = db_session.query(Movie).filter(Movie.id == 10).first()
        assert db_movie is not None
        assert db_movie.title == "The Matrix"

    def test_store_movie_returns_created_object(self, client):
        movie_data = {
            "id": 20,
            "title": "Pulp Fiction",
            "genres": "Crime|Drama"
        }
        response = client.post("/movies", json=movie_data)

        assert response.status_code == 200
        movie = response.json()
        assert movie["id"] == 20
        assert movie["title"] == "Pulp Fiction"

    def test_store_movie_increases_database_count(self, client, movie_fixtures, db_session):
        initial_count = db_session.query(Movie).count()

        movie_data = {
            "id": 30,
            "title": "Forrest Gump",
            "genres": "Drama|Romance"
        }
        client.post("/movies", json=movie_data)

        final_count = db_session.query(Movie).count()
        assert final_count == initial_count + 1


class TestMovieUpdate:
    def test_update_movie_modifies_existing_movie(self, client, movie_fixtures, db_session):
        updated_data = {
            "id": 1,
            "title": "The Shawshank Redemption - Updated",
            "genres": "Drama|Crime"
        }
        response = client.put("/movies/1", json=updated_data)

        assert response.status_code == 200
        movie = response.json()
        assert movie["title"] == "The Shawshank Redemption - Updated"
        assert movie["genres"] == "Drama|Crime"

        # Verify in database
        db_movie = db_session.query(Movie).filter(Movie.id == 1).first()
        assert db_movie.title == "The Shawshank Redemption - Updated"

    def test_update_movie_preserves_id(self, client, movie_fixtures, db_session):
        updated_data = {
            "id": 1,
            "title": "Updated Title",
            "genres": "Drama"
        }
        response = client.put("/movies/1", json=updated_data)
        movie = response.json()

        assert movie["id"] == 1

    def test_update_movie_not_found(self, client, movie_fixtures):
        updated_data = {
            "id": 999,
            "title": "Non-existent Movie",
            "genres": "Drama"
        }
        response = client.put("/movies/999", json=updated_data)

        assert response.status_code == 200
        assert "error" in response.json()
        assert response.json()["error"] == "Movie not found"

    def test_update_only_title(self, client, movie_fixtures, db_session):
        updated_data = {
            "id": 2,
            "title": "The Dark Knight - New Title",
            "genres": "Action|Crime|Drama"
        }
        response = client.put("/movies/2", json=updated_data)

        assert response.status_code == 200
        db_movie = db_session.query(Movie).filter(Movie.id == 2).first()
        assert db_movie.title == "The Dark Knight - New Title"


class TestMovieDelete:
    def test_delete_movie_removes_from_database(self, client, movie_fixtures, db_session):
        """Verify DELETE /movies/{movie_id} removes movie from database."""
        response = client.delete("/movies/1")

        assert response.status_code == 200
        assert "message" in response.json()

        # Verify deleted from database
        deleted_movie = db_session.query(Movie).filter(Movie.id == 1).first()
        assert deleted_movie is None

    def test_delete_movie_decreases_count(self, client, movie_fixtures, db_session):
        initial_count = db_session.query(Movie).count()

        client.delete("/movies/1")

        final_count = db_session.query(Movie).count()
        assert final_count == initial_count - 1

    def test_delete_movie_not_found(self, client, movie_fixtures):
        response = client.delete("/movies/999")

        assert response.status_code == 200
        assert "error" in response.json()
        assert response.json()["error"] == "Movie not found"

    def test_delete_movie_returns_success_message(self, client, movie_fixtures):
        response = client.delete("/movies/1")

        assert response.status_code == 200
        assert response.json()["message"] == "Movie deleted successfully"

    def test_delete_different_movies(self, client, movie_fixtures, db_session):
        client.delete("/movies/1")
        client.delete("/movies/2")

        count = db_session.query(Movie).count()
        assert count == 1
