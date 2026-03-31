DATASET_NAME = "mvp-maroc-france"

DOSAGE_FORMS = [
    {
        "code": "tablet",
        "name": "Tablet",
        "route": "oral",
    },
    {
        "code": "oral_sachet",
        "name": "Oral sachet",
        "route": "oral",
    },
]

ACTIVE_INGREDIENTS = [
    {"inn_name": "Paracetamol", "atc_code": "N02BE01"},
    {"inn_name": "Metformin", "atc_code": "A10BA02"},
    {"inn_name": "Amoxicillin", "atc_code": "J01CA04"},
    {"inn_name": "Clavulanic acid", "atc_code": None},
    {"inn_name": "Ibuprofen", "atc_code": "M01AE01"},
    {"inn_name": "Acenocoumarol", "atc_code": "B01AA07"},
    {"inn_name": "Acetylsalicylic acid", "atc_code": "N02BA01"},
]

PRODUCTS = [
    {
        "key": "fr_doliprane_1000_tablet",
        "brand_name": "Doliprane",
        "country_code": "FR",
        "manufacturer": "Sanofi",
        "description": "Paracetamol 1000 mg tablet commercialized in France.",
        "presentation": {
            "dosage_form_code": "tablet",
            "route": "oral",
            "strength_text": "1000 mg",
            "ingredients": [
                {"inn_name": "Paracetamol", "strength_value": 1000, "strength_unit": "mg", "is_primary": True},
            ],
        },
    },
    {
        "key": "ma_dolostop_1000_tablet",
        "brand_name": "Dolostop",
        "country_code": "MA",
        "manufacturer": "Pharma 5",
        "description": "Paracetamol 1000 mg tablet commercialized in Morocco.",
        "presentation": {
            "dosage_form_code": "tablet",
            "route": "oral",
            "strength_text": "1000 mg",
            "ingredients": [
                {"inn_name": "Paracetamol", "strength_value": 1000, "strength_unit": "mg", "is_primary": True},
            ],
        },
    },
    {
        "key": "ma_doliprane_1000_tablet",
        "brand_name": "Doliprane",
        "country_code": "MA",
        "manufacturer": "Sanofi",
        "description": "Paracetamol 1000 mg tablet commercialized in Morocco.",
        "presentation": {
            "dosage_form_code": "tablet",
            "route": "oral",
            "strength_text": "1000 mg",
            "ingredients": [
                {"inn_name": "Paracetamol", "strength_value": 1000, "strength_unit": "mg", "is_primary": True},
            ],
        },
    },
    {
        "key": "fr_glucophage_850_tablet",
        "brand_name": "Glucophage",
        "country_code": "FR",
        "manufacturer": "Merck Sante",
        "description": "Metformin 850 mg tablet commercialized in France.",
        "presentation": {
            "dosage_form_code": "tablet",
            "route": "oral",
            "strength_text": "850 mg",
            "ingredients": [
                {"inn_name": "Metformin", "strength_value": 850, "strength_unit": "mg", "is_primary": True},
            ],
        },
    },
    {
        "key": "ma_glucophage_850_tablet",
        "brand_name": "Glucophage",
        "country_code": "MA",
        "manufacturer": "Cooper Pharma",
        "description": "Metformin 850 mg tablet commercialized in Morocco.",
        "presentation": {
            "dosage_form_code": "tablet",
            "route": "oral",
            "strength_text": "850 mg",
            "ingredients": [
                {"inn_name": "Metformin", "strength_value": 850, "strength_unit": "mg", "is_primary": True},
            ],
        },
    },
    {
        "key": "fr_augmentin_1g_125_sachet",
        "brand_name": "Augmentin",
        "country_code": "FR",
        "manufacturer": "GlaxoSmithKline",
        "description": "Amoxicillin 1 g + clavulanic acid 125 mg oral sachet commercialized in France.",
        "presentation": {
            "dosage_form_code": "oral_sachet",
            "route": "oral",
            "strength_text": "1 g / 125 mg",
            "ingredients": [
                {"inn_name": "Amoxicillin", "strength_value": 1000, "strength_unit": "mg", "is_primary": True},
                {"inn_name": "Clavulanic acid", "strength_value": 125, "strength_unit": "mg", "is_primary": False},
            ],
        },
    },
    {
        "key": "ma_augmentin_1g_125_sachet",
        "brand_name": "Augmentin",
        "country_code": "MA",
        "manufacturer": "GSK Maroc",
        "description": "Amoxicillin 1 g + clavulanic acid 125 mg oral sachet commercialized in Morocco.",
        "presentation": {
            "dosage_form_code": "oral_sachet",
            "route": "oral",
            "strength_text": "1 g / 125 mg",
            "ingredients": [
                {"inn_name": "Amoxicillin", "strength_value": 1000, "strength_unit": "mg", "is_primary": True},
                {"inn_name": "Clavulanic acid", "strength_value": 125, "strength_unit": "mg", "is_primary": False},
            ],
        },
    },
    {
        "key": "fr_spedifen_400_tablet",
        "brand_name": "Spedifen",
        "country_code": "FR",
        "manufacturer": "Zambon France",
        "description": "Ibuprofen 400 mg tablet commercialized in France.",
        "presentation": {
            "dosage_form_code": "tablet",
            "route": "oral",
            "strength_text": "400 mg",
            "ingredients": [
                {"inn_name": "Ibuprofen", "strength_value": 400, "strength_unit": "mg", "is_primary": True},
            ],
        },
    },
    {
        "key": "ma_brufen_400_tablet",
        "brand_name": "Brufen",
        "country_code": "MA",
        "manufacturer": "Cooper Pharma",
        "description": "Ibuprofen 400 mg tablet commercialized in Morocco.",
        "presentation": {
            "dosage_form_code": "tablet",
            "route": "oral",
            "strength_text": "400 mg",
            "ingredients": [
                {"inn_name": "Ibuprofen", "strength_value": 400, "strength_unit": "mg", "is_primary": True},
            ],
        },
    },
    {
        "key": "fr_sintrom_4_tablet",
        "brand_name": "Sintrom",
        "country_code": "FR",
        "manufacturer": "Novartis",
        "description": "Acenocoumarol 4 mg tablet commercialized in France.",
        "presentation": {
            "dosage_form_code": "tablet",
            "route": "oral",
            "strength_text": "4 mg",
            "ingredients": [
                {"inn_name": "Acenocoumarol", "strength_value": 4, "strength_unit": "mg", "is_primary": True},
            ],
        },
    },
    {
        "key": "ma_sintrom_4_tablet",
        "brand_name": "Sintrom",
        "country_code": "MA",
        "manufacturer": "Novartis Pharma Maroc",
        "description": "Acenocoumarol 4 mg tablet commercialized in Morocco.",
        "presentation": {
            "dosage_form_code": "tablet",
            "route": "oral",
            "strength_text": "4 mg",
            "ingredients": [
                {"inn_name": "Acenocoumarol", "strength_value": 4, "strength_unit": "mg", "is_primary": True},
            ],
        },
    },
    {
        "key": "fr_aspegic_1000_sachet",
        "brand_name": "Aspegic",
        "country_code": "FR",
        "manufacturer": "Sanofi",
        "description": "Acetylsalicylic acid 1000 mg oral sachet commercialized in France.",
        "presentation": {
            "dosage_form_code": "oral_sachet",
            "route": "oral",
            "strength_text": "1000 mg",
            "ingredients": [
                {"inn_name": "Acetylsalicylic acid", "strength_value": 1000, "strength_unit": "mg", "is_primary": True},
            ],
        },
    },
    {
        "key": "ma_aspegic_ad_1000_sachet",
        "brand_name": "Aspegic AD",
        "country_code": "MA",
        "manufacturer": "Sanofi",
        "description": "Acetylsalicylic acid 1000 mg oral sachet commercialized in Morocco.",
        "presentation": {
            "dosage_form_code": "oral_sachet",
            "route": "oral",
            "strength_text": "1000 mg",
            "ingredients": [
                {"inn_name": "Acetylsalicylic acid", "strength_value": 1000, "strength_unit": "mg", "is_primary": True},
            ],
        },
    },
]

EQUIVALENTS = [
    {
        "source_key": "fr_doliprane_1000_tablet",
        "target_key": "ma_dolostop_1000_tablet",
        "equivalence_type": "same_active_ingredient",
        "equivalence_score": 99,
        "clinical_notes": "Same active ingredient, same oral tablet strength.",
    },
    {
        "source_key": "fr_doliprane_1000_tablet",
        "target_key": "ma_doliprane_1000_tablet",
        "equivalence_type": "same_active_ingredient",
        "equivalence_score": 100,
        "clinical_notes": "Same brand family, same active ingredient and same oral tablet strength.",
    },
    {
        "source_key": "fr_glucophage_850_tablet",
        "target_key": "ma_glucophage_850_tablet",
        "equivalence_type": "same_active_ingredient",
        "equivalence_score": 99,
        "clinical_notes": "Same brand family, same active ingredient and same strength.",
    },
    {
        "source_key": "fr_augmentin_1g_125_sachet",
        "target_key": "ma_augmentin_1g_125_sachet",
        "equivalence_type": "same_combo",
        "equivalence_score": 99,
        "clinical_notes": "Same amoxicillin-clavulanic acid combination and same strength.",
    },
    {
        "source_key": "fr_spedifen_400_tablet",
        "target_key": "ma_brufen_400_tablet",
        "equivalence_type": "same_active_ingredient",
        "equivalence_score": 97,
        "clinical_notes": "Same ibuprofen oral tablet strength in France and Morocco.",
    },
    {
        "source_key": "fr_sintrom_4_tablet",
        "target_key": "ma_sintrom_4_tablet",
        "equivalence_type": "same_active_ingredient",
        "equivalence_score": 99,
        "clinical_notes": "Same acenocoumarol oral tablet strength.",
    },
    {
        "source_key": "fr_aspegic_1000_sachet",
        "target_key": "ma_aspegic_ad_1000_sachet",
        "equivalence_type": "same_active_ingredient",
        "equivalence_score": 98,
        "clinical_notes": "Same acetylsalicylic acid oral sachet strength.",
    },
]

INTERACTIONS = [
    {
        "ingredient_a": "Acenocoumarol",
        "ingredient_b": "Acetylsalicylic acid",
        "severity": "contraindicated",
        "clinical_effect": "Major increase in bleeding risk with oral anticoagulant plus analgesic-dose aspirin.",
        "recommendation": "Avoid the combination unless a clinician has explicitly validated it and monitoring is reinforced.",
        "source_reference": "VIDAL interaction guidance for acenocoumarol and analgesic-dose acetylsalicylic acid.",
    },
]
