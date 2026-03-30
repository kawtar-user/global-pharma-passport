from tests.helpers import auth_headers, register_user


def register_and_login(client, email="billing@example.com", password="StrongPass123!"):
    return auth_headers(register_user(client, email=email, password=password))


def test_free_plan_entitlements_and_medication_limit(client):
    headers = register_and_login(client)

    entitlements = client.get("/api/v1/billing/me/entitlements", headers=headers)
    assert entitlements.status_code == 200
    assert entitlements.json()["plan_code"] == "free"
    assert entitlements.json()["limits"]["medications_max"] == 3
    assert entitlements.json()["limits"]["travel_mode_enabled"] is False

    for index in range(3):
        created = client.post(
            "/api/v1/medications/me",
            json={
                "entered_name": f"Medication {index}",
                "dose_text": "1 tablet",
                "frequency_text": "daily",
                "indication": "Test",
            },
            headers=headers,
        )
        assert created.status_code == 201

    blocked = client.post(
        "/api/v1/medications/me",
        json={
            "entered_name": "Medication 4",
            "dose_text": "1 tablet",
            "frequency_text": "daily",
            "indication": "Test",
        },
        headers=headers,
    )
    assert blocked.status_code == 403
