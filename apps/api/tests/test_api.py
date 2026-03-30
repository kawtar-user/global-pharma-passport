from tests.helpers import create_admin_token, create_catalog_foundation, register_user


def _create_foundation_data(client):
    headers = create_admin_token(client)
    ingredient_1, ingredient_2, tablet = create_catalog_foundation(client, headers)
    return ingredient_1, ingredient_2, tablet, headers


def test_user_and_medication_flow(client):
    token = register_user(client, email="patient-medications@example.com", password="PatientPass123!")
    headers = {"Authorization": f"Bearer {token}"}

    medication = client.post(
        "/api/v1/medications/me",
        json={
            "entered_name": "Doliprane",
            "dose_text": "500 mg",
            "frequency_text": "2x/day",
        },
        headers=headers,
    )
    assert medication.status_code == 201

    medications = client.get("/api/v1/medications/me", headers=headers)
    assert medications.status_code == 200
    assert len(medications.json()) == 1


def test_interactions_and_equivalents_flow(client):
    ingredient_1, ingredient_2, tablet, admin_headers = _create_foundation_data(client)
    user_token = register_user(client, email="equivalents@example.com", password="PatientPass123!")
    user_headers = {"Authorization": f"Bearer {user_token}"}

    product_fr = client.post(
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
    assert product_fr.status_code == 201
    fr_presentation_id = product_fr.json()["presentations"][0]["id"]

    product_us = client.post(
        "/api/v1/medications/products",
        json={
            "brand_name": "Motrin",
            "country_code": "US",
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
    assert product_us.status_code == 201
    us_presentation_id = product_us.json()["presentations"][0]["id"]

    product_warfarin = client.post(
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
    assert product_warfarin.status_code == 201
    warfarin_presentation_id = product_warfarin.json()["presentations"][0]["id"]

    interaction = client.post(
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
    assert interaction.status_code == 201

    equivalent = client.post(
        "/api/v1/international-equivalents",
        json={
            "source_drug_presentation_id": fr_presentation_id,
            "target_drug_presentation_id": us_presentation_id,
            "equivalence_type": "same_active_ingredient",
            "equivalence_score": 98,
            "clinical_notes": "Same active ingredient and dose",
        },
        headers=admin_headers,
    )
    assert equivalent.status_code == 201

    check = client.post(
        "/api/v1/interactions/check",
        json={"presentation_ids": [fr_presentation_id, warfarin_presentation_id]},
        headers=user_headers,
    )
    assert check.status_code == 200
    assert len(check.json()["matches"]) == 1
    assert check.json()["matches"][0]["severity"] == "major"

    search = client.get(
        f"/api/v1/international-equivalents/search/{fr_presentation_id}?target_country_code=US",
        headers=user_headers,
    )
    assert search.status_code == 200
    assert len(search.json()["results"]) == 1
    assert search.json()["results"][0]["brand_name"] == "Motrin"
