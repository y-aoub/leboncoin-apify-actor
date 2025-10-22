# Leboncoin Scraper

Un scraper universel pour extraire des données structurées depuis Leboncoin.fr. Supporte toutes les catégories du site avec filtrage avancé et exports multiples.

## Vue d'ensemble

Cet outil permet d'extraire des données publiques depuis Leboncoin de manière automatisée. Il gère la pagination, la déduplication, et offre des options de filtrage par localisation, catégorie, prix et autres attributs spécifiques.

Conçu pour fonctionner sur la plateforme Apify, il peut également être exécuté localement avec une interface Streamlit pour tests et prototypage.

## Fonctionnalités

### Extraction de données

- Support de toutes les catégories Leboncoin (Immobilier, Véhicules, Emploi, Électronique, etc.)
- Pagination automatique avec gestion des limites
- Déduplication des annonces
- Export en format JSON ou CSV

### Filtrage

**Par localisation :**
- Ville (avec rayon de recherche en mètres)
- Département(s)
- Région(s)
- France entière

**Par critères généraux :**
- Catégorie spécifique
- Fourchette de prix
- Type d'annonce (offre/demande)
- Type de vendeur (particulier/professionnel)
- Recherche textuelle (dans titre ou titre+description)
- Tri (plus récent, pertinence, prix croissant/décroissant)

**Par critères spécifiques :**
- Immobilier : surface, terrain, nombre de pièces, DPE, type de bien
- Véhicules : kilométrage, année, carburant, marque/modèle
- Emploi : type de contrat, salaire, expérience
- Autres catégories : attributs variables selon la catégorie

### Options avancées

- Filtrage temporel : collecte uniquement les annonces récentes (dernières X heures/jours)
- Arrêt automatique après X annonces anciennes consécutives
- Support proxy pour éviter les limitations
- Délais configurables entre requêtes

## Données extraites

### Format détaillé

Chaque annonce extraite contient :

```json
{
  "id": "2456789123",
  "url": "https://www.leboncoin.fr/...",
  "subject": "Titre de l'annonce",
  "body": "Description complète",
  "price": 450000,
  "first_publication_date": "2025-10-20 14:30:00",
  "index_date": "2025-10-22 09:15:00",
  "scraped_at": "2025-10-22 10:00:00",
  "city": "Paris",
  "zipcode": "75001",
  "department_id": "75",
  "department_name": "Paris",
  "region_id": "12",
  "region_name": "Île-de-France",
  "latitude": 48.8566,
  "longitude": 2.3522,
  "attributes": {
    "square": "120",
    "rooms": "4",
    "energy_rate": "c"
  },
  "images": ["url1", "url2"],
  "image_count": 2
}
```

### Format compact

Version allégée avec informations essentielles :
- ID, URL, titre
- Prix
- Ville, code postal
- Date de mise à jour

## Configuration

### Paramètres d'entrée

| Paramètre | Type | Description | Requis |
|-----------|------|-------------|--------|
| `category` | String | Catégorie Leboncoin (ex: `IMMOBILIER_VENTES_IMMOBILIERES`) | Oui |
| `location_type` | String | Type de localisation : `city`, `department`, `region`, `none` | Non |
| `locations` | Array | Liste de localisations (format dépend du type) | Non |
| `search_text` | String | Mots-clés de recherche | Non |
| `price_min` | Integer | Prix minimum en euros | Non |
| `price_max` | Integer | Prix maximum en euros | Non |
| `max_pages` | Integer | Nombre maximum de pages à scraper (0 = illimité) | Non |
| `max_age_days` | Float | Âge maximum des annonces en jours (0 = désactivé) | Non |
| `output_format` | String | Format de sortie : `detailed` ou `compact` | Non |
| `filters` | Object | Filtres spécifiques par catégorie (JSON) | Non |

### Exemple de configuration

**Immobilier :**
```json
{
  "category": "IMMOBILIER_VENTES_IMMOBILIERES",
  "location_type": "department",
  "locations": [{"code": "75"}],
  "filters": {
    "real_estate_type": ["1"],
    "square": [100, 200],
    "rooms": [3, 5],
    "energy_rate": ["a", "b", "c"]
  },
  "price_min": 300000,
  "price_max": 800000,
  "max_pages": 10
}
```

**Véhicules :**
```json
{
  "category": "VEHICULES_VOITURES",
  "location_type": "region",
  "locations": [{"name": "ILE_DE_FRANCE"}],
  "filters": {
    "fuel": ["4"],
    "mileage": [0, 50000]
  },
  "price_min": 15000,
  "price_max": 35000
}
```

## Performance

### Vitesse

- Environ 100-200 annonces par minute (dépend des délais configurés)
- Pagination automatique sans intervention

### Limites

- Leboncoin limite généralement les résultats à ~100 pages par recherche
- Utilisation de proxy recommandée pour éviter les erreurs 403 (Datadome)
- Les délais entre requêtes impactent la vitesse mais améliorent la stabilité

### Consommation (Apify)

Estimation approximative :
- 1 000 annonces : ~0.01-0.02 compute units
- Dépend du format de sortie choisi et des délais configurés

## Catégories supportées

Toutes les catégories Leboncoin sont supportées. Exemples :

- `TOUTES_CATEGORIES`
- `IMMOBILIER_VENTES_IMMOBILIERES`
- `IMMOBILIER_LOCATIONS`
- `VEHICULES_VOITURES`
- `VEHICULES_MOTOS`
- `EMPLOI_OFFRES_DEMPLOI`
- `ELECTRONIQUE_ORDINATEURS`
- `ELECTRONIQUE_TELEPHONES_ET_OBJETS_CONNECTES`
- `MAISON_ET_JARDIN_AMEUBLEMENT`

Liste complète dans `CATEGORIES_REFERENCE.md`.

## Limitations et points d'attention

### Limitations techniques

- **Blocages possibles** : Leboncoin utilise Datadome pour détecter les bots. L'utilisation d'un proxy propre (résidentiel français de préférence) est recommandée pour des volumes importants.
- **Pagination limitée** : Le site limite généralement l'accès aux 100 premières pages de résultats. Pour des recherches exhaustives, affinez les filtres.
- **Pas d'historique** : Le scraper collecte l'état actuel, pas l'historique des modifications d'annonces.

### Utilisation responsable

- Respectez les délais entre requêtes (1-2 secondes minimum recommandé)
- Ne collectez que les données dont vous avez réellement besoin
- Les données collectées sont publiques mais leur utilisation doit respecter le RGPD
- Cet outil n'est pas affilié à Leboncoin

### Cas non supportés

- Extraction de numéros de téléphone masqués (nécessite connexion)
- Accès aux messages entre vendeurs et acheteurs
- Création ou modification d'annonces

## Installation locale

Pour tester en local (non requis pour Apify) :

```bash
# Installation
pip install -r requirements.txt

# Interface Streamlit
streamlit run ui.py

# Ligne de commande
# Créer apify_input.json avec votre configuration
python main.py
```

## Tests

```bash
python test_scraper.py
```

Suite de tests incluse pour valider :
- Configuration
- Enums et mapping
- Construction de localisations
- Traitement des données
- Initialisation du client
- (Optionnel) Test de scraping réel

## Documentation

- `README.md` - Ce fichier
- `QUICKSTART.md` - Guide de démarrage rapide
- `USAGE.md` - Documentation détaillée d'utilisation
- `CATEGORIES_REFERENCE.md` - Liste complète des catégories et filtres
- `FILES_OVERVIEW.md` - Structure du projet

## Architecture

```
leboncoin_actor/
├── main.py                  # Script principal (Apify compatible)
├── ui.py                    # Interface Streamlit
├── requirements.txt         # Dépendances Python
├── Dockerfile              # Container Apify
├── .actor/
│   ├── actor.json          # Configuration Apify
│   └── input_schema.json   # Schéma d'interface
└── config_examples.json    # Configurations d'exemple
```

### Composants principaux

- **ApifyAdapter** : Gère l'intégration avec Apify (fallback local si non disponible)
- **Config** : Charge et valide la configuration
- **LocationBuilder** : Construit les objets de localisation
- **DataProcessor** : Traite et normalise les données
- **AdTransformer** : Transforme les annonces en format structuré
- **ScraperEngine** : Moteur principal de scraping

## Dépendances

- `lbc` (>=1.0.10) - Bibliothèque Python pour l'API Leboncoin
- `apify` (>=2.0.0) - SDK Apify (optionnel)
- `streamlit` (>=1.28.0) - Interface UI (optionnel)
- `pandas` (>=2.0.0) - Export CSV (optionnel)

Voir `requirements.txt` pour la liste complète.

## Changelog

### Version 1.0.0 (2025-10-22)

- Support de toutes les catégories Leboncoin
- Filtrage par ville, département, région
- Filtres personnalisés par catégorie
- Export JSON et CSV
- Interface Streamlit pour tests
- Déduplication automatique
- Gestion des erreurs et reprises
- Support proxy
- Documentation complète

## Licence

MIT License - Voir fichier `LICENSE`

## Support

Pour signaler un bug ou demander une fonctionnalité, ouvrez une issue sur le dépôt.

Documentation complète disponible dans les fichiers `.md` du projet.

## Avertissement

Cet outil collecte des données publiquement accessibles depuis Leboncoin.fr. Les utilisateurs sont responsables :
- Du respect des conditions d'utilisation de Leboncoin
- De la conformité avec le RGPD dans le traitement des données
- De l'usage légal et éthique des données collectées

Cet outil n'est pas affilié à, approuvé par, ou associé de quelque manière que ce soit avec Leboncoin ou ses services.

---

*Projet basé sur la bibliothèque [lbc](https://github.com/etienne-hd/lbc) d'Etienne Hodé*
