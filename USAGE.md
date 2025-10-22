# Guide d'utilisation - Leboncoin Universal Scraper

## 🚀 Démarrage rapide

### 1. Installation des dépendances

```bash
pip install -r requirements.txt
```

### 2. Utilisation avec Streamlit (PoC)

```bash
streamlit run ui.py
```

L'interface web s'ouvrira automatiquement dans votre navigateur.

### 3. Utilisation en ligne de commande (local)

Créez un fichier `apify_input.json` avec votre configuration :

```json
{
  "search_text": "maison",
  "category": "IMMOBILIER",
  "location_type": "department",
  "locations": [{"code": "75"}],
  "max_pages": 5
}
```

Lancez le scraper :

```bash
python main.py
```

Les résultats seront dans `scraper_results.json` et `apify_output.json`.

## 📋 Configuration

### Catégories disponibles

Toutes les catégories Leboncoin sont supportées :

- `TOUTES_CATEGORIES` - Toutes les catégories
- `IMMOBILIER_VENTES_IMMOBILIERES` - Ventes immobilières
- `IMMOBILIER_LOCATIONS` - Locations
- `VEHICULES_VOITURES` - Voitures
- `VEHICULES_MOTOS` - Motos
- `EMPLOI_OFFRES_DEMPLOI` - Offres d'emploi
- `ELECTRONIQUE_ORDINATEURS` - Ordinateurs
- etc. (voir `lbc.Category` pour la liste complète)

### Types de localisation

#### 1. Aucune (France entière)
```json
{
  "location_type": "none",
  "locations": []
}
```

#### 2. Par département
```json
{
  "location_type": "department",
  "locations": [
    {"code": "75"},
    {"code": "92"}
  ]
}
```

#### 3. Par région
```json
{
  "location_type": "region",
  "locations": [
    {"name": "ILE_DE_FRANCE"},
    {"name": "BRETAGNE"}
  ]
}
```

#### 4. Par ville
```json
{
  "location_type": "city",
  "locations": [
    {
      "name": "Paris",
      "lat": 48.8566,
      "lng": 2.3522,
      "radius": 10000
    }
  ]
}
```

### Filtres personnalisés

Selon la catégorie, ajoutez des filtres spécifiques :

#### Immobilier
```json
{
  "filters": {
    "real_estate_type": ["1"],        // 1=maison, 2=appartement
    "square": [100, 200],              // Surface 100-200 m²
    "rooms": [3, 5],                   // 3-5 pièces
    "land_plot_surface": [300, 1000], // Terrain 300-1000 m²
    "energy_rate": ["a", "b", "c"]    // DPE A, B, C
  }
}
```

#### Véhicules
```json
{
  "filters": {
    "mileage": [0, 100000],   // Kilométrage 0-100k
    "fuel": ["1", "2"],       // 1=essence, 2=diesel
    "regdate": [2018, 2023]   // Année 2018-2023
  }
}
```

### Options de scraping

```json
{
  "max_pages": 10,                    // Pages max (0=illimité)
  "delay_between_pages": 1,           // Délai entre pages (secondes)
  "delay_between_locations": 2,       // Délai entre localisations
  "max_age_days": 7,                  // Âge max des annonces (0=désactivé)
  "consecutive_old_limit": 5,         // Seuil d'arrêt (annonces anciennes)
  "output_format": "detailed"         // "detailed" ou "compact"
}
```

### Proxy

```json
{
  "proxy_host": "proxy.example.com",
  "proxy_port": 8080,
  "proxy_username": "user",
  "proxy_password": "pass"
}
```

## 🎯 Exemples de configurations

Voir `config_examples.json` pour des configurations prêtes à l'emploi :

1. **immobilier_paris** - Appartements à Paris
2. **voitures_ile_de_france** - Voitures en IdF
3. **emploi_informatique** - Jobs informatique
4. **electronique_france** - Électronique nationale
5. **immobilier_complet** - Scraping immobilier DPE

### Utiliser un exemple

```bash
# Extraire une config exemple
cat config_examples.json | jq '.immobilier_paris.config' > apify_input.json

# Lancer
python main.py
```

## 📊 Format de sortie

### Mode "detailed"

```json
{
  "id": "2456789123",
  "url": "https://www.leboncoin.fr/...",
  "subject": "Belle maison avec jardin",
  "body": "Description complète...",
  "price": 450000,
  "price_formatted": "450000€",
  "first_publication_date": "2025-10-20 14:30:00",
  "index_date": "2025-10-22 09:15:00",
  "scraped_at": "2025-10-22 10:00:00",
  "city": "Paris",
  "zipcode": "75001",
  "department_name": "Paris",
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

### Mode "compact"

```json
{
  "id": "2456789123",
  "url": "https://www.leboncoin.fr/...",
  "subject": "Belle maison avec jardin",
  "price": 450000,
  "city": "Paris",
  "zipcode": "75001",
  "index_date": "2025-10-22 09:15:00",
  "scraped_at": "2025-10-22 10:00:00"
}
```

## 🐳 Déploiement sur Apify

### 1. Préparer le projet

Fichiers nécessaires pour Apify :
- `main.py` - Script principal
- `requirements.txt` - Dépendances
- `.actor/` - Configuration Apify (à créer)

### 2. Structure Apify

Créez `.actor/actor.json` :

```json
{
  "actorSpecification": 1,
  "name": "leboncoin-universal-scraper",
  "version": "1.0.0",
  "buildTag": "latest",
  "environmentVariables": {},
  "dockerfile": "./Dockerfile",
  "readme": "./README.md",
  "input": "./input_schema.json"
}
```

### 3. Input Schema

Créez `.actor/input_schema.json` pour définir l'interface Apify.

### 4. Déploiement

```bash
# Via Apify CLI
apify login
apify push

# Ou via GitHub integration
git push origin main
```

## 💡 Conseils & Astuces

### Performance

1. **Utiliser des proxies** pour éviter les blocages (Datadome)
2. **Augmenter les délais** si vous rencontrez des 403
3. **Limiter les pages** pour des tests rapides
4. **Mode compact** pour économiser l'espace

### Filtrage intelligent

1. **max_age_days** : Scraper uniquement les nouvelles annonces
2. **consecutive_old_limit** : Arrêt automatique quand plus de nouvelles annonces
3. **search_in_title_only** : Recherche plus précise

### Scraping par lots

Pour scraper tous les départements :

```python
# Générer locations pour tous les départements
locations = [{"code": str(i).zfill(2)} for i in range(1, 96) if i != 20]
locations.extend([{"code": "2A"}, {"code": "2B"}])
```

### Déduplication

Le scraper gère automatiquement :
- Les doublons dans une même exécution
- Comptage des duplicatas dans les stats

## 🛠️ Troubleshooting

### Erreur 403 (Datadome)

**Solution** : Utilisez un proxy français propre
```json
{
  "proxy_host": "your-proxy.com",
  "proxy_port": 8080
}
```

### Pas de résultats

**Vérifications** :
1. Catégorie valide ?
2. Filtres trop restrictifs ?
3. Location existe ?
4. `max_age_days` trop strict ?

### Import Error

**Solution** : Vérifier l'installation
```bash
pip install -r requirements.txt --upgrade
```

### Scraping lent

**Optimisations** :
1. Réduire `delay_between_pages`
2. Limiter `max_pages`
3. Utiliser mode `compact`
4. Filtrer par `max_age_days`

## 📞 Support

Pour toute question sur l'utilisation, consultez :
1. Ce guide
2. `config_examples.json` pour des exemples
3. Interface Streamlit pour tester interactivement
4. Documentation de la lib `lbc` : https://github.com/etienne-hd/lbc

