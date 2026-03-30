from tests.helpers import auth_headers, register_user


def test_auth_register_login_and_me(client):
    token = register_user(client)

    me = client.get("/api/v1/auth/me", headers=auth_headers(token))
    assert me.status_code == 200
    assert me.json()["email"] == "patient@example.com"

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "patient@example.com", "password": "StrongPass123!"},
    )
    assert login.status_code == 200
    assert login.json()["token_type"] == "bearer"


def test_patient_medication_management(client):
    token = register_user(client)

    created = client.post(
        "/api/v1/medications/me",
        json={
            "entered_name": "Glucophage 850 mg",
            "dose_text": "850 mg",
            "frequency_text": "2x/day",
            "indication": "Diabete de type 2",
        },
        headers=auth_headers(token),
    )
    assert created.status_code == 201
    medication_id = created.json()["id"]

    listing = client.get("/api/v1/medications/me", headers=auth_headers(token))
    assert listing.status_code == 200
    assert len(listing.json()) == 1

    updated = client.patch(
        f"/api/v1/medications/me/{medication_id}",
        json={"status": "paused"},
        headers=auth_headers(token),
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "paused"

    deleted = client.delete(f"/api/v1/medications/me/{medication_id}", headers=auth_headers(token))
    assert deleted.status_code == 204
