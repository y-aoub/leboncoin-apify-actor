# 📑 Index de la documentation

## 🚀 Par où commencer ?

### 👉 Vous êtes pressé ?
**→ [QUICKSTART.md](QUICKSTART.md)** - Démarrage en 3 minutes

### 👉 Première utilisation ?
**→ [README.md](README.md)** - Vue d'ensemble complète

### 👉 Configuration détaillée ?
**→ [USAGE.md](USAGE.md)** - Guide d'utilisation complet

### 👉 Besoin de références ?
**→ [CATEGORIES_REFERENCE.md](CATEGORIES_REFERENCE.md)** - Toutes les catégories et filtres

### 👉 Vue d'ensemble des fichiers ?
**→ [FILES_OVERVIEW.md](FILES_OVERVIEW.md)** - Comprendre la structure

---

## 📚 Documentation complète

### 🎯 Pour démarrer

| Document | Description | Temps de lecture |
|----------|-------------|------------------|
| **[QUICKSTART.md](QUICKSTART.md)** | Guide de démarrage rapide | ⏱️ 3 min |
| **[README.md](README.md)** | Documentation principale | ⏱️ 10 min |

### 📖 Pour approfondir

| Document | Description | Temps de lecture |
|----------|-------------|------------------|
| **[USAGE.md](USAGE.md)** | Guide d'utilisation détaillé | ⏱️ 20 min |
| **[CATEGORIES_REFERENCE.md](CATEGORIES_REFERENCE.md)** | Référence des catégories | ⏱️ 15 min |
| **[FILES_OVERVIEW.md](FILES_OVERVIEW.md)** | Vue d'ensemble des fichiers | ⏱️ 5 min |

---

## 💻 Fichiers de code

### Scripts principaux

| Fichier | Description | Usage |
|---------|-------------|-------|
| **[main.py](main.py)** | Scraper principal (Apify ready) | `python main.py` |
| **[ui.py](ui.py)** | Interface Streamlit | `streamlit run ui.py` |
| **[test_scraper.py](test_scraper.py)** | Suite de tests | `python test_scraper.py` |

### Scripts existants

| Fichier | Description |
|---------|-------------|
| **search_leboncoin.py** | Scraper immobilier spécialisé (original) |
| **search_dpe_api.py** | Matching avec API DPE (original) |

---

## ⚙️ Fichiers de configuration

### Essentiels

| Fichier | Description | Format |
|---------|-------------|--------|
| **[requirements.txt](requirements.txt)** | Dépendances Python | Liste packages |
| **[Dockerfile](Dockerfile)** | Image Docker Apify | Dockerfile |

### Configuration Apify

| Fichier | Description |
|---------|-------------|
| **[.actor/actor.json](.actor/actor.json)** | Métadonnées actor |
| **[.actor/input_schema.json](.actor/input_schema.json)** | Schéma UI Apify |

### Exemples et templates

| Fichier | Description |
|---------|-------------|
| **[config_examples.json](config_examples.json)** | 6 configurations prêtes |
| **[apify_input_example.json](apify_input_example.json)** | Template de configuration |

---

## 🎯 Selon votre objectif

### 🧪 Tester rapidement
1. Lire [QUICKSTART.md](QUICKSTART.md)
2. Lancer `streamlit run ui.py`
3. Configurer et scraper visuellement

### 📦 Scraper en production
1. Lire [USAGE.md](USAGE.md)
2. Copier une config de [config_examples.json](config_examples.json)
3. Lancer `python main.py`

### 🚀 Déployer sur Apify
1. Lire la section "Apify" dans [USAGE.md](USAGE.md)
2. Vérifier [Dockerfile](Dockerfile) et [.actor/](.actor/)
3. Pousser avec `apify push`

### 🔧 Personnaliser le scraper
1. Comprendre l'architecture dans [README.md](README.md)
2. Consulter [CATEGORIES_REFERENCE.md](CATEGORIES_REFERENCE.md)
3. Modifier [main.py](main.py) selon vos besoins

### 🐛 Débugger un problème
1. Lancer [test_scraper.py](test_scraper.py)
2. Consulter la section "Troubleshooting" dans [USAGE.md](USAGE.md)
3. Vérifier [FILES_OVERVIEW.md](FILES_OVERVIEW.md)

---

## 🗂️ Structure du projet

```
leboncoin_scraper/
├── 📄 Documentation
│   ├── INDEX.md                    ← Vous êtes ici
│   ├── QUICKSTART.md               ← Démarrage rapide
│   ├── README.md                   ← Doc principale
│   ├── USAGE.md                    ← Guide détaillé
│   ├── CATEGORIES_REFERENCE.md     ← Référence complète
│   └── FILES_OVERVIEW.md           ← Vue d'ensemble
│
├── 💻 Code
│   ├── main.py                     ← Scraper universel
│   ├── ui.py                       ← Interface Streamlit
│   ├── test_scraper.py             ← Tests automatiques
│   ├── search_leboncoin.py         ← Scraper immobilier (original)
│   └── search_dpe_api.py           ← Matching DPE (original)
│
├── ⚙️ Configuration
│   ├── requirements.txt            ← Dépendances
│   ├── Dockerfile                  ← Docker Apify
│   ├── config_examples.json        ← Configs prêtes
│   ├── apify_input_example.json    ← Template
│   ├── .gitignore                  ← Exclusions Git
│   └── .actor/                     ← Config Apify
│       ├── actor.json
│       └── input_schema.json
│
└── 📊 Données (générées)
    ├── scraper_results.json
    ├── apify_output.json
    └── *.log
```

---

## 🎓 Parcours d'apprentissage

### Niveau 1 : Débutant (30 min)
1. ✅ Lire [QUICKSTART.md](QUICKSTART.md)
2. ✅ Installer : `pip install -r requirements.txt`
3. ✅ Tester UI : `streamlit run ui.py`
4. ✅ Premier scraping avec interface

### Niveau 2 : Intermédiaire (1h)
1. ✅ Lire [README.md](README.md)
2. ✅ Explorer [config_examples.json](config_examples.json)
3. ✅ Scraper en CLI : `python main.py`
4. ✅ Personnaliser une configuration

### Niveau 3 : Avancé (2h)
1. ✅ Lire [USAGE.md](USAGE.md) complet
2. ✅ Étudier [CATEGORIES_REFERENCE.md](CATEGORIES_REFERENCE.md)
3. ✅ Créer configs personnalisées complexes
4. ✅ Configurer proxies et filtres avancés

### Niveau 4 : Expert (3h+)
1. ✅ Comprendre [main.py](main.py) en détail
2. ✅ Modifier le code source
3. ✅ Déployer sur Apify
4. ✅ Intégrer dans vos pipelines

---

## 📖 Glossaire rapide

| Terme | Signification |
|-------|---------------|
| **Apify** | Plateforme de scraping cloud |
| **DPE** | Diagnostic de Performance Énergétique |
| **GES** | Gaz à Effet de Serre |
| **lbc** | Bibliothèque Python pour Leboncoin |
| **Streamlit** | Framework pour créer des interfaces web |
| **Dataset** | Ensemble de données collectées |
| **Actor** | Script déployé sur Apify |

---

## 🔗 Liens utiles

### Ressources externes
- [Bibliothèque lbc](https://github.com/etienne-hd/lbc) - Lib Python Leboncoin
- [Documentation Apify](https://docs.apify.com) - Plateforme de scraping
- [Streamlit Docs](https://docs.streamlit.io) - Framework UI
- [Leboncoin.fr](https://www.leboncoin.fr) - Site source

### Ressources internes
- [Tests](test_scraper.py) - Vérifier l'installation
- [Exemples](config_examples.json) - Configurations prêtes
- [Template](apify_input_example.json) - Base de config

---

## ❓ FAQ Rapide

### Q: Par où commencer ?
**R:** [QUICKSTART.md](QUICKSTART.md) → 3 minutes pour tout comprendre

### Q: Comment configurer les filtres ?
**R:** [CATEGORIES_REFERENCE.md](CATEGORIES_REFERENCE.md) → Liste complète

### Q: J'ai une erreur, que faire ?
**R:** [USAGE.md](USAGE.md) → Section "Troubleshooting"

### Q: Comment déployer sur Apify ?
**R:** [USAGE.md](USAGE.md) → Section "Déploiement Apify"

### Q: Quelles catégories sont supportées ?
**R:** [CATEGORIES_REFERENCE.md](CATEGORIES_REFERENCE.md) → Toutes !

### Q: Comment personnaliser le code ?
**R:** [FILES_OVERVIEW.md](FILES_OVERVIEW.md) + [main.py](main.py)

---

## 🎯 Checklist de démarrage

- [ ] Lire [QUICKSTART.md](QUICKSTART.md)
- [ ] Installer dépendances : `pip install -r requirements.txt`
- [ ] Tester interface : `streamlit run ui.py`
- [ ] Faire un premier scraping
- [ ] Lire [README.md](README.md) pour comprendre
- [ ] Explorer [config_examples.json](config_examples.json)
- [ ] Tester en CLI : `python main.py`
- [ ] Consulter [CATEGORIES_REFERENCE.md](CATEGORIES_REFERENCE.md)
- [ ] Personnaliser une configuration
- [ ] (Optionnel) Déployer sur Apify

---

## 💡 Conseil final

**Pour la majorité des utilisateurs :**
1. Commencez par [QUICKSTART.md](QUICKSTART.md)
2. Utilisez l'interface Streamlit ([ui.py](ui.py))
3. Consultez [CATEGORIES_REFERENCE.md](CATEGORIES_REFERENCE.md) au besoin
4. Revenez à ce fichier INDEX.md si besoin d'orientation

**Bon scraping ! 🚀**

---

*Dernière mise à jour : 22 octobre 2025*

