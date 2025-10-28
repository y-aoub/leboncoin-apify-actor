# Leboncoin Scraper

Extrayez des données structurées depuis Leboncoin.fr avec support de toutes les catégories, filtrage avancé et exports JSON/CSV.

## Ce que fait cet outil

Ce scraper collecte automatiquement les annonces depuis Leboncoin selon vos critères de recherche. Il gère la pagination, élimine les doublons et exporte les données dans un format exploitable.

**Catégories supportées :**
- Immobilier (ventes, locations, colocations)
- Véhicules (voitures, motos, utilitaires, vélos)
- Emploi (offres, formations)
- Électronique (ordinateurs, téléphones, consoles)
- Maison & Jardin
- Mode & Vêtements
- Loisirs & Sports
- Services
- Et toutes les autres catégories

## Configuration

### Paramètres obligatoires

| Champ | Description | Valeurs possibles |
|-------|-------------|-------------------|
| **Category** | Catégorie à scraper | `IMMOBILIER_VENTES_IMMOBILIERES`, `VEHICULES_VOITURES`, `EMPLOI_OFFRES_DEMPLOI`, etc. |

### Paramètres de localisation

| Champ | Description | Exemple |
|-------|-------------|---------|
| **Location type** | Type de zone géographique | `city`, `department`, `region`, `none` |
| **Locations** | Liste des localisations | `[{"code": "75"}]` pour département, `[{"name": "Paris", "lat": 48.8566, "lng": 2.3522, "radius": 10000}]` pour ville |

### Filtres

| Champ | Description | Exemple |
|-------|-------------|---------|
| **Search text** | Mots-clés de recherche | `"appartement"`, `"iphone 13"` |
| **Price min/max** | Fourchette de prix en € | Min: `100000`, Max: `500000` |
| **Sort** | Ordre de tri | `NEWEST`, `RELEVANCE`, `PRICE_ASC`, `PRICE_DESC` |
| **Ad type** | Type d'annonce | `OFFER` (offre), `DEMAND` (demande) |
| **Owner type** | Type de vendeur | `PRIVATE`, `PRO`, ou vide pour tous |
| **Filters** | Filtres spécifiques par catégorie | Voir exemples ci-dessous |

### Options avancées

| Champ | Description | Défaut |
|-------|-------------|--------|
| **Max pages** | Nombre maximum de pages (0 = toutes les pages, illimité) | `10` |
| **Max age days** | Âge maximum des annonces en jours (0 = tous) | `0` |
| **Output format** | Format de sortie | `detailed` (complet) ou `compact` (essentiel) |
| **Delay between pages** | Délai entre pages en secondes | `1` |

## Exemples de configuration

### Exemple 1 : Recherche simple

Chercher des voitures en Île-de-France :

```json
{
  "category": "VEHICULES_VOITURES",
  "location_type": "region",
  "locations": [{"name": "ILE_DE_FRANCE"}],
  "price_min": 5000,
  "price_max": 20000,
  "max_pages": 5
}
```

### Exemple 2 : Recherche avec filtres avancés

Appartements à Paris avec critères spécifiques :

```json
{
  "category": "IMMOBILIER_VENTES_IMMOBILIERES",
  "location_type": "department",
  "locations": [{"code": "75"}],
  "price_min": 300000,
  "price_max": 600000,
  "filters": {
    "real_estate_type": ["2"],
    "square": [50, 100],
    "rooms": [2, 4]
  },
  "max_pages": 10
}
```

### Exemple 3 : Recherche par mots-clés

Offres d'emploi avec mots-clés :

```json
{
  "category": "EMPLOI_OFFRES_DEMPLOI",
  "search_text": "développeur",
  "search_in_title_only": true,
  "location_type": "none",
  "max_pages": 3
}
```

### Exemple 4 : Recherche géolocalisée

Dans une ville avec rayon de recherche :

```json
{
  "category": "TOUTES_CATEGORIES",
  "location_type": "city",
  "locations": [{
    "name": "Lyon",
    "lat": 45.764043,
    "lng": 4.835659,
    "radius": 15000
  }],
  "max_pages": 5
}
```

## Filtres par catégorie

### Immobilier

```json
{
  "real_estate_type": ["1"],     // 1=maison, 2=appartement, 3=terrain
  "square": [100, 200],           // Surface habitable (m²)
  "land_plot_surface": [300, 1000], // Surface terrain (m²)
  "rooms": [3, 5],                // Nombre de pièces
  "bedrooms": [2, 3],             // Nombre de chambres
  "energy_rate": ["a", "b", "c"]  // DPE
}
```

### Véhicules

```json
{
  "mileage": [0, 100000],         // Kilométrage
  "regdate": [2018, 2023],        // Année
  "fuel": ["1", "2"],             // 1=essence, 2=diesel, 4=électrique
  "gearbox": ["1", "2"]           // 1=manuelle, 2=automatique
}
```

### Électronique

```json
{
  "storage_capacity": ["128", "256"], // Stockage (Go)
  "ram": ["8", "16"]                  // RAM (Go)
}
```

## Données extraites

### Format détaillé

**Structure aplatie (un seul niveau de profondeur)** :

```json
{
  "id": "2456789123",
  "url": "https://www.leboncoin.fr/...",
  "title": "Titre de l'annonce",
  "subject": "Titre de l'annonce",
  "body": "Description complète",
  
  "category_id": "9",
  "category_name": "Ventes immobilières",
  
  "price": 450000,
  
  "ad_type": "offer",
  "status": "active",
  
  "first_publication_date": "2025-10-20 14:30:00",
  "index_date": "2025-10-22 09:15:00",
  "scraped_at": "2025-10-22 12:00:00",
  
  "has_phone": true,
  
  "city": "Paris",
  "zipcode": "75001",
  "department_id": "75",
  "department_name": "Paris",
  "region_name": "Île-de-France",
  "latitude": 48.8566,
  "longitude": 2.3522,
  
  "images": ["url1", "url2", "url3"],
  "image_count": 3,
  
  "user_id": "abc123",
  "user_name": "Jean Dupont",
  "user_is_pro": false,
  "user_registered_at": "2020-01-15 10:00:00",
  "user_total_ads": 3,
  
  "attribute_square": "120",
  "attribute_rooms": "4",
  "attribute_energy_rate": "B",
  "attribute_condition": "good",
  "attribute_shippable": "true",
  
  "search_category": "IMMOBILIER_VENTES_IMMOBILIERES",
  "search_location": "Paris"
}
```

### Champs extraits

**Structure aplatie : tous les champs au même niveau**

**Informations de base :**
- `id`, `url`, `title`, `subject`, `body`
- `category_id`, `category_name`
- `price`
- `ad_type`, `status`

**Dates :**
- `first_publication_date` : Date de première publication
- `index_date` : Date d'indexation
- `scraped_at` : Date d'extraction

**Contact :**
- `has_phone` : Numéro de téléphone disponible

**Localisation :**
- `city`, `zipcode`
- `department_id`, `department_name`
- `region_name`
- `latitude`, `longitude`

**Médias :**
- `images` : Liste des URLs des images
- `image_count` : Nombre d'images

**Vendeur (préfixe `user_`) :**
- `user_id` : ID du vendeur
- `user_name` : Nom du vendeur
- `user_is_pro` : Professionnel ou particulier
- `user_registered_at` : Date d'inscription
- `user_total_ads` : Nombre total d'annonces

**Attributs spécifiques (préfixe `attribute_`) :**
- `attribute_square` : Surface (immobilier)
- `attribute_rooms` : Nombre de pièces (immobilier)
- `attribute_energy_rate` : DPE (immobilier)
- `attribute_mileage` : Kilométrage (véhicules)
- `attribute_regdate` : Année (véhicules)
- `attribute_fuel` : Carburant (véhicules)
- `attribute_condition` : État du produit
- `attribute_shippable` : Livraison disponible
- `attribute_shipping_type` : Type de livraison
- Et tous les autres attributs spécifiques à chaque catégorie...

**Contexte de recherche :**
- `search_category` : Catégorie recherchée
- `search_location` : Localisation recherchée

> **Note :** 
> - Structure complètement aplatie : **aucun dictionnaire imbriqué**
> - Les champs techniques internes sont automatiquement filtrés
> - Format idéal pour CSV, bases de données relationnelles et analyses

### Format compact

Version allégée avec informations essentielles (ID, URL, titre, prix, ville, date).

## Catégories disponibles

Liste des principales catégories (utilisez exactement ces valeurs) :

**Immobilier :**
- `IMMOBILIER_VENTES_IMMOBILIERES`
- `IMMOBILIER_LOCATIONS`
- `IMMOBILIER_COLOCATIONS`
- `IMMOBILIER_BUREAUX_ET_COMMERCES`

**Véhicules :**
- `VEHICULES_VOITURES`
- `VEHICULES_MOTOS`
- `VEHICULES_UTILITAIRES`
- `VEHICULES_CARAVANING`
- `VEHICULES_VELOS`

**Emploi :**
- `EMPLOI_OFFRES_DEMPLOI`
- `EMPLOI_FORMATIONS_PROFESSIONNELLES`

**Électronique :**
- `ELECTRONIQUE_ORDINATEURS`
- `ELECTRONIQUE_TELEPHONES_ET_OBJETS_CONNECTES`
- `ELECTRONIQUE_CONSOLES`

**Autres :**
- `MAISON_ET_JARDIN_AMEUBLEMENT`
- `MODE_VETEMENTS`
- `LOISIRS_SPORTS_ET_HOBBIES`
- `TOUTES_CATEGORIES`

Liste complète : voir l'onglet "Input" de l'Actor.

## Performance et limites

### Vitesse

- **Environ 100-200 annonces par minute** selon les délais configurés
- Plus le délai entre pages est grand, plus c'est lent mais stable

### Limites techniques

**Pagination :** Vous pouvez maintenant scraper un nombre illimité de pages. Pour de meilleures performances, affinez vos filtres (par département, prix, etc.).

**Blocages :** Pour de gros volumes ou une utilisation intensive, un proxy français est fortement recommandé (voir section Proxy ci-dessous).

**Données :** Seules les données publiquement visibles sont collectées. Les numéros de téléphone masqués ou les messages privés ne sont pas accessibles.

## Configuration proxy

Pour éviter les blocages lors d'un scraping intensif, utilisez des proxies :

### Apify Proxy (Recommandé)

L'Actor supporte nativement **Apify Proxy**. Dans l'interface :

1. Allez dans la section **"Proxy configuration"**
2. Activez **"Use Apify Proxy"**
3. Sélectionnez **"Residential"** (recommandé pour Leboncoin)
4. Pays : **France (FR)** pour de meilleurs résultats

**Préconfiguration par défaut :** Proxies résidentiels français activés.

### Proxies personnalisés

Vous pouvez aussi utiliser vos propres proxies :
- Sélectionnez "Custom proxies"
- Entrez vos URLs de proxy

### Pourquoi utiliser des proxies ?

- **Évite les blocages Datadome** sur Leboncoin
- **Augmente le taux de réussite** pour les gros volumes
- **Proxies résidentiels français** = meilleurs résultats (IP françaises)

**Note :** L'utilisation de proxies Apify consomme des crédits supplémentaires selon votre plan.

## Cas d'usage

**Analyse de marché :** Suivez les prix et tendances dans votre secteur

**Veille concurrentielle :** Surveillez les offres de vos concurrents

**Études immobilières :** Analysez les prix par zone et performance énergétique

**Lead generation :** Constituez des bases de données qualifiées

**Monitoring de prix :** Suivez l'évolution des prix d'un produit

## Support

Pour toute question ou problème :
1. Consultez l'onglet "Input" pour la liste complète des paramètres
2. Vérifiez les exemples de configuration ci-dessus
3. Contactez le support via l'onglet "Issues"

## Points d'attention

⚠️ **Utilisation responsable :** Cet outil collecte des données publiques. Respectez les conditions d'utilisation de Leboncoin et le RGPD dans votre traitement des données.

⚠️ **Pas d'affiliation :** Cet outil n'est pas affilié à Leboncoin.

⚠️ **Blocages possibles :** En cas d'utilisation intensive sans proxy, des blocages temporaires peuvent survenir. Dans ce cas, réduisez la fréquence ou ajoutez un proxy.

## Changelog

**v1.0.0 (Oct 2025)**
- Support de toutes les catégories Leboncoin
- Filtrage par ville, département, région
- Filtres personnalisés par catégorie
- Export JSON et CSV
- Déduplication automatique
- Gestion des erreurs

---

**Prêt à commencer ?** Configurez vos paramètres dans l'onglet "Input" et lancez l'extraction !
