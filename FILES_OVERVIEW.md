# 📁 Fichiers du projet - Vue d'ensemble

## 🎯 Fichiers principaux (essentiels)

### `main.py` ⭐⭐⭐
**Le script principal du scraper**
- Script prêt pour Apify
- Supporte toutes les catégories Leboncoin
- Configuration dynamique via JSON
- Gestion des proxies, déduplication, filtrage
- Sortie vers Apify dataset ou fichier local
- **Usage** : `python main.py` (nécessite `apify_input.json`)

### `ui.py` ⭐⭐⭐
**Interface Streamlit pour PoC**
- Interface graphique interactive
- Configuration visuelle de tous les paramètres
- Prévisualisation de la config
- Lancement du scraping en un clic
- Visualisation des résultats
- Export JSON/CSV
- **Usage** : `streamlit run ui.py`

### `requirements.txt` ⭐⭐⭐
**Liste des dépendances Python**
- lbc (bibliothèque Leboncoin)
- apify (SDK Apify)
- streamlit (interface UI)
- pandas (export CSV)
- **Usage** : `pip install -r requirements.txt`

## 📚 Documentation

### `README.md` ⭐⭐
**Documentation principale**
- Vue d'ensemble du projet
- Fonctionnalités
- Installation et utilisation rapide
- Exemples de configurations
- Architecture du système
- Troubleshooting

### `USAGE.md` ⭐⭐
**Guide d'utilisation détaillé**
- Instructions complètes d'installation
- Configuration de tous les paramètres
- Exemples pour chaque catégorie
- Guide de déploiement Apify
- Conseils et astuces
- Résolution de problèmes détaillée

### `FILES_OVERVIEW.md` ⭐
**Ce fichier**
- Liste de tous les fichiers du projet
- Description et utilité de chaque fichier

## 🔧 Configuration

### `apify_input_example.json` ⭐⭐
**Exemple de configuration d'entrée**
- Template pour vos propres configurations
- Tous les paramètres disponibles commentés
- Valeurs d'exemple pour l'immobilier
- **Usage** : Copier et modifier selon vos besoins

### `config_examples.json` ⭐⭐
**Configurations prêtes à l'emploi**
- 6 configurations complètes pour différents cas d'usage
- Immobilier Paris, voitures, emploi, électronique, etc.
- **Usage** : 
  ```bash
  cat config_examples.json | jq '.immobilier_paris.config' > apify_input.json
  python main.py
  ```

## 🐳 Déploiement Apify

### `Dockerfile` ⭐⭐
**Image Docker pour Apify**
- Basé sur apify/actor-python:3.11
- Installation des dépendances
- Configuration du point d'entrée
- **Usage** : Utilisé automatiquement par Apify

### `.actor/actor.json` ⭐⭐
**Métadonnées de l'acteur Apify**
- Nom, version, description
- Configuration du dataset
- Vues personnalisées des résultats
- **Usage** : Utilisé par la plateforme Apify

### `.actor/input_schema.json` ⭐⭐
**Schéma d'interface utilisateur Apify**
- Définition de tous les champs d'input
- Types, validations, valeurs par défaut
- Interface UI générée automatiquement
- **Usage** : Génère l'UI Apify automatiquement

## 🧪 Tests

### `test_scraper.py` ⭐
**Suite de tests pour valider le scraper**
- 7 tests couvrant toutes les fonctionnalités
- Test de configuration, enums, locations, client
- Test optionnel de scraping réel
- **Usage** : `python test_scraper.py`

## 🔒 Autre

### `.gitignore` ⭐
**Exclusions Git**
- Fichiers Python temporaires
- Environnements virtuels
- Fichiers de sortie (.json, .log)
- Données scrapées
- **Usage** : Automatique avec Git

## 📊 Fichiers générés (non versionnés)

Ces fichiers sont créés lors de l'exécution :

### `apify_input.json`
Configuration d'entrée active (créer manuellement ou via UI)

### `scraper_results.json`
Résultats complets du scraping (mode local)

### `apify_output.json`
Sortie formatée pour Apify (mode local)

### `scraper.log`
Logs détaillés de l'exécution (si activé)

## 🚀 Quick Start selon votre besoin

### Tester rapidement (PoC)
```bash
streamlit run ui.py
```
Fichiers nécessaires : `ui.py`, `main.py`, `requirements.txt`

### Scraper en local
```bash
# 1. Créer config
cp apify_input_example.json apify_input.json
# 2. Modifier apify_input.json selon vos besoins
# 3. Lancer
python main.py
```
Fichiers nécessaires : `main.py`, `apify_input.json`, `requirements.txt`

### Déployer sur Apify
```bash
apify push
```
Fichiers nécessaires : 
- `main.py`
- `requirements.txt`
- `Dockerfile`
- `.actor/actor.json`
- `.actor/input_schema.json`

## 📈 Workflow recommandé

1. **Phase PoC** : Utiliser `ui.py` pour tester et valider la config
2. **Export config** : Bouton "Exporter" dans l'UI → génère `apify_input.json`
3. **Test local** : `python main.py` pour vérifier
4. **Validation** : `python test_scraper.py` pour tests
5. **Déploiement** : `apify push` vers la plateforme

## 🎨 Personnalisation

Pour adapter le scraper à vos besoins :

1. **Modifier les catégories** : Voir `lbc.Category` dans la lib
2. **Ajouter des filtres** : Section `filters` dans la config
3. **Changer le format de sortie** : Modifier `AdTransformer` dans `main.py`
4. **Ajouter des transformations** : Étendre `DataProcessor`

## 💡 Fichiers selon l'utilisation

| Usage | Fichiers essentiels |
|-------|---------------------|
| **PoC rapide** | `ui.py`, `main.py`, `requirements.txt` |
| **CLI local** | `main.py`, `apify_input.json`, `requirements.txt` |
| **Apify** | `main.py`, `requirements.txt`, `Dockerfile`, `.actor/*` |
| **Documentation** | `README.md`, `USAGE.md` |
| **Exemples** | `config_examples.json`, `apify_input_example.json` |

## 🔍 Résumé

| Fichier | Type | Priorité | Description courte |
|---------|------|----------|-------------------|
| `main.py` | Code | ⭐⭐⭐ | Scraper principal |
| `ui.py` | Code | ⭐⭐⭐ | Interface Streamlit |
| `requirements.txt` | Config | ⭐⭐⭐ | Dépendances Python |
| `README.md` | Doc | ⭐⭐ | Documentation générale |
| `USAGE.md` | Doc | ⭐⭐ | Guide détaillé |
| `Dockerfile` | Deploy | ⭐⭐ | Image Docker Apify |
| `.actor/actor.json` | Deploy | ⭐⭐ | Config Apify |
| `.actor/input_schema.json` | Deploy | ⭐⭐ | UI Apify |
| `config_examples.json` | Config | ⭐⭐ | Configs prêtes |
| `apify_input_example.json` | Config | ⭐⭐ | Template de config |
| `test_scraper.py` | Test | ⭐ | Suite de tests |
| `.gitignore` | Git | ⭐ | Exclusions Git |
| `FILES_OVERVIEW.md` | Doc | ⭐ | Ce fichier |

---

**Total : 13 fichiers + 1 dossier (.actor avec 2 fichiers)**

Tous les fichiers sont prêts à l'emploi et ne nécessitent aucune modification pour fonctionner ! 🎉

