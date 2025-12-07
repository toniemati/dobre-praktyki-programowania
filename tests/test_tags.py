from models.tag import Tag


class TestTagGetAll:
    def test_read_tags_returns_all_tags(self, client, tag_fixtures):
        response = client.get("/tags")

        assert response.status_code == 200
        assert len(response.json()) == 3

    def test_read_tags_returns_correct_count(self, client, tag_fixtures):
        response = client.get("/tags")
        tags = response.json()

        assert response.status_code == 200
        assert len(tags) == len(tag_fixtures)

    def test_read_tags_contains_tag_text(self, client, tag_fixtures):
        response = client.get("/tags")
        tags = response.json()

        assert response.status_code == 200
        tag_texts = [t["tag"] for t in tags]
        assert "masterpiece" in tag_texts
        assert "excellent" in tag_texts
        assert "superhero" in tag_texts

    def test_read_tags_empty_database(self, client):
        response = client.get("/tags")

        assert response.status_code == 200
        assert response.json() == []


class TestTagGetById:
    def test_read_tag_returns_correct_tag(self, client, tag_fixtures, db_session):
        # Get the ID of the first tag
        tag_id = tag_fixtures[0].id
        response = client.get(f"/tags/{tag_id}")
        tag = response.json()

        assert response.status_code == 200
        assert tag["userId"] == 1
        assert tag["movieId"] == 1
        assert tag["tag"] == "masterpiece"

    def test_read_tag_with_different_ids(self, client, tag_fixtures):
        tag_id1 = tag_fixtures[0].id
        tag_id2 = tag_fixtures[1].id

        response1 = client.get(f"/tags/{tag_id1}")
        response2 = client.get(f"/tags/{tag_id2}")

        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response1.json()["tag"] != response2.json()["tag"]

    def test_read_tag_not_found(self, client, tag_fixtures):
        response = client.get("/tags/999")

        assert response.status_code == 200
        assert "error" in response.json()
        assert response.json()["error"] == "Tag not found"

    def test_read_tag_returns_all_fields(self, client, tag_fixtures):
        tag_id = tag_fixtures[0].id
        response = client.get(f"/tags/{tag_id}")
        tag = response.json()

        assert response.status_code == 200
        assert "userId" in tag
        assert "movieId" in tag
        assert "tag" in tag
        assert "timestamp" in tag


class TestTagCreate:
    def test_store_tag_creates_new_tag(self, client, db_session):
        tag_data = {
            "userId": 10,
            "movieId": 10,
            "tag": "awesome",
            "timestamp": 2000000000
        }
        response = client.post("/tags", json=tag_data)

        assert response.status_code == 200
        created_tag = response.json()
        assert created_tag["userId"] == 10
        assert created_tag["tag"] == "awesome"

        # Verify in database
        db_tag = db_session.query(Tag).filter(
            Tag.userId == 10,
            Tag.movieId == 10
        ).first()
        assert db_tag is not None
        assert db_tag.tag == "awesome"

    def test_store_tag_returns_created_object(self, client):
        tag_data = {
            "userId": 20,
            "movieId": 20,
            "tag": "thrilling",
            "timestamp": 2000000001
        }
        response = client.post("/tags", json=tag_data)

        assert response.status_code == 200
        tag = response.json()
        assert tag["userId"] == 20
        assert tag["movieId"] == 20
        assert tag["tag"] == "thrilling"

    def test_store_tag_increases_database_count(self, client, tag_fixtures, db_session):
        initial_count = db_session.query(Tag).count()

        tag_data = {
            "userId": 30,
            "movieId": 30,
            "tag": "intense",
            "timestamp": 2000000002
        }
        client.post("/tags", json=tag_data)

        final_count = db_session.query(Tag).count()
        assert final_count == initial_count + 1


class TestTagUpdate:
    def test_update_tag_modifies_existing_tag(self, client, tag_fixtures, db_session):
        tag_id = tag_fixtures[0].id
        updated_data = {
            "userId": 1,
            "movieId": 1,
            "tag": "phenomenal",
            "timestamp": 1000000000
        }
        response = client.put(f"/tags/{tag_id}", json=updated_data)

        assert response.status_code == 200
        tag = response.json()
        assert tag["tag"] == "phenomenal"

        # Verify in database
        db_tag = db_session.query(Tag).filter(Tag.id == tag_id).first()
        assert db_tag.tag == "phenomenal"

    def test_update_tag_preserves_user_id(self, client, tag_fixtures, db_session):
        tag_id = tag_fixtures[1].id
        updated_data = {
            "userId": 2,
            "movieId": 1,
            "tag": "incredible",
            "timestamp": 1000000001
        }
        response = client.put(f"/tags/{tag_id}", json=updated_data)
        tag = response.json()

        assert tag["userId"] == 2

    def test_update_tag_not_found(self, client, tag_fixtures):
        updated_data = {
            "userId": 999,
            "movieId": 999,
            "tag": "nonexistent",
            "timestamp": 2000000000
        }
        response = client.put("/tags/999", json=updated_data)

        assert response.status_code == 200
        assert "error" in response.json()
        assert response.json()["error"] == "Tag not found"

    def test_update_tag_text_only(self, client, tag_fixtures, db_session):
        tag_id = tag_fixtures[2].id
        updated_data = {
            "userId": 1,
            "movieId": 2,
            "tag": "blockbuster",
            "timestamp": 1000000002
        }
        response = client.put(f"/tags/{tag_id}", json=updated_data)

        assert response.status_code == 200
        db_tag = db_session.query(Tag).filter(Tag.id == tag_id).first()
        assert db_tag.tag == "blockbuster"


class TestTagDelete:
    def test_delete_tag_removes_from_database(self, client, tag_fixtures, db_session):
        tag_id = tag_fixtures[0].id
        response = client.delete(f"/tags/{tag_id}")

        assert response.status_code == 200
        assert "message" in response.json()

        # Verify deleted from database
        deleted_tag = db_session.query(Tag).filter(Tag.id == tag_id).first()
        assert deleted_tag is None

    def test_delete_tag_decreases_count(self, client, tag_fixtures, db_session):
        initial_count = db_session.query(Tag).count()
        tag_id = tag_fixtures[0].id

        client.delete(f"/tags/{tag_id}")

        final_count = db_session.query(Tag).count()
        assert final_count == initial_count - 1

    def test_delete_tag_not_found(self, client, tag_fixtures):
        response = client.delete("/tags/999")

        assert response.status_code == 200
        assert "error" in response.json()
        assert response.json()["error"] == "Tag not found"

    def test_delete_tag_returns_success_message(self, client, tag_fixtures):
        tag_id = tag_fixtures[0].id
        response = client.delete(f"/tags/{tag_id}")

        assert response.status_code == 200
        assert response.json()["message"] == "Tag deleted successfully"

    def test_delete_multiple_tags(self, client, tag_fixtures, db_session):
        tag_id1 = tag_fixtures[0].id
        tag_id2 = tag_fixtures[1].id

        client.delete(f"/tags/{tag_id1}")
        client.delete(f"/tags/{tag_id2}")

        count = db_session.query(Tag).count()
        assert count == 1
