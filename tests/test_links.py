from models.link import Link


class TestLinkGetAll:
    def test_read_links_returns_all_links(self, client, link_fixtures):
        response = client.get("/links")

        assert response.status_code == 200
        assert len(response.json()) == 3

    def test_read_links_returns_correct_count(self, client, link_fixtures):
        response = client.get("/links")
        links = response.json()

        assert response.status_code == 200
        assert len(links) == len(link_fixtures)

    def test_read_links_contains_imdb_data(self, client, link_fixtures):
        response = client.get("/links")
        links = response.json()

        assert response.status_code == 200
        assert links[0]["imdbId"] == 111161 or any(
            l["imdbId"] == 111161 for l in links
        )
        assert links[1]["imdbId"] == 468569 or any(
            l["imdbId"] == 468569 for l in links)

    def test_read_links_empty_database(self, client):
        response = client.get("/links")

        assert response.status_code == 200
        assert response.json() == []


class TestLinkGetById:
    def test_read_link_returns_correct_link(self, client, link_fixtures):
        response = client.get("/links/1")
        link = response.json()

        assert response.status_code == 200
        assert link["id"] == 1
        assert link["imdbId"] == 111161
        assert link["tmdbId"] == 278

    def test_read_link_with_different_ids(self, client, link_fixtures):
        response1 = client.get("/links/1")
        response2 = client.get("/links/2")

        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response1.json()["imdbId"] != response2.json()["imdbId"]

    def test_read_link_not_found(self, client, link_fixtures):
        response = client.get("/links/999")

        assert response.status_code == 200
        assert "error" in response.json()
        assert response.json()["error"] == "Link not found"

    def test_read_link_returns_all_fields(self, client, link_fixtures):
        response = client.get("/links/1")
        link = response.json()

        assert response.status_code == 200
        assert "id" in link
        assert "imdbId" in link
        assert "tmdbId" in link


class TestLinkCreate:

    def test_store_link_creates_new_link(self, client, db_session):
        link_data = {
            "id": 10,
            "imdbId": 500000,
            "tmdbId": 500
        }
        response = client.post("/links", json=link_data)

        assert response.status_code == 200
        created_link = response.json()
        assert created_link["imdbId"] == 500000
        assert created_link["tmdbId"] == 500

        # Verify in database
        db_link = db_session.query(Link).filter(Link.id == 10).first()
        assert db_link is not None
        assert db_link.imdbId == 500000

    def test_store_link_returns_created_object(self, client):
        link_data = {
            "id": 20,
            "imdbId": 600000,
            "tmdbId": 600
        }
        response = client.post("/links", json=link_data)

        assert response.status_code == 200
        link = response.json()
        assert link["id"] == 20
        assert link["imdbId"] == 600000

    def test_store_link_increases_database_count(self, client, link_fixtures, db_session):
        initial_count = db_session.query(Link).count()

        link_data = {
            "id": 30,
            "imdbId": 700000,
            "tmdbId": 700
        }
        client.post("/links", json=link_data)

        final_count = db_session.query(Link).count()
        assert final_count == initial_count + 1


class TestLinkUpdate:
    def test_update_link_modifies_existing_link(self, client, link_fixtures, db_session):
        updated_data = {
            "id": 1,
            "imdbId": 999999,
            "tmdbId": 888
        }
        response = client.put("/links/1", json=updated_data)

        assert response.status_code == 200
        link = response.json()
        assert link["imdbId"] == 999999
        assert link["tmdbId"] == 888

        # Verify in database
        db_link = db_session.query(Link).filter(Link.id == 1).first()
        assert db_link.imdbId == 999999

    def test_update_link_preserves_id(self, client, link_fixtures, db_session):
        updated_data = {
            "id": 1,
            "imdbId": 111111,
            "tmdbId": 111
        }
        response = client.put("/links/1", json=updated_data)
        link = response.json()

        assert link["id"] == 1

    def test_update_link_not_found(self, client, link_fixtures):
        updated_data = {
            "id": 999,
            "imdbId": 999999,
            "tmdbId": 999
        }
        response = client.put("/links/999", json=updated_data)

        assert response.status_code == 200
        assert "error" in response.json()
        assert response.json()["error"] == "Link not found"

    def test_update_only_imdb_id(self, client, link_fixtures, db_session):
        updated_data = {
            "id": 2,
            "imdbId": 222222,
            "tmdbId": 155
        }
        response = client.put("/links/2", json=updated_data)

        assert response.status_code == 200
        db_link = db_session.query(Link).filter(Link.id == 2).first()
        assert db_link.imdbId == 222222


class TestLinkDelete:
    def test_delete_link_removes_from_database(self, client, link_fixtures, db_session):
        response = client.delete("/links/1")

        assert response.status_code == 200
        assert "message" in response.json()

        # Verify deleted from database
        deleted_link = db_session.query(Link).filter(Link.id == 1).first()
        assert deleted_link is None

    def test_delete_link_decreases_count(self, client, link_fixtures, db_session):
        initial_count = db_session.query(Link).count()

        client.delete("/links/1")

        final_count = db_session.query(Link).count()
        assert final_count == initial_count - 1

    def test_delete_link_not_found(self, client, link_fixtures):
        response = client.delete("/links/999")

        assert response.status_code == 200
        assert "error" in response.json()
        assert response.json()["error"] == "Link not found"

    def test_delete_link_returns_success_message(self, client, link_fixtures):
        response = client.delete("/links/1")

        assert response.status_code == 200
        assert response.json()["message"] == "Link deleted successfully"
