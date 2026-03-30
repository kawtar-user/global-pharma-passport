from tests.helpers import auth_headers, create_admin_token, register_user


def test_passport_generation_includes_medications_and_share_token(client):
    admin_headers = create_admin_token(client)
    acenocoumarol = client.post(
        "/api/v1/medications/ingredients",
        json={"inn_name": "Acenocoumarol", "atc_code": "B01AA07"},
        headers=admin_headers,
    ).json()
    aspirin = client.post(
        "/api/v1/medications/ingredients",
        json={"inn_name": "Acetylsalicylic acid", "atc_code": "N02BA01"},
        headers=admin_headers,
    ).json()
    tablet = client.post(
        "/api/v1/medications/dosage-forms",
        json={"code": "tablet", "name": "Tablet", "route": "oral"},
        headers=admin_headers,
    ).json()

    product_anticoagulant = client.post(
        "/api/v1/medications/products",
        json={
            "brand_name": "Sintrom",
            "country_code": "FR",
            "presentations": [
                {
                    "dosage_form_id": tablet["id"],
                    "strength_text": "4 mg",
                    "route": "oral",
                    "ingredients": [
                        {
                            "active_ingredient_id": acenocoumarol["id"],
                            "strength_value": 4,
                            "strength_unit": "mg",
                            "is_primary": True,
                        }
                    ],
                }
            ],
        },
        headers=admin_headers,
    )
    presentation_a = product_anticoagulant.json()["presentations"][0]["id"]

    product_anti_inflammatory = client.post(
        "/api/v1/medications/products",
        json={
            "brand_name": "Aspegic",
            "country_code": "FR",
            "presentations": [
                {
                    "dosage_form_id": tablet["id"],
                    "strength_text": "1000 mg",
                    "route": "oral",
                    "ingredients": [
                        {
                            "active_ingredient_id": aspirin["id"],
                            "strength_value": 1000,
                            "strength_unit": "mg",
                            "is_primary": True,
                        }
                    ],
                }
            ],
        },
        headers=admin_headers,
    )
    presentation_b = product_anti_inflammatory.json()["presentations"][0]["id"]

    created_interaction = client.post(
        "/api/v1/interactions",
        json={
            "ingredient_a_id": acenocoumarol["id"],
            "ingredient_b_id": aspirin["id"],
            "severity": "major",
            "clinical_effect": "High bleeding risk",
            "recommendation": "Avoid this association",
        },
        headers=admin_headers,
    )
    assert created_interaction.status_code == 201

    token = register_user(client, email="passport@example.com", password="PatientPass123!")
    headers = auth_headers(token)

    medication_a = client.post(
        "/api/v1/medications/me",
        json={
            "drug_presentation_id": presentation_a,
            "entered_name": "Sintrom 4 mg",
            "dose_text": "4 mg",
            "frequency_text": "1 tablet daily",
            "indication": "Anticoagulation",
        },
        headers=headers,
    )
    assert medication_a.status_code == 201

    medication_b = client.post(
        "/api/v1/medications/me",
        json={
            "drug_presentation_id": presentation_b,
            "entered_name": "Aspegic 1000 mg",
            "dose_text": "1000 mg",
            "frequency_text": "As needed",
            "indication": "Pain",
        },
        headers=headers,
    )
    assert medication_b.status_code == 201

    passport = client.get("/api/v1/passport/me", headers=headers)
    assert passport.status_code == 200
    data = passport.json()
    assert data["title"] == "Global Pharma Passport"
    assert data["patient"]["full_name"] == "Test Patient"
    assert len(data["medications"]) == 2
    assert len(data["major_interactions"]) == 1
    assert data["share_token"]
    assert data["share_path"].endswith(data["share_token"])


def test_shared_passport_can_be_read_without_auth(client):
    token = register_user(client, email="shared-passport@example.com", password="PatientPass123!")
    headers = auth_headers(token)

    generated = client.get("/api/v1/passport/me", headers=headers)
    assert generated.status_code == 200
    share_token = generated.json()["share_token"]

    shared = client.get(f"/api/v1/passport/shared/{share_token}")
    assert shared.status_code == 200
    assert "email" not in shared.json()["patient"]
    assert shared.json()["patient"]["full_name"] == "Test Patient"
