def test_weak_password_is_rejected(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "weak@example.com",
            "password": "weakpass",
            "full_name": "Weak Password",
            "preferred_language": "fr",
            "country_code": "MA",
        },
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_extra_fields_are_rejected(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "extra@example.com",
            "password": "StrongPass123!",
            "full_name": "Extra Fields",
            "preferred_language": "fr",
            "country_code": "MA",
            "unexpected": "forbidden",
        },
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_security_headers_are_set(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Cache-Control"] == "no-store"
    assert "X-Request-ID" in response.headers


def test_validation_errors_include_readable_message_and_details(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "invalid@example.com",
            "password": "StrongPass123!",
            "full_name": "Invalid Country",
            "preferred_language": "fr",
            "country_code": "INVALID",
        },
    )
    assert response.status_code == 422
    payload = response.json()["error"]
    assert payload["message"] == "Some information is missing or invalid. Please review the form and try again."
    assert payload["details"]
