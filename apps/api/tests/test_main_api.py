from tests.helpers import auth_headers, register_user


def test_health_endpoint_is_available(client):
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["environment"]
    assert payload["version"]


def test_main_patient_api_flow(client):
    token = register_user(client, email="main@example.com")
    headers = auth_headers(token)

    profile = client.get("/api/v1/users/me/profile", headers=headers)
    assert profile.status_code == 200
    assert profile.json()["email"] == "main@example.com"

    updated = client.patch(
        "/api/v1/users/me/profile",
        json={"full_name": "Main Flow Updated", "preferred_language": "en"},
        headers=headers,
    )
    assert updated.status_code == 200
    assert updated.json()["full_name"] == "Main Flow Updated"
    assert updated.json()["preferred_language"] == "en"


def test_catalog_search_requires_authentication(client):
    response = client.get("/api/v1/medications/products?query=glu&country_code=MA")
    assert response.status_code == 401
    assert response.json()["error"]["message"] == "Not authenticated"
