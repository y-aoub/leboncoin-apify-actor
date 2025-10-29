# 🏠 Leboncoin Scraper

**L'outil simple pour extraire toutes les annonces Leboncoin et transformer le marché français en données exploitables.**

---

## 💡 Pourquoi utiliser cet outil ?

Économisez des heures de recherche manuelle. Collectez automatiquement des milliers d'annonces filtrées et exportez-les en JSON ou CSV.

### 🎯 Cas d'usage

✅ Analyse immobilière • Monitoring de prix • Recherche d'opportunités • Veille concurrentielle • Génération de leads • Étude de marché

---

## 🚀 Démarrage rapide

1. **Allez sur Leboncoin.fr** et faites une recherche
2. **Copiez l'URL** (ex: `https://www.leboncoin.fr/recherche?category=9&locations=Paris&price=100000-300000`)
3. **Collez dans l'outil** et lancez
4. **Récupérez vos données** en quelques minutes

C'est tout ! Aucune connaissance technique requise.

---

## 📊 Exemples

**Appartements à Paris (2-3 pièces, 250-400k€)**
```json
{
  "direct_url": "https://www.leboncoin.fr/recherche?category=9&locations=Paris&price=250000-400000&rooms=2.0-4.0&real_estate_type=2",
  "max_pages": 0
}
```

**Voitures électriques en Île-de-France**
```json
{
  "direct_url": "https://www.leboncoin.fr/recherche?category=2&locations=Paris__48.856614_2.3522219_10000&fuel=4&regdate=2020-2024",
  "max_pages": 50
}
```

---

## ✨ Fonctionnalités

**Filtres avancés** : Prix, surface, pièces, DPE, kilométrage, année, carburant, géolocalisation, mots-clés  
**Export riche** : Titre, description, prix, photos, adresse, GPS, infos vendeur, métadonnées  
**Formats** : JSON structuré ou CSV  
**Performance** : Plus de 10000 annonces/min, pas de limite de pages

---

## 📋 Catégories supportées

🏠 Immobilier • 🚗 Véhicules • 💼 Emploi • 📱 Électronique • 🏡 Maison & Jardin • 👔 Mode • ⚽ Loisirs • 🔧 Services

---

## Alternate common questions

**Coût** : Quelques euros pour 1000 annonces (crédits Apify)  
**Légal** : Données publiques uniquement. Respectez ToS et RGPD  
**Blocage** : Proxies français inclus pour gros volumes  
**Données** : À jour, collectées en temps réel  
**Automatisation** : API Apify disponible

---

## ⚠️ Important

🎯 Utilisation responsable • 🔒 Conformité RGPD • ❌ Indépendant de Leboncoin

---

## 🚀 Prêt ?

1. Onglet "Input" → Collez votre URL → "Run"  
2. Récupérez dans "Dataset"

**Question ?** Consultez "Issues"
