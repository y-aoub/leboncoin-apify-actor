# 🏠 Leboncoin Scraper

**L'outil simple et puissant pour extraire toutes les annonces Leboncoin et transformer le marché français en données exploitables.**

---

## 💡 Pourquoi utiliser cet outil ?

Vous cherchez à analyser le marché, surveiller les prix, trouver des opportunités d'achat ou générer des leads ? 

**Avant** : Vous passiez des heures à parcourir manuellement des centaines de pages Leboncoin, à copier-coller des données, et à vous demander si vous avez bien tout vu.

**Maintenant** : En quelques clics, collectez automatiquement des milliers d'annonces structurées, filtrées selon vos critères exacts, et exportables en JSON ou CSV pour vos analyses.

### 🎯 Ce que vous pouvez faire

✅ **Analyse immobilière** - Mieux comprendre le marché immobilier dans votre région  
✅ **Monitoring de prix** - Suivre l'évolution des prix d'un produit spécifique  
✅ **Recherche d'opportunités** - Détecter les bonnes affaires avant les autres  
✅ **Veille concurrentielle** - Surveiller les annonces de vos concurrents  
✅ **Génération de leads** - Créer une base de données qualifiée automatiquement  
✅ **Étude de marché** - Obtenir des données pour vos analyses et rapports  

---

## 🚀 Démarrage rapide

### Méthode 1 : Via URL (le plus simple)

1. **Allez sur Leboncoin.fr** et faites une recherche normalement
2. **Copiez l'URL** de votre recherche (ex: `https://www.leboncoin.fr/recherche?category=9&locations=Paris&price=100000-300000`)
3. **Collez l'URL** dans l'outil
4. **Lancez** - Vous obtenez toutes les annonces en quelques minutes

C'est tout ! Vous n'avez pas besoin de comprendre les API ou les paramètres techniques.

### Méthode 2 : Configuration personnalisée

Pour plus de contrôle, vous pouvez configurer manuellement :

```json
{
  "direct_url": "https://www.leboncoin.fr/recherche?category=9&text=appartement&locations=Paris",
  "max_pages": 20,
  "output_format": "detailed"
}
```

---

## 📊 Exemples concrets

### Exemple 1 : Trouver des appartements abordables à Paris

**Objectif** : Identifier tous les appartements de 2-3 pièces à Paris entre 250 000€ et 400 000€

```json
{
  "direct_url": "https://www.leboncoin.fr/recherche?category=9&locations=Paris&price=250000-400000&rooms=2.0-4.0&real_estate_type=2",
  "max_pages": 0
}
```

**Résultat** : Export CSV avec tous les appartements correspondant à vos critères, incluant :
- Prix exact
- Surface
- Nombre de pièces
- Adresse complète
- Photos
- Coordonnées du vendeur
- Date de publication

### Exemple 2 : Surveiller les voitures électriques en région parisienne

**Objectif** : Tracker l'évolution du marché des voitures électriques d'occasion

```json
{
  "direct_url": "https://www.leboncoin.fr/recherche?category=2&locations=Paris__48.856614_2.3522219_10000&fuel=4&regdate=2020-2024",
  "max_pages": 50
}
```

**Résultat** : Base de données complète à exporter dans Excel pour créer des graphiques de tendance

### Exemple 3 : Chercher des opportunités professionnelles

**Objectif** : Trouver tous les postes de développeur en télétravail

```json
{
  "direct_url": "https://www.leboncoin.fr/recherche?category=56&text=développeur&search_in_description=false",
  "max_pages": 30
}
```

**Résultat** : Liste complète de toutes les offres, prêtes pour votre CRM

---

## 🎨 Cas d'usage réels

### 🏢 Agent immobilier

*"J'utilise cet outil chaque matin pour surveiller les nouvelles annonces de ma zone. En 5 minutes, j'ai une vue complète du marché du jour, avec toutes les informations dont j'ai besoin pour contacter les clients."*  
**Gain de temps** : 2 heures par jour → 5 minutes

### 🔍 Chasseur d'appartements

*"Pour notre déménagement, j'ai scrapy toutes les annonces correspondant à nos critères sur 3 mois. J'ai pu analyser les prix moyens par arrondissement et identifier le meilleur quartier pour notre budget."*  
**Résultat** : 2 500 annonces analysées en quelques heures

### 💼 Étude de marché

*"Nous devions comprendre le marché des smartphones d'occasion pour notre projet. Avec cet outil, nous avons collecté 10 000 annonces en quelques jours, avec toutes les métadonnées pour nos analyses."*  
**Données** : Prêtes pour analyse statistique

### 🛒 Comparateur de prix

*"Je voulais vérifier si le MacBook que je convoitais était bien au bon prix. J'ai scrapy toutes les annonces du modèle sur 2 mois et créé un graphique de l'évolution des prix."*  
**Insight** : J'ai attendu la bonne période pour acheter au meilleur prix

---

## ✨ Fonctionnalités

### 🔍 Recherche ultra-précise

- **Filtres avancés** : Prix, surface, nombre de pièces, DPE, kilométrage, année, carburant, et bien plus
- **Géolocalisation** : Recherche par ville, département, région ou rayon personnalisé
- **Mots-clés** : Recherche textuelle dans les titres et descriptions
- **Toutes les catégories** : Immobilier, véhicules, emploi, électronique, etc.

### 📥 Export de données

Chaque annonce inclut :
- Informations de base (titre, description, prix, photos)
- Localisation (adresse complète, coordonnées GPS)
- Informations vendeur (pro/particulier, nombre d'annonces)
- Métadonnées (dates de publication, indexation)
- Attributs spécifiques (surface, kilométrage, DPE, etc.)

**Formats** : JSON structuré ou CSV prêt pour Excel

### ⚡ Performance

- **Vitesse** : 100-200 annonces par minute
- **Volume** : Pas de limite de pages
- **Fiabilité** : Gestion automatique des erreurs
- **Stabilité** : Protection anti-blocage avec proxies

---

## 📋 Catégories supportées

L'outil fonctionne avec **toutes** les catégories Leboncoin :

| Catégorie | Exemples |
|-----------|----------|
| 🏠 **Immobilier** | Ventes, locations, colocations, bureaux |
| 🚗 **Véhicules** | Voitures, motos, utilitaires, vélos |
| 💼 **Emploi** | Offres d'emploi, formations |
| 📱 **Électronique** | Smartphones, ordinateurs, consoles |
| 🏡 **Maison & Jardin** | Ameublement, décoration, outillage |
| 👔 **Mode** | Vêtements, chaussures, accesscusaires |
| ⚽ **Loisirs** | Sports, hobbies, événements |
| 🔧 **Services** | Prestations, réparations, cours |
| 🌐 **Autres** | Toutes les catégories Leboncoin |

---

## 🎬 Foire aux questions

### Combien ça coûte ?

L'outil fonctionne avec le système de crédits Apify. Un scraping de 1 000 annonces coûte environ quelques euros, bien moins cher qu'une solution développée sur mesure.

### Est-ce légal ?

Oui, l'outil collecte uniquement des **données publiques** visibles sur Leboncoin. Respectez les conditions d'utilisation et les règles GDPR dans votre traitement des données.

### Y a-t-il un risque de blocage ?

Pour des volumes importants, nous recommandons d'utiliser des proxies résidentiels français (inclus dans l'outil). Pour un usage modéré, aucun problème.

### Les données sont-elles à jour ?

Oui, les données sont collectées en temps réel lors de l'exécution du scraping.

### Puis-je automatiser les recherches ?

Absolument ! L'outil s'intègre parfaitement dans vos workflows automatisés grâce à l'API Apify.

### Que faire des données exportées ?

Vous pouvez :
- Les importer dans Excel/JSON pour des analyses
- Les charger dans une base de données
- Les utiliser dans vos outils de veille
- Les intégrer dans votre CRM
- Créer des tableaux de bord avec Power BI ou Tableau

---

## 🛠️ Configuration avancée (optionnel)

Si vous voulez personnaliser finement, vous pouvez configurer :

- **Nombre de pages** : Limitez ou scrapez toutes les pages (illimité)
- **Filtrage par date** : Ignorez les annonces trop anciennes
- **Délai entre pages** : Réglez la vitesse (0 = vitesse maximale)
- **Format de sortie** : Détaillé (tous les champs) ou compact (essentiel)
- **Proxies** : Choisissez entre Apify Proxy ou vos propres proxies

Consultez l'onglet "Input" dans l'interface pour tous les détails.

---

## 📊 Performance et limites

**Vitesse** : Environ 100-200 annonces par minute  
**Volume** : Pas de limite de pages  
**Fiabilité** : Gestion automatique des erreurs et retry  
**Données** : Seules les données publiques sont collectées (pas de numéros de téléphone masqués)

---

## ⚠️ Important

- 🎯 **Utilisation responsable** : Respectez les conditions d'utilisation de Leboncoin
- 🔒 **Données personnelles** : Conformez-vous au RGPD
- ❌ **Pas d'affiliation** : Cet outil est indépendant de Leboncoin

---

## 🚀 Prêt à commencer ?

1. **Ouvrez l'onglet "Input"**
2. **Collez votre URL de recherche Leboncoin**
3. **Cliquez sur "Run"**
4. **Récupérez vos données** dans l'onglet "Dataset"

**Vous avez une question ?** Consultez la section "Issues" ou contactez le support.

---

<div align="center">

**Passez de la recherche manuelle à l'exploitation de données en quelques clics** 🎯

Fait avec ❤️ pour la communauté française

</div>
