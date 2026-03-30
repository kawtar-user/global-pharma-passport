from tests.helpers import auth_headers, create_admin_token, register_user


def test_anonymous_event_tracking_is_accepted(client):
    response = client.post(
        "/api/v1/analytics/track",
        json={
            "event_name": "landing_viewed",
            "session_id": "sess_test",
            "locale": "fr",
            "country_code": "MA",
            "source": "web",
            "properties": {"screen": "landing", "email": "should_not_be_stored"},
        },
    )
    assert response.status_code == 202
    assert response.json()["status"] == "accepted"


def test_analytics_dashboard_returns_core_metrics(client):
    user_token = register_user(client, email="analytics@example.com")
    client.post(
        "/api/v1/analytics/track",
        json={
            "event_name": "dashboard_viewed",
            "session_id": "sess_user",
            "locale": "fr",
            "country_code": "MA",
            "source": "web",
            "properties": {"screen": "dashboard"},
        },
        headers=auth_headers(user_token),
    )

    admin_headers = create_admin_token(client, email="analytics-admin@example.com", password="AdminPass123!")
    response = client.get("/api/v1/analytics/dashboard", headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["total_users"] >= 2
    assert "feature_usage" in response.json()
    assert "metrics" in response.json()
