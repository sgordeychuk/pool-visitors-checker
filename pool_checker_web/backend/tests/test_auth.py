import pytest
from fastapi import status


class TestRegistration:
    def test_register_success(self, client, test_user_data):
        response = client.post("/api/v1/auth/register", json=test_user_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["username"] == test_user_data["username"]
        assert "id" in data
        assert data["is_active"] is True
        assert data["is_superuser"] is False
        assert "password" not in data
        assert "hashed_password" not in data

    def test_register_duplicate_email(self, client, test_user_data, registered_user):
        new_user = {**test_user_data, "username": "different_username"}
        response = client.post("/api/v1/auth/register", json=new_user)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Email already registered" in response.json()["detail"]

    def test_register_duplicate_username(self, client, test_user_data, registered_user):
        new_user = {**test_user_data, "email": "different@example.com"}
        response = client.post("/api/v1/auth/register", json=new_user)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Username already taken" in response.json()["detail"]

    def test_register_invalid_email(self, client, test_user_data):
        invalid_data = {**test_user_data, "email": "not-an-email"}
        response = client.post("/api/v1/auth/register", json=invalid_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_short_password(self, client, test_user_data):
        invalid_data = {**test_user_data, "password": "short"}
        response = client.post("/api/v1/auth/register", json=invalid_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_short_username(self, client, test_user_data):
        invalid_data = {**test_user_data, "username": "ab"}
        response = client.post("/api/v1/auth/register", json=invalid_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestLogin:
    def test_login_success_with_username(self, client, test_user_data, registered_user):
        response = client.post(
            "/api/v1/auth/login",
            data={"username": test_user_data["username"], "password": test_user_data["password"]},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_success_with_email(self, client, test_user_data, registered_user):
        response = client.post(
            "/api/v1/auth/login",
            data={"username": test_user_data["email"], "password": test_user_data["password"]},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_login_wrong_password(self, client, test_user_data, registered_user):
        response = client.post(
            "/api/v1/auth/login",
            data={"username": test_user_data["username"], "password": "wrongpassword"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Incorrect username or password" in response.json()["detail"]

    def test_login_nonexistent_user(self, client):
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "nonexistent", "password": "somepassword"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Incorrect username or password" in response.json()["detail"]


class TestAuthenticatedEndpoints:
    def test_get_me_success(self, client, test_user_data, registered_user):
        login_response = client.post(
            "/api/v1/auth/login",
            data={"username": test_user_data["username"], "password": test_user_data["password"]},
        )
        token = login_response.json()["access_token"]

        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["username"] == test_user_data["username"]

    def test_get_me_no_token(self, client):
        response = client.get("/api/v1/auth/me")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_me_invalid_token(self, client):
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestRefreshToken:
    def test_refresh_token_success(self, client, test_user_data, registered_user):
        login_response = client.post(
            "/api/v1/auth/login",
            data={"username": test_user_data["username"], "password": test_user_data["password"]},
        )
        refresh_token = login_response.json()["refresh_token"]

        response = client.post(
            "/api/v1/auth/refresh",
            params={"refresh_token": refresh_token}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_refresh_token_invalid(self, client):
        response = client.post(
            "/api/v1/auth/refresh",
            params={"refresh_token": "invalid_refresh_token"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
