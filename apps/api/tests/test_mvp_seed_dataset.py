from app.seeds.mvp_maroc_france import ACTIVE_INGREDIENTS, EQUIVALENTS, INTERACTIONS, PRODUCTS


def test_mvp_dataset_covers_france_and_morocco():
    countries = {product["country_code"] for product in PRODUCTS}
    assert countries == {"FR", "MA"}


def test_mvp_equivalents_reference_existing_products():
    product_keys = {product["key"] for product in PRODUCTS}
    for equivalent in EQUIVALENTS:
        assert equivalent["source_key"] in product_keys
        assert equivalent["target_key"] in product_keys


def test_mvp_interactions_are_only_major_or_stronger():
    allowed = {"major", "contraindicated"}
    for interaction in INTERACTIONS:
        assert interaction["severity"] in allowed


def test_mvp_active_ingredients_are_unique():
    ingredient_names = [ingredient["inn_name"] for ingredient in ACTIVE_INGREDIENTS]
    assert len(ingredient_names) == len(set(ingredient_names))
