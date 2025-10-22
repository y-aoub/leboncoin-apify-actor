# 🔍 Leboncoin Universal Scraper

> **Scraper avancé et flexible pour Leboncoin.fr - Toutes catégories, localisations et filtres**

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 🌟 Fonctionnalités

### ✨ Principales
- 🎯 **Toutes les catégories** : Immobilier, Véhicules, Emploi, Électronique, etc.
- 🌍 **Localisations flexibles** : Ville, Département, Région ou France entière
- 🔧 **Filtres personnalisables** : Prix, surface, DPE, kilométrage, etc.
- 📊 **Formats de sortie** : Détaillé (tous champs) ou Compact (essentiel)
- 🔄 **Déduplication intelligente** : Évite les doublons automatiquement
- ⏰ **Filtrage par âge** : Scrape uniquement les nouvelles annonces
- 🔒 **Support proxy** : Évite les blocages Datadome
- 📈 **Statistiques détaillées** : Suivi complet du scraping

### 🎨 Interface
- 💻 **Script CLI** : Déploiement Apify ou exécution locale
- 🖥️ **Interface Streamlit** : PoC interactif pour tests
- ⚙️ **Configuration JSON** : Paramétrage flexible et reproductible

### 🚀 Production Ready
- ✅ Code robuste avec gestion d'erreurs avancée
- ✅ Logging détaillé pour monitoring
- ✅ Sauvegarde incrémentale des données
- ✅ Optimisé pour Apify platform
- ✅ Architecture modulaire et maintenable

## 📦 Structure du projet

```
leboncoin_scraper/
├── main.py                      # Script principal (Apify ready)
├── ui.py                        # Interface Streamlit
├── requirements.txt             # Dépendances Python
├── Dockerfile                   # Container Apify
├── USAGE.md                     # Guide d'utilisation détaillé
├── README.md                    # Ce fichier
├── config_examples.json         # Configurations prêtes à l'emploi
├── apify_input_example.json     # Exemple d'input Apify
└── .actor/                      # Configuration Apify
    ├── actor.json               # Métadonnées actor
    └── input_schema.json        # Schéma d'input UI
```

## 🚀 Installation

```bash
# Cloner le projet
cd /path/to/leboncoin_scraper

# Installer les dépendances
pip install -r requirements.txt
```

## 💻 Utilisation

### 1️⃣ Interface Streamlit (PoC)

```bash
streamlit run ui.py
```

L'interface web s'ouvre automatiquement avec :
- Configuration interactive
- Prévisualisation des paramètres
- Lancement du scraping
- Visualisation des résultats
- Export JSON/CSV

### 2️⃣ Ligne de commande (Local)

Créez `apify_input.json` :

```json
{
  "search_text": "maison",
  "category": "IMMOBILIER_VENTES_IMMOBILIERES",
  "location_type": "department",
  "locations": [{"code": "75"}],
  "max_pages": 5,
  "output_format": "detailed"
}
```

Exécutez :

```bash
python main.py
```

Résultats dans `scraper_results.json` et `apify_output.json`.

### 3️⃣ Déploiement Apify

```bash
# Via Apify CLI
apify login
apify push

# Ou via GitHub integration
git push origin main
```

## 📋 Exemples de configurations

### Immobilier Paris

```json
{
  "search_text": "appartement",
  "category": "IMMOBILIER_VENTES_IMMOBILIERES",
  "location_type": "department",
  "locations": [{"code": "75"}],
  "filters": {
    "square": [50, 100],
    "rooms": [2, 4]
  },
  "price_min": 300000,
  "price_max": 600000,
  "max_pages": 5
}
```

### Voitures Île-de-France

```json
{
  "category": "VEHICULES_VOITURES",
  "location_type": "region",
  "locations": [{"name": "ILE_DE_FRANCE"}],
  "filters": {
    "mileage": [0, 100000]
  },
  "price_min": 5000,
  "price_max": 20000,
  "sort": "PRICE_ASC"
}
```

### Emploi Développeur

```json
{
  "search_text": "développeur python",
  "category": "EMPLOI_OFFRES_DEMPLOI",
  "search_in_title_only": true,
  "max_age_days": 2,
  "max_pages": 3
}
```

**Plus d'exemples** : Voir `config_examples.json`

## 🎯 Catégories supportées

Toutes les catégories Leboncoin sont disponibles :

| Catégorie | Code |
|-----------|------|
| Toutes catégories | `TOUTES_CATEGORIES` |
| Ventes immobilières | `IMMOBILIER_VENTES_IMMOBILIERES` |
| Locations | `IMMOBILIER_LOCATIONS` |
| Voitures | `VEHICULES_VOITURES` |
| Motos | `VEHICULES_MOTOS` |
| Emploi | `EMPLOI_OFFRES_DEMPLOI` |
| Ordinateurs | `ELECTRONIQUE_ORDINATEURS` |
| Téléphones | `ELECTRONIQUE_TELEPHONES_ET_OBJETS_CONNECTES` |
| Ameublement | `MAISON_ET_JARDIN_AMEUBLEMENT` |
| ... | *Et bien d'autres* |

Voir la bibliothèque [lbc](https://github.com/etienne-hd/lbc) pour la liste complète.

## 🌍 Types de localisation

### France entière
```json
{"location_type": "none", "locations": []}
```

### Département(s)
```json
{
  "location_type": "department",
  "locations": [{"code": "75"}, {"code": "92"}]
}
```

### Région(s)
```json
{
  "location_type": "region",
  "locations": [{"name": "ILE_DE_FRANCE"}]
}
```

### Ville(s) avec rayon
```json
{
  "location_type": "city",
  "locations": [{
    "name": "Paris",
    "lat": 48.8566,
    "lng": 2.3522,
    "radius": 10000
  }]
}
```

## 🔧 Filtres personnalisés

Les filtres varient selon la catégorie :

### Immobilier
```json
{
  "real_estate_type": ["1"],        // 1=maison, 2=appartement
  "square": [100, 200],              // Surface habitable (m²)
  "rooms": [3, 5],                   // Nombre de pièces
  "land_plot_surface": [300, 1000], // Terrain (m²)
  "energy_rate": ["a", "b", "c"]    // DPE (a-g)
}
```

### Véhicules
```json
{
  "mileage": [0, 100000],   // Kilométrage
  "fuel": ["1", "2"],       // 1=essence, 2=diesel
  "regdate": [2018, 2023]   // Année de première immatriculation
}
```

## 📊 Format de sortie

### Mode "detailed"
Tous les champs disponibles : id, url, subject, body, price, dates, location complète, attributes, images, etc.

### Mode "compact"
Champs essentiels uniquement : id, url, subject, price, city, zipcode, date

## ⚙️ Configuration avancée

### Pagination
- `max_pages` : Nombre de pages max (0 = illimité)
- `limit_per_page` : Résultats par page (max 35)
- `delay_between_pages` : Délai entre pages (secondes)
- `delay_between_locations` : Délai entre localisations

### Filtrage temporel
- `max_age_days` : Âge max des annonces en jours (0 = désactivé)
- `consecutive_old_limit` : Arrêt après N annonces anciennes consécutives

### Proxy
```json
{
  "proxy_host": "proxy.example.com",
  "proxy_port": 8080,
  "proxy_username": "user",
  "proxy_password": "pass"
}
```

## 📈 Statistiques

Le scraper génère des statistiques complètes :

- `total_ads` : Nombre total d'annonces trouvées
- `unique_ads` : Annonces uniques (sans doublons)
- `duplicates` : Nombre de duplicatas détectés
- `pages_processed` : Pages scrapées
- `locations_processed` : Localisations traitées
- `errors` : Nombre d'erreurs rencontrées

## 🛠️ Résolution de problèmes

### Erreur 403 (Datadome)
**Solution** : Utilisez un proxy français propre
```json
{"proxy_host": "proxy.fr", "proxy_port": 8080}
```

### Pas de résultats
**Vérifications** :
- Catégorie valide
- Filtres pas trop restrictifs
- Location existe
- `max_age_days` pas trop strict

### Scraping lent
**Optimisations** :
- Réduire `delay_between_pages`
- Limiter `max_pages`
- Mode `compact`
- Filtrer par `max_age_days`

## 📚 Documentation

- **[USAGE.md](USAGE.md)** : Guide d'utilisation détaillé
- **[config_examples.json](config_examples.json)** : Configurations prêtes à l'emploi
- **[lbc library](https://github.com/etienne-hd/lbc)** : Documentation de la bibliothèque

## 🏗️ Architecture

### Composants principaux

1. **ApifyAdapter** : Intégration Apify avec fallback local
2. **Config** : Configuration dynamique depuis input
3. **EnumMapper** : Conversion chaînes → enums lbc
4. **LocationBuilder** : Construction d'objets de localisation
5. **DataProcessor** : Traitement et transformation de données
6. **AdTransformer** : Formatage des annonces
7. **ScraperEngine** : Moteur de scraping principal

### Flux d'exécution

```
Input → Config → Client Init → Location Build → 
Scraping Loop → Data Transform → Dedup → 
Output (Dataset/File) → Stats
```

## 🤝 Contributions

Ce projet utilise la bibliothèque [lbc](https://github.com/etienne-hd/lbc) d'Etienne Hodé.

## 📄 Licence

MIT License - Voir LICENSE pour plus de détails

## ⚠️ Avertissement

Ce scraper est fourni à des fins éducatives et de recherche. L'utilisation intensive peut entraîner des blocages. Respectez les conditions d'utilisation de Leboncoin et utilisez des proxies appropriés.

---

**Créé avec ❤️ pour automatiser le scraping Leboncoin**

