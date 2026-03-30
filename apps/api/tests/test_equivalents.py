from tests.helpers import auth_headers, create_admin_token, create_catalog_foundation, register_user


def test_equivalent_search_requires_authentication(client):
    response = client.get("/api/v1/international-equivalents/search/some-id?target_country_code=US")
    assert response.status_code == 401


def test_free_plan_limits_equivalent_results_to_one(client):
    admin_headers = create_admin_token(client)
    ingredient_1, _, tablet = create_catalog_foundation(client, admin_headers)

    source = client.post(
        "/api/v1/medications/products",
        json={
            "brand_name": "Glucophage",
            "country_code": "MA",
            "presentations": [
                {
                    "dosage_form_id": tablet["id"],
                    "strength_text": "850 mg",
                    "route": "oral",
                    "ingredients": [
                        {
                            "active_ingredient_id": ingredient_1["id"],
                            "strength_value": 850,
                            "strength_unit": "mg",
                            "is_primary": True,
                        }
                    ],
                }
            ],
        },
        headers=admin_headers,
    )
    assert source.status_code == 201
    source_presentation_id = source.json()["presentations"][0]["id"]

    target_names = [("FranceEq", "FR"), ("USEq", "US")]
    target_ids = []
    for name, country in target_names:
        created = client.post(
            "/api/v1/medications/products",
            json={
                "brand_name": name,
                "country_code": country,
                "presentations": [
                    {
                        "dosage_form_id": tablet["id"],
                        "strength_text": "850 mg",
                        "route": "oral",
                        "ingredients": [
                            {
                                "active_ingredient_id": ingredient_1["id"],
                                "strength_value": 850,
                                "strength_unit": "mg",
                                "is_primary": True,
                            }
                        ],
                    }
                ],
            },
            headers=admin_headers,
        )
        assert created.status_code == 201
        target_ids.append(created.json()["presentations"][0]["id"])

    for target_id in target_ids:
        link = client.post(
            "/api/v1/international-equivalents",
            json={
                "source_drug_presentation_id": source_presentation_id,
                "target_drug_presentation_id": target_id,
                "equivalence_type": "same_active_ingredient",
                "equivalence_score": 95,
                "clinical_notes": "Equivalent based on ingredient and dose",
            },
            headers=admin_headers,
        )
        assert link.status_code == 201

    token = register_user(client, email="eq@example.com")
    search = client.get(
        f"/api/v1/international-equivalents/search/{source_presentation_id}",
        headers=auth_headers(token),
    )
    assert search.status_code == 200
    assert len(search.json()["results"]) == 1


def test_equivalent_search_returns_notice_when_no_match_exists(client):
    admin_headers = create_admin_token(client)
    ingredient_1, _, tablet = create_catalog_foundation(client, admin_headers)

    source = client.post(
        "/api/v1/medications/products",
        json={
            "brand_name": "Glucophage",
            "country_code": "MA",
            "presentations": [
                {
                    "dosage_form_id": tablet["id"],
                    "strength_text": "850 mg",
                    "route": "oral",
                    "ingredients": [
                        {
                            "active_ingredient_id": ingredient_1["id"],
                            "strength_value": 850,
                            "strength_unit": "mg",
                            "is_primary": True,
                        }
                    ],
                }
            ],
        },
        headers=admin_headers,
    )
    assert source.status_code == 201
    source_presentation_id = source.json()["presentations"][0]["id"]

    token = register_user(client, email="eq-empty@example.com")
    search = client.get(
        f"/api/v1/international-equivalents/search/{source_presentation_id}?target_country_code=FR",
        headers=auth_headers(token),
    )
    assert search.status_code == 200
    assert search.json()["results"] == []
    assert search.json()["notice"]["code"] == "no_equivalent_found"
