# 🚀 Quick Start Guide

## ⚡ Démarrage en 3 minutes

### 1️⃣ Installation (30 secondes)

```bash
cd /home/y-aoub/my_projects/leboncoin_scraper
pip install -r requirements.txt
```

### 2️⃣ Test avec l'interface (1 minute)

```bash
streamlit run ui.py
```

Une interface web s'ouvre automatiquement :
1. Choisissez une catégorie (ex: Immobilier)
2. Sélectionnez une localisation (ex: Paris)
3. Cliquez sur "▶️ Lancer le scraping"
4. Voyez les résultats en temps réel !

### 3️⃣ Ou en ligne de commande (1 minute)

```bash
# Utiliser une configuration d'exemple
cat config_examples.json | python -c "import sys, json; print(json.dumps(json.load(sys.stdin)['immobilier_paris']['config']))" > apify_input.json

# Lancer le scraper
python main.py

# Voir les résultats
cat scraper_results.json
```

## 📖 Fichiers importants

| Fichier | Description | Quand l'utiliser |
|---------|-------------|------------------|
| `ui.py` | Interface Streamlit | ✅ Pour tester et configurer |
| `main.py` | Script principal | ✅ Pour scraping production |
| `config_examples.json` | Configs prêtes | ✅ Pour démarrer rapidement |
| `test_scraper.py` | Tests automatiques | ✅ Pour valider l'installation |
| `README.md` | Doc complète | 📚 Pour tout comprendre |
| `USAGE.md` | Guide détaillé | 📚 Pour configuration avancée |

## 🎯 Cas d'usage rapides

### Scraper l'immobilier à Paris

```bash
streamlit run ui.py
# Dans l'interface:
# 1. Catégorie: "IMMOBILIER_VENTES_IMMOBILIERES"
# 2. Localisation: "Département" → "75"
# 3. Prix: 300000 - 800000
# 4. Cliquer "Lancer"
```

### Scraper des voitures en Île-de-France

```bash
# Copier la config exemple
echo '{
  "category": "VEHICULES_VOITURES",
  "location_type": "region",
  "locations": [{"name": "ILE_DE_FRANCE"}],
  "price_min": 5000,
  "price_max": 20000,
  "max_pages": 5
}' > apify_input.json

# Lancer
python main.py
```

### Scraper toutes les catégories dans une ville

```bash
echo '{
  "category": "TOUTES_CATEGORIES",
  "location_type": "city",
  "locations": [{
    "name": "Lyon",
    "lat": 45.764043,
    "lng": 4.835659,
    "radius": 15000
  }],
  "max_pages": 3
}' > apify_input.json

python main.py
```

## 🧪 Vérifier que tout fonctionne

```bash
python test_scraper.py
```

Tous les tests doivent passer ✅

## 📊 Formats de sortie

### Mode UI (Streamlit)
- Visualisation en direct
- Export JSON/CSV via boutons
- Statistiques en temps réel

### Mode CLI
- `scraper_results.json` : Résultats complets avec stats
- `apify_output.json` : Toutes les annonces en tableau

## 🔥 Configurations prêtes à l'emploi

Utilisez `config_examples.json` :

```bash
# Liste des configs disponibles
cat config_examples.json | python -c "import sys, json; [print(f'- {k}: {v[\"description\"]}') for k,v in json.load(sys.stdin).items()]"
```

Configs disponibles :
- `immobilier_paris` : Appartements à Paris
- `voitures_ile_de_france` : Voitures en IdF
- `emploi_informatique` : Jobs IT
- `electronique_france` : Électronique nationale
- `immobilier_complet` : Scraping immobilier DPE complet
- `tous_categories_region` : Multi-catégories

Pour utiliser une config :

```bash
# Extraire la config
cat config_examples.json | python -c "import sys, json; print(json.dumps(json.load(sys.stdin)['immobilier_paris']['config']))" > apify_input.json

# Lancer
python main.py
```

## 🎨 Interface Streamlit - Guide visuel

### Zone latérale (Configuration)
1. **Catégorie** : Dropdown avec toutes les catégories
2. **Recherche** : Mots-clés optionnels
3. **Localisation** : Type (Ville/Département/Région) + sélection
4. **Filtres** : Prix, tri, type d'annonce
5. **Filtres avancés** : JSON personnalisé selon catégorie
6. **Pagination** : Pages max, délais
7. **Âge** : Filtrage par date
8. **Proxy** : Configuration optionnelle
9. **Format** : Détaillé ou compact

### Zone principale
- **Configuration actuelle** : Prévisualisation JSON
- **Export** : Bouton pour sauvegarder la config
- **Actions** : Lancer/Arrêter
- **Statistiques** : Métriques en temps réel
- **Résultats** : Onglets Aperçu/Export/Détails

## 💡 Astuces pro

### 1. Test rapide avant production
```bash
# Dans apify_input.json, mettre:
"max_pages": 1,
"limit_per_page": 5
# → Scrape 5 annonces pour tester
```

### 2. Export de config depuis UI
1. Configurer dans Streamlit
2. Cliquer "💾 Exporter configuration"
3. Récupérer `apify_input.json`
4. Utiliser en CLI : `python main.py`

### 3. Scraping par lots
```bash
# Créer plusieurs configs
echo '{"category": "VEHICULES_VOITURES", ...}' > config_voitures.json
echo '{"category": "IMMOBILIER", ...}' > config_immo.json

# Scraper chacune
for f in config_*.json; do
  cp "$f" apify_input.json
  python main.py
done
```

### 4. Mode debug
Dans `apify_input.json` :
```json
{
  "verbose": true,
  "max_pages": 1
}
```

## 🐛 Problèmes courants

### Erreur "Module not found"
```bash
pip install -r requirements.txt --upgrade
```

### Erreur 403 (Datadome)
Ajouter un proxy dans la config :
```json
{
  "proxy_host": "your-proxy.com",
  "proxy_port": 8080
}
```

### Pas de résultats
Vérifier que les filtres ne sont pas trop restrictifs :
- Retirer `max_age_days`
- Augmenter la plage de prix
- Essayer sans filtres avancés

### UI Streamlit ne démarre pas
```bash
# Vérifier l'installation
pip install streamlit --upgrade

# Vérifier le port
streamlit run ui.py --server.port 8502
```

## 🚀 Déployer sur Apify

### Méthode 1 : Apify CLI
```bash
# Installer CLI
npm install -g apify-cli

# Login
apify login

# Déployer
apify push
```

### Méthode 2 : GitHub
1. Push le code sur GitHub
2. Connecter GitHub à Apify
3. Deploy automatique à chaque push

### Fichiers nécessaires pour Apify
✅ `main.py`
✅ `requirements.txt`
✅ `Dockerfile`
✅ `.actor/actor.json`
✅ `.actor/input_schema.json`

Tous sont déjà prêts ! 🎉

## 📞 Besoin d'aide ?

1. **Documentation** : `README.md` et `USAGE.md`
2. **Tests** : `python test_scraper.py`
3. **Exemples** : `config_examples.json`
4. **Fichiers** : `FILES_OVERVIEW.md`

## ✨ C'est parti !

```bash
# La commande magique pour démarrer
streamlit run ui.py
```

Bon scraping ! 🎉

