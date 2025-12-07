import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from main import app, get_db, Base
from models.user import User
from auth import hash_password

# Use the same database as the main app
DATABASE_URL = "sqlite:///example.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_teardown():
    db = TestingSessionLocal()
    try:
        # Delete all users from the database before test
        db.query(User).delete()
        db.commit()
        yield
    finally:
        # Clean up after test
        db.query(User).delete()
        db.commit()
        db.close()


@pytest.fixture
def test_user(setup_teardown):
    db = TestingSessionLocal()
    try:
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=hash_password("password123"),
            roles=["ROLE_USER"]
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    finally:
        db.close()


@pytest.fixture
def admin_user(setup_teardown):
    db = TestingSessionLocal()
    try:
        user = User(
            username="adminuser",
            email="admin@example.com",
            hashed_password=hash_password("adminpass123"),
            roles=["ROLE_ADMIN", "ROLE_USER"]
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    finally:
        db.close()


@pytest.fixture
def user_token(test_user):
    response = client.post(
        "/login",
        json={"username": "testuser", "password": "password123"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def admin_token(admin_user):
    response = client.post(
        "/login",
        json={"username": "adminuser", "password": "adminpass123"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


# ! LOGIN TESTS

class TestLogin:
    def test_login_successful(self, test_user):
        response = client.post(
            "/login",
            json={"username": "testuser", "password": "password123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_username(self):
        response = client.post(
            "/login",
            json={"username": "nonexistent", "password": "password123"}
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid credentials"

    def test_login_invalid_password(self, test_user):
        response = client.post(
            "/login",
            json={"username": "testuser", "password": "wrongpassword"}
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid credentials"


# ! USER TESTS

class TestUsers:
    def test_create_user_success_as_admin(self, admin_token):
        response = client.post(
            "/users",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "newpass123",
                "roles": ["ROLE_USER"]
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert data["roles"] == ["ROLE_USER"]

    def test_create_user_duplicate_username(self, admin_token, test_user):
        response = client.post(
            "/users",
            json={
                "username": "testuser",
                "email": "another@example.com",
                "password": "pass123",
                "roles": ["ROLE_USER"]
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_create_user_duplicate_email(self, admin_token, test_user):
        response = client.post(
            "/users",
            json={
                "username": "anotheruser",
                "email": "test@example.com",
                "password": "pass123",
                "roles": ["ROLE_USER"]
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_create_user_without_admin_role(self, user_token):
        response = client.post(
            "/users",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "newpass123",
                "roles": ["ROLE_USER"]
            },
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 403
        assert "do not have permission" in response.json()["detail"]

    def test_create_user_without_token(self):
        response = client.post(
            "/users",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "newpass123",
                "roles": ["ROLE_USER"]
            }
        )
        assert response.status_code == 403

    def test_get_all_users_as_admin(self, admin_token, test_user):
        response = client.get(
            "/users",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        users = response.json()
        assert len(users) == 2  # admin_user and test_user
        usernames = [u["username"] for u in users]
        assert "adminuser" in usernames
        assert "testuser" in usernames

    def test_get_all_users_without_admin_role(self, user_token):
        response = client.get(
            "/users",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 403
        assert "do not have permission" in response.json()["detail"]

    def test_get_all_users_without_token(self):
        response = client.get("/users")
        assert response.status_code == 403


# ! USER DETAILS TESTS

class TestUserDetails:
    def test_get_user_details_success(self, user_token, test_user):
        response = client.get(
            "/user_details",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert data["roles"] == ["ROLE_USER"]
        assert data["user_id"] == test_user.id

    def test_get_user_details_without_token(self):
        response = client.get("/user_details")
        assert response.status_code == 403

    def test_get_user_details_with_invalid_token(self):
        response = client.get(
            "/user_details",
            headers={"Authorization": "Bearer invalid.token.here"}
        )
        assert response.status_code == 401

    def test_get_user_details_admin(self, admin_token, admin_user):
        response = client.get(
            "/user_details",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "adminuser"
        assert data["email"] == "admin@example.com"
        assert "ROLE_ADMIN" in data["roles"]
        assert "ROLE_USER" in data["roles"]


# ! PROTECTED ENDPOINTS TEST

class TestProtectedEndpoints:
    def test_movies_endpoint_requires_auth(self):
        response = client.get("/movies")
        assert response.status_code == 403

    def test_movies_endpoint_with_token(self, user_token):
        response = client.get(
            "/movies",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200

    def test_links_endpoint_requires_auth(self):
        response = client.get("/links")
        assert response.status_code == 403

    def test_links_endpoint_with_token(self, user_token):
        response = client.get(
            "/links",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200

    def test_ratings_endpoint_requires_auth(self):
        response = client.get("/ratings")
        assert response.status_code == 403

    def test_ratings_endpoint_with_token(self, user_token):
        response = client.get(
            "/ratings",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200

    def test_tags_endpoint_requires_auth(self):
        response = client.get("/tags")
        assert response.status_code == 403

    def test_tags_endpoint_with_token(self, user_token):
        response = client.get(
            "/tags",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200


# ! INTEGRATION TESTS

class TestIntegration:
    def test_complete_user_flow(self):
        # Create user as admin
        admin_db = TestingSessionLocal()
        admin_user = User(
            username="admin",
            email="admin@example.com",
            hashed_password=hash_password("adminpass"),
            roles=["ROLE_ADMIN"]
        )
        admin_db.add(admin_user)
        admin_db.commit()
        admin_db.close()

        # Login as admin
        login_response = client.post(
            "/login",
            json={"username": "admin", "password": "adminpass"}
        )
        assert login_response.status_code == 200
        admin_token = login_response.json()["access_token"]

        # Create new user
        create_response = client.post(
            "/users",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "userpass123",
                "roles": ["ROLE_USER"]
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert create_response.status_code == 200

        # Login as new user
        new_login_response = client.post(
            "/login",
            json={"username": "newuser", "password": "userpass123"}
        )
        assert new_login_response.status_code == 200
        new_token = new_login_response.json()["access_token"]

        # Get user details
        details_response = client.get(
            "/user_details",
            headers={"Authorization": f"Bearer {new_token}"}
        )
        assert details_response.status_code == 200
        assert details_response.json()["username"] == "newuser"

    def test_token_gives_access_to_protected_endpoints(self, user_token):
        endpoints = ["/movies", "/links", "/ratings", "/tags"]
        
        for endpoint in endpoints:
            response = client.get(
                endpoint,
                headers={"Authorization": f"Bearer {user_token}"}
            )
            assert response.status_code == 200, f"Failed for {endpoint}"
