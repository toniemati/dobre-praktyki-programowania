from models.rating import Rating


class TestRatingGetAll:
    def test_read_ratings_returns_all_ratings(self, client, rating_fixtures):
        response = client.get("/ratings")

        assert response.status_code == 200
        assert len(response.json()) == 3

    def test_read_ratings_returns_correct_count(self, client, rating_fixtures):
        response = client.get("/ratings")
        ratings = response.json()

        assert response.status_code == 200
        assert len(ratings) == len(rating_fixtures)

    def test_read_ratings_contains_rating_values(self, client, rating_fixtures):
        response = client.get("/ratings")
        ratings = response.json()

        assert response.status_code == 200
        rating_values = [r["rating"] for r in ratings]
        assert 5.0 in rating_values
        assert 4.5 in rating_values

    def test_read_ratings_empty_database(self, client):
        response = client.get("/ratings")

        assert response.status_code == 200
        assert response.json() == []


class TestRatingGetById:
    def test_read_rating_returns_correct_rating(self, client, rating_fixtures, db_session):
        # Get the ID of the first rating
        rating_id = rating_fixtures[0].id
        response = client.get(f"/ratings/{rating_id}")
        rating = response.json()

        assert response.status_code == 200
        assert rating["userId"] == 1
        assert rating["movieId"] == 1
        assert rating["rating"] == 5.0

    def test_read_rating_with_different_ids(self, client, rating_fixtures):
        rating_id1 = rating_fixtures[0].id
        rating_id2 = rating_fixtures[1].id

        response1 = client.get(f"/ratings/{rating_id1}")
        response2 = client.get(f"/ratings/{rating_id2}")

        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response1.json()["rating"] != response2.json()["rating"]

    def test_read_rating_not_found(self, client, rating_fixtures):
        response = client.get("/ratings/999")

        assert response.status_code == 200
        assert "error" in response.json()
        assert response.json()["error"] == "Rating not found"

    def test_read_rating_returns_all_fields(self, client, rating_fixtures):
        rating_id = rating_fixtures[0].id
        response = client.get(f"/ratings/{rating_id}")
        rating = response.json()

        assert response.status_code == 200
        assert "userId" in rating
        assert "movieId" in rating
        assert "rating" in rating
        assert "timestamp" in rating


class TestRatingCreate:
    def test_store_rating_creates_new_rating(self, client, db_session):
        rating_data = {
            "userId": 10,
            "movieId": 10,
            "rating": 4.5,
            "timestamp": 2000000000
        }
        response = client.post("/ratings", json=rating_data)

        assert response.status_code == 200
        created_rating = response.json()
        assert created_rating["userId"] == 10
        assert created_rating["rating"] == 4.5

        # Verify in database
        db_rating = db_session.query(Rating).filter(
            Rating.userId == 10,
            Rating.movieId == 10
        ).first()
        assert db_rating is not None
        assert db_rating.rating == 4.5

    def test_store_rating_returns_created_object(self, client):
        rating_data = {
            "userId": 20,
            "movieId": 20,
            "rating": 3.5,
            "timestamp": 2000000001
        }
        response = client.post("/ratings", json=rating_data)

        assert response.status_code == 200
        rating = response.json()
        assert rating["userId"] == 20
        assert rating["movieId"] == 20
        assert rating["rating"] == 3.5

    def test_store_rating_increases_database_count(self, client, rating_fixtures, db_session):
        initial_count = db_session.query(Rating).count()

        rating_data = {
            "userId": 30,
            "movieId": 30,
            "rating": 2.0,
            "timestamp": 2000000002
        }
        client.post("/ratings", json=rating_data)

        final_count = db_session.query(Rating).count()
        assert final_count == initial_count + 1


class TestRatingUpdate:
    def test_update_rating_modifies_existing_rating(self, client, rating_fixtures, db_session):
        rating_id = rating_fixtures[0].id
        updated_data = {
            "userId": 1,
            "movieId": 1,
            "rating": 3.5,
            "timestamp": 1000000000
        }
        response = client.put(f"/ratings/{rating_id}", json=updated_data)

        assert response.status_code == 200
        rating = response.json()
        assert rating["rating"] == 3.5

        # Verify in database
        db_rating = db_session.query(Rating).filter(
            Rating.id == rating_id).first()
        assert db_rating.rating == 3.5

    def test_update_rating_preserves_user_id(self, client, rating_fixtures, db_session):
        rating_id = rating_fixtures[1].id
        updated_data = {
            "userId": 2,
            "movieId": 1,
            "rating": 2.0,
            "timestamp": 1000000001
        }
        response = client.put(f"/ratings/{rating_id}", json=updated_data)
        rating = response.json()

        assert rating["userId"] == 2

    def test_update_rating_not_found(self, client, rating_fixtures):
        updated_data = {
            "userId": 999,
            "movieId": 999,
            "rating": 1.0,
            "timestamp": 2000000000
        }
        response = client.put("/ratings/999", json=updated_data)

        assert response.status_code == 200
        assert "error" in response.json()
        assert response.json()["error"] == "Rating not found"

    def test_update_rating_value_only(self, client, rating_fixtures, db_session):
        rating_id = rating_fixtures[2].id
        updated_data = {
            "userId": 1,
            "movieId": 2,
            "rating": 5.0,
            "timestamp": 1000000002
        }
        response = client.put(f"/ratings/{rating_id}", json=updated_data)

        assert response.status_code == 200
        db_rating = db_session.query(Rating).filter(
            Rating.id == rating_id).first()
        assert db_rating.rating == 5.0


class TestRatingDelete:
    def test_delete_rating_removes_from_database(self, client, rating_fixtures, db_session):
        rating_id = rating_fixtures[0].id
        response = client.delete(f"/ratings/{rating_id}")

        assert response.status_code == 200
        assert "message" in response.json()

        # Verify deleted from database
        deleted_rating = db_session.query(Rating).filter(
            Rating.id == rating_id).first()
        assert deleted_rating is None

    def test_delete_rating_decreases_count(self, client, rating_fixtures, db_session):
        initial_count = db_session.query(Rating).count()
        rating_id = rating_fixtures[0].id

        client.delete(f"/ratings/{rating_id}")

        final_count = db_session.query(Rating).count()
        assert final_count == initial_count - 1

    def test_delete_rating_not_found(self, client, rating_fixtures):
        response = client.delete("/ratings/999")

        assert response.status_code == 200
        assert "error" in response.json()
        assert response.json()["error"] == "Rating not found"

    def test_delete_rating_returns_success_message(self, client, rating_fixtures):
        rating_id = rating_fixtures[0].id
        response = client.delete(f"/ratings/{rating_id}")

        assert response.status_code == 200
        assert response.json()["message"] == "Rating deleted successfully"

    def test_delete_multiple_ratings(self, client, rating_fixtures, db_session):
        rating_id1 = rating_fixtures[0].id
        rating_id2 = rating_fixtures[1].id

        client.delete(f"/ratings/{rating_id1}")
        client.delete(f"/ratings/{rating_id2}")

        count = db_session.query(Rating).count()
        assert count == 1
