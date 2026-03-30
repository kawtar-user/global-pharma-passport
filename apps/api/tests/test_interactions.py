from tests.helpers import create_admin_token, create_catalog_foundation


def _create_products(client, admin_headers, ingredient_1, ingredient_2, tablet):
    product_a = client.post(
        "/api/v1/medications/products",
        json={
            "brand_name": "Advil",
            "country_code": "FR",
            "presentations": [
                {
                    "dosage_form_id": tablet["id"],
                    "strength_text": "200 mg",
                    "route": "oral",
                    "ingredients": [
                        {
                            "active_ingredient_id": ingredient_1["id"],
                            "strength_value": 200,
                            "strength_unit": "mg",
                            "is_primary": True,
                        }
                    ],
                }
            ],
        },
        headers=admin_headers,
    )
    assert product_a.status_code == 201

    product_b = client.post(
        "/api/v1/medications/products",
        json={
            "brand_name": "Coumadin",
            "country_code": "US",
            "presentations": [
                {
                    "dosage_form_id": tablet["id"],
                    "strength_text": "5 mg",
                    "route": "oral",
                    "ingredients": [
                        {
                            "active_ingredient_id": ingredient_2["id"],
                            "strength_value": 5,
                            "strength_unit": "mg",
                            "is_primary": True,
                        }
                    ],
                }
            ],
        },
        headers=admin_headers,
    )
    assert product_b.status_code == 201
    return product_a.json()["presentations"][0]["id"], product_b.json()["presentations"][0]["id"]


def test_interaction_duplicate_is_rejected(client):
    admin_headers = create_admin_token(client)
    ingredient_1, ingredient_2, tablet = create_catalog_foundation(client, admin_headers)
    _create_products(client, admin_headers, ingredient_1, ingredient_2, tablet)

    first = client.post(
        "/api/v1/interactions",
        json={
            "ingredient_a_id": ingredient_1["id"],
            "ingredient_b_id": ingredient_2["id"],
            "severity": "major",
            "clinical_effect": "Increased bleeding risk",
            "recommendation": "Avoid combination unless clinically supervised",
        },
        headers=admin_headers,
    )
    assert first.status_code == 201

    duplicate = client.post(
        "/api/v1/interactions",
        json={
            "ingredient_a_id": ingredient_2["id"],
            "ingredient_b_id": ingredient_1["id"],
            "severity": "major",
            "clinical_effect": "Increased bleeding risk",
            "recommendation": "Avoid combination unless clinically supervised",
        },
        headers=admin_headers,
    )
    assert duplicate.status_code == 409


def test_interaction_check_returns_empty_when_no_interaction_exists(client):
    admin_headers = create_admin_token(client)
    ingredient_1, ingredient_2, tablet = create_catalog_foundation(client, admin_headers)
    presentation_a, presentation_b = _create_products(client, admin_headers, ingredient_1, ingredient_2, tablet)

    response = client.post(
        "/api/v1/interactions/check",
        json={"presentation_ids": [presentation_a, presentation_b]},
    )
    assert response.status_code == 200
    assert response.json()["matches"] == []
