def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def register_user(client, email="patient@example.com", password="StrongPass123!"):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "full_name": "Test Patient",
            "preferred_language": "fr",
            "country_code": "MA",
        },
    )
    assert response.status_code == 201
    return response.json()["access_token"]


def create_admin_token(client, email="admin@example.com", password="AdminPass123!"):
    created = client.post(
        "/api/v1/users",
        json={
            "email": email,
            "password": password,
            "full_name": "Admin User",
            "preferred_language": "en",
            "country_code": "US",
            "role": "admin",
        },
    )
    assert created.status_code == 201

    login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login.status_code == 200
    return auth_headers(login.json()["access_token"])


def create_catalog_foundation(client, admin_headers):
    ingredient_1 = client.post(
        "/api/v1/medications/ingredients",
        json={"inn_name": "Ibuprofen", "atc_code": "M01AE01"},
        headers=admin_headers,
    ).json()
    ingredient_2 = client.post(
        "/api/v1/medications/ingredients",
        json={"inn_name": "Warfarin", "atc_code": "B01AA03"},
        headers=admin_headers,
    ).json()
    tablet = client.post(
        "/api/v1/medications/dosage-forms",
        json={"code": "tablet", "name": "Tablet", "route": "oral"},
        headers=admin_headers,
    ).json()
    return ingredient_1, ingredient_2, tablet
