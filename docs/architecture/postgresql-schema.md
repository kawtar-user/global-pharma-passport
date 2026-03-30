# PostgreSQL Schema Notes

This initial schema is designed for the `Global Pharma Passport` MVP with enough structure to support:

- patient medication tracking
- prescription OCR ingestion
- international drug normalization
- interaction and contraindication checks
- multilingual travel passport sharing
- future subscriptions and B2B API access

## Design choices

- `UUID` primary keys keep the schema API-friendly and safer for public identifiers.
- `drug_products` and `drug_presentations` are separated because the same commercial brand can exist in multiple presentations.
- `drug_presentation_ingredients` links ingredients at the presentation level so dosage-specific equivalence remains accurate.
- `drug_interactions` is normalized at the ingredient level because interactions usually depend on active compounds, not brand names.
- `medical_passport_snapshots` stores immutable JSON versions of the shareable travel card per language.
- `subscriptions`, `organizations`, and `api_clients` are included now so the schema is ready for SaaS and API monetization without a later redesign.

## Constraint strategy

- Unique constraints prevent duplicate catalog and membership rows.
- `CHECK` constraints guard common domain errors such as invalid scores, negative pack sizes, and reversed date ranges.
- `ON DELETE CASCADE` is used where child records have no meaning without the parent.
- `ON DELETE SET NULL` is used where historical records should survive even if a related object disappears.

## Search strategy

- `pg_trgm` indexes are included on ingredient names, brand names, and synonyms to support fuzzy search for OCR and user-entered medication names.
- Additional indexes target the most common MVP lookups: user medications, prescriptions, interactions, and API usage logs.
