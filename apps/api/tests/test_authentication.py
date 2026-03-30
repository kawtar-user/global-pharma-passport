from tests.helpers import auth_headers, register_user


def test_login_rejects_invalid_credentials(client):
    register_user(client, email="auth@example.com", password="StrongPass123!")

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "auth@example.com", "password": "WrongPass123!"},
    )
    assert response.status_code == 401
    assert response.json()["error"]["message"] == "Invalid credentials"


def test_protected_endpoint_requires_token(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_auth_responses_are_not_cacheable(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "cache@example.com",
            "password": "StrongPass123!",
            "full_name": "Cache Test",
            "preferred_language": "fr",
            "country_code": "MA",
        },
    )
    assert response.status_code == 201
    assert response.headers["Cache-Control"] == "no-store"

    token = response.json()["access_token"]
    me = client.get("/api/v1/auth/me", headers=auth_headers(token))
    assert me.status_code == 200
