# 📚 Référence complète des catégories et filtres Leboncoin

## 🎯 Catégories principales

### Toutes catégories
```
TOUTES_CATEGORIES
```

## 🏠 Immobilier

| Code | Description |
|------|-------------|
| `IMMOBILIER` | Immobilier (général) |
| `IMMOBILIER_VENTES_IMMOBILIERES` | Ventes immobilières |
| `IMMOBILIER_LOCATIONS` | Locations |
| `IMMOBILIER_COLOCATIONS` | Colocations |
| `IMMOBILIER_BUREAUX_ET_COMMERCES` | Bureaux et commerces |
| `IMMOBILIER_IMMOBILIER_NEUF` | Immobilier neuf |
| `IMMOBILIER_SERVICES_DE_DEMENAGEMENT` | Services de déménagement |

### Filtres immobilier
```json
{
  "real_estate_type": ["1", "2", "3", "4"],
  // 1=maison, 2=appartement, 3=terrain, 4=parking/box
  
  "square": [50, 150],              // Surface habitable (m²)
  "land_plot_surface": [100, 500],  // Surface terrain (m²)
  "rooms": [2, 5],                  // Nombre de pièces
  "bedrooms": [1, 3],               // Nombre de chambres
  
  "energy_rate": ["a", "b", "c", "d", "e", "f", "g"],  // DPE
  "ges": ["a", "b", "c", "d", "e"],                     // GES
  
  "furnished": ["1", "2"],          // 1=meublé, 2=non meublé
  "outside_access": ["garden", "terrace", "balcony"],
  "orientation": ["north", "south", "east", "west"]
}
```

## 🏖️ Locations de vacances

| Code | Description |
|------|-------------|
| `LOCATIONS_DE_VACANCES` | Locations de vacances |
| `LOCATIONS_DE_VACANCES_LOCATIONS_SAISONNIERES` | Locations saisonnières |

## 🚗 Véhicules

| Code | Description |
|------|-------------|
| `VEHICULES` | Véhicules (général) |
| `VEHICULES_VOITURES` | Voitures |
| `VEHICULES_MOTOS` | Motos |
| `VEHICULES_CARAVANING` | Caravaning |
| `VEHICULES_UTILITAIRES` | Utilitaires |
| `VEHICULES_CAMIONS` | Camions |
| `VEHICULES_NAUTISME` | Nautisme |
| `VEHICULES_VELOS` | Vélos |
| `VEHICULES_EQUIPEMENT_AUTO` | Équipement auto |
| `VEHICULES_EQUIPEMENT_MOTO` | Équipement moto |
| `VEHICULES_EQUIPEMENT_CARAVANING` | Équipement caravaning |
| `VEHICULES_EQUIPEMENT_NAUTISME` | Équipement nautisme |
| `VEHICULES_EQUIPEMENTS_VELOS` | Équipements vélos |
| `VEHICULES_SERVICES_DE_REPARATIONS_MECANIQUES` | Services de réparations |

### Filtres véhicules
```json
{
  "mileage": [0, 100000],           // Kilométrage
  "regdate": [2015, 2023],          // Année
  "fuel": ["1", "2", "3", "4", "5", "6"],
  // 1=essence, 2=diesel, 3=GPL, 4=électrique, 5=hybride, 6=autre
  
  "gearbox": ["1", "2"],            // 1=manuelle, 2=automatique
  "cubic_capacity": [1000, 2000],   // Cylindrée (cm³)
  "horse_power_din": [50, 200],     // Puissance (CV)
  
  "model": "308",                   // Modèle
  "brand": "peugeot"                // Marque
}
```

## 💼 Emploi

| Code | Description |
|------|-------------|
| `EMPLOI` | Emploi (général) |
| `EMPLOI_OFFRES_DEMPLOI` | Offres d'emploi |
| `EMPLOI_FORMATIONS_PROFESSIONNELLES` | Formations professionnelles |

### Filtres emploi
```json
{
  "job_type": ["1", "2", "3", "4"],
  // 1=CDI, 2=CDD, 3=Stage, 4=Alternance
  
  "salary": [25000, 50000],         // Salaire annuel
  "experience": ["1", "2", "3"],     // 1=débutant, 2=confirmé, 3=expert
  "contract_type": ["full_time", "part_time"],
  "remote": ["1"]                    // 1=télétravail possible
}
```

## 💻 Électronique

| Code | Description |
|------|-------------|
| `ELECTRONIQUE` | Électronique (général) |
| `ELECTRONIQUE_ORDINATEURS` | Ordinateurs |
| `ELECTRONIQUE_ACCESSOIRES_INFORMATIQUE` | Accessoires informatique |
| `ELECTRONIQUE_TABLETTES_ET_LISEUSES` | Tablettes et liseuses |
| `ELECTRONIQUE_PHOTO_AUDIO_ET_VIDEO` | Photo, audio et vidéo |
| `ELECTRONIQUE_TELEPHONES_ET_OBJETS_CONNECTES` | Téléphones et objets connectés |
| `ELECTRONIQUE_ACCESSOIRES_TELEPHONE_ET_OBJETS_CONNECTES` | Accessoires téléphone |
| `ELECTRONIQUE_CONSOLES` | Consoles |
| `ELECTRONIQUE_JEUX_VIDEO` | Jeux vidéo |
| `ELECTRONIQUE_ELECTROMENAGER` | Électroménager |
| `ELECTRONIQUE_SERVICES_DE_REPARATIONS_ELECTRONIQUES` | Services de réparations |

### Filtres électronique
```json
{
  "brand": "apple",                 // Marque
  "model": "iphone 13",             // Modèle
  "storage_capacity": ["64", "128", "256"],  // Stockage (Go)
  "ram": ["8", "16", "32"],         // RAM (Go)
  "processor": "i7",                // Processeur
  "screen_size": [13, 15]           // Taille écran (pouces)
}
```

## 🏡 Maison et jardin

| Code | Description |
|------|-------------|
| `MAISON_ET_JARDIN` | Maison et jardin (général) |
| `MAISON_ET_JARDIN_AMEUBLEMENT` | Ameublement |
| `MAISON_ET_JARDIN_PAPETERIE_ET_FOURNITURES_SCOLAIRES` | Papeterie |
| `MAISON_ET_JARDIN_ELECTROMENAGER` | Électroménager |
| `MAISON_ET_JARDIN_ARTS_DE_LA_TABLE` | Arts de la table |
| `MAISON_ET_JARDIN_DECORATION` | Décoration |
| `MAISON_ET_JARDIN_LINGE_DE_MAISON` | Linge de maison |
| `MAISON_ET_JARDIN_BRICOLAGE` | Bricolage |
| `MAISON_ET_JARDIN_JARDIN_ET_PLANTES` | Jardin et plantes |
| `MAISON_ET_JARDIN_SERVICES_DE_JARDINERIE_ET_BRICOLAGE` | Services jardinerie |

## 👶 Famille

| Code | Description |
|------|-------------|
| `FAMILLE` | Famille (général) |
| `FAMILLE_EQUIPEMENT_BEBE` | Équipement bébé |
| `FAMILLE_MOBILIER_ENFANT` | Mobilier enfant |
| `FAMILLE_VETEMENTS_BEBE` | Vêtements bébé |

## 🎮 Loisirs

| Code | Description |
|------|-------------|
| `LOISIRS` | Loisirs (général) |
| `LOISIRS_SPORTS_ET_HOBBIES` | Sports et hobbies |
| `LOISIRS_VELOS` | Vélos |
| `LOISIRS_SPORTS_DHIVER` | Sports d'hiver |
| `LOISIRS_COLLECTION` | Collection |
| `LOISIRS_INSTRUMENTS_DE_MUSIQUE` | Instruments de musique |
| `LOISIRS_LIVRES` | Livres |
| `LOISIRS_CD_VINYLES` | CD/Vinyles |
| `LOISIRS_DVD_FILMS` | DVD/Films |

## 👔 Mode

| Code | Description |
|------|-------------|
| `MODE_ET_VETEMENTS` | Mode et vêtements |
| `MODE_VETEMENTS` | Vêtements |
| `MODE_CHAUSSURES` | Chaussures |
| `MODE_ACCESSOIRES` | Accessoires |
| `MODE_MONTRES_ET_BIJOUX` | Montres et bijoux |
| `MODE_BAGAGERIE` | Bagagerie |

## 🐾 Animaux

| Code | Description |
|------|-------------|
| `ANIMAUX` | Animaux |

## 🏢 Services

| Code | Description |
|------|-------------|
| `SERVICES` | Services (général) |
| `SERVICES_PRESTATIONS_DE_SERVICES` | Prestations de services |
| `SERVICES_BILLETTERIE` | Billetterie |
| `SERVICES_EVENEMENTS` | Événements |
| `SERVICES_COURS_PARTICULIERS` | Cours particuliers |

## 🎁 Divers

| Code | Description |
|------|-------------|
| `AUTRES` | Autres |

## 🔧 Paramètres généraux (toutes catégories)

### Tri (sort)
```
NEWEST          - Plus récentes
RELEVANCE       - Plus pertinentes
PRICE_ASC       - Prix croissant
PRICE_DESC      - Prix décroissant
```

### Type d'annonce (ad_type)
```
OFFER           - Offres (ventes)
DEMAND          - Demandes (recherches)
```

### Type de vendeur (owner_type)
```
PRIVATE         - Particulier
PRO             - Professionnel
ALL             - Tous (ne pas spécifier)
```

## 📍 Localisations

### Par département
```json
{
  "location_type": "department",
  "locations": [
    {"code": "75"},   // Paris
    {"code": "69"},   // Rhône
    {"code": "13"}    // Bouches-du-Rhône
  ]
}
```

Liste complète : d_1 à d_95 (sauf d_20 → d_2A et d_2B pour Corse)

### Par région
```json
{
  "location_type": "region",
  "locations": [
    {"name": "ILE_DE_FRANCE"},
    {"name": "AUVERGNE_RHONE_ALPES"},
    {"name": "NOUVELLE_AQUITAINE"}
  ]
}
```

Régions disponibles :
- `ILE_DE_FRANCE`
- `AUVERGNE_RHONE_ALPES`
- `BOURGOGNE_FRANCHE_COMTE`
- `BRETAGNE`
- `CENTRE_VAL_DE_LOIRE`
- `CORSE`
- `GRAND_EST`
- `HAUTS_DE_FRANCE`
- `NORMANDIE`
- `NOUVELLE_AQUITAINE`
- `OCCITANIE`
- `PAYS_DE_LA_LOIRE`
- `PROVENCE_ALPES_COTE_DAZUR`

### Par ville
```json
{
  "location_type": "city",
  "locations": [{
    "name": "Paris",
    "lat": 48.8566,
    "lng": 2.3522,
    "radius": 10000  // en mètres
  }]
}
```

## 💡 Exemples de configurations complètes

### 1. Appartements Paris avec DPE
```json
{
  "category": "IMMOBILIER_VENTES_IMMOBILIERES",
  "location_type": "department",
  "locations": [{"code": "75"}],
  "filters": {
    "real_estate_type": ["2"],
    "square": [50, 80],
    "rooms": [2, 3],
    "energy_rate": ["a", "b", "c"]
  },
  "price_min": 300000,
  "price_max": 500000,
  "sort": "NEWEST"
}
```

### 2. Voitures électriques Île-de-France
```json
{
  "category": "VEHICULES_VOITURES",
  "location_type": "region",
  "locations": [{"name": "ILE_DE_FRANCE"}],
  "filters": {
    "fuel": ["4"],
    "mileage": [0, 50000],
    "regdate": [2020, 2024]
  },
  "price_min": 15000,
  "price_max": 35000,
  "sort": "PRICE_ASC"
}
```

### 3. Emplois CDI développeur
```json
{
  "search_text": "développeur python",
  "category": "EMPLOI_OFFRES_DEMPLOI",
  "location_type": "none",
  "filters": {
    "job_type": ["1"],
    "remote": ["1"]
  },
  "search_in_title_only": true,
  "max_age_days": 7
}
```

### 4. iPhone occasion
```json
{
  "search_text": "iphone",
  "category": "ELECTRONIQUE_TELEPHONES_ET_OBJETS_CONNECTES",
  "location_type": "none",
  "filters": {
    "brand": "apple",
    "storage_capacity": ["128", "256"]
  },
  "price_min": 300,
  "price_max": 800,
  "owner_type": "PRIVATE",
  "sort": "PRICE_ASC"
}
```

## 🔍 Découvrir les filtres disponibles

Pour découvrir les filtres d'une catégorie :

1. Aller sur leboncoin.fr
2. Faire une recherche dans la catégorie
3. Appliquer des filtres
4. Observer l'URL : `...&filter_name=value&...`
5. Utiliser ces noms dans la section `filters`

Exemple d'URL :
```
https://www.leboncoin.fr/recherche?
  category=9&
  real_estate_type=1&
  square=100-200&
  rooms=3-5&
  energy_rate=a,b,c
```

Devient :
```json
{
  "category": "IMMOBILIER_VENTES_IMMOBILIERES",
  "filters": {
    "real_estate_type": ["1"],
    "square": [100, 200],
    "rooms": [3, 5],
    "energy_rate": ["a", "b", "c"]
  }
}
```

## 📞 Support

Pour toute question sur les catégories et filtres :
- Consulter ce document
- Tester avec l'interface Streamlit (`ui.py`)
- Voir les exemples dans `config_examples.json`
- Consulter la doc lbc : https://github.com/etienne-hd/lbc

---

**Note** : Les valeurs des filtres peuvent évoluer. Ce document est à jour au 22/10/2025.

