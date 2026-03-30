# Dataset MVP Maroc-France

## Objectif

Ce dataset fournit un socle minimal et exploitable pour le MVP `Global Pharma Passport` sur un seul corridor international :

- Maroc
- France

Il privilégie :

- des présentations orales simples
- des médicaments courants
- des équivalents basés sur DCI + dosage + forme
- une seule interaction critique pour démarrer proprement

## Tables déjà utilisées

Le schéma PostgreSQL existant suffit. Aucun changement de table n'est nécessaire pour ce MVP.

Tables mobilisées :

- `active_ingredients`
- `dosage_forms`
- `drug_products`
- `drug_presentations`
- `drug_presentation_ingredients`
- `drug_equivalents`
- `drug_interactions`

## Couverture seedée

Dosage forms :

- `tablet`
- `oral_sachet`

Active ingredients :

- Paracetamol
- Metformin
- Amoxicillin
- Clavulanic acid
- Ibuprofen
- Acenocoumarol
- Acetylsalicylic acid

Paires France <-> Maroc :

- Doliprane 1000 mg <-> Dolostop 1000 mg
- Glucophage 850 mg <-> Glucophage 850 mg
- Augmentin 1 g / 125 mg <-> Augmentin 1 g / 125 mg
- Spedifen 400 mg <-> Brufen 400 mg
- Sintrom 4 mg <-> Sintrom 4 mg
- Aspegic 1000 mg <-> Aspegic AD 1000 mg

Interaction critique seedée :

- Acenocoumarol + Acetylsalicylic acid

## Loader

Le loader est idempotent et peut être rejoué :

- [mvp_maroc_france.py](/Users/kawtar/Documents/New%20project%203/apps/api/app/seeds/mvp_maroc_france.py)
- [load_mvp_catalog.py](/Users/kawtar/Documents/New%20project%203/apps/api/app/seeds/load_mvp_catalog.py)

Commande :

```bash
cd /Users/kawtar/Documents/New\ project\ 3/apps/api
python -m app.seeds.load_mvp_catalog
```

## Références de travail utilisées pour ce seed

France :

- [VIDAL - Glucophage](https://www.vidal.fr/recherche/index/q/Glucophage%20850%20mg)
- [VIDAL - Augmentin](https://www.vidal.fr/recherche/index/q/Augmentin%201%20g%20125%20mg)
- [VIDAL - Ibuprofène / générique de Brufen](https://www.vidal.fr/medicaments/ibuprofene-viatris-sante-400-mg-cp-pellic-242885.html)
- [VIDAL - Acénocoumarol](https://www.vidal.fr/medicaments/substances/acenocoumarol-3967.html)

Maroc :

- [med.ma - Glucophage 850 mg](https://www.med.ma/pharmaceutical/glucophage-850-mg-comprime-pellicule-4751)
- [medicament.ma - Augmentin 1 g / 125 mg](https://medicament.ma/medicament/augmentin-1-g125-mg-sachet-2/)
- [med.ma - Dolostop 1000 mg](https://www.med.ma/%D8%AF%D9%88%D8%A7%D8%A1/dolostop-1000-mg-comprime-effervescent-8834)
- [med.ma - Aspegic AD 1000 mg](https://www.med.ma/medicament/aspegic-ad-1000-mg-poudre-en-sachet-5817)

## Pourquoi cette structure est saine

- le dataset reste petit et audit-able
- les produits sont déclaratifs
- les équivalents sont séparés des produits
- les interactions sont au niveau des principes actifs
- l'ajout futur d'autres pays suit exactement la même structure
