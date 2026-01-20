# 🤖 Plouf Scraper - Structure du Projet

## 📁 Structure des fichiers

```
scrapping/
├── 📱 APPLICATIONS PRINCIPALES
│   └── app_scrapper.py              # Application Streamlit complète (4 onglets)
│
├── 🔧 MODULES CORE
│   ├── scraper.py                   # Scraper Google Maps (Firefox)
│   ├── scraper_chrome.py            # Scraper Google Maps (Chrome)
│   ├── enrichisseur.py              # Enrichissement emails/tél (Firefox)
│   ├── enrichisseur_chrome.py       # Enrichissement emails/tél (Chrome)
│   ├── recherche_dirigeants.py      # Recherche dirigeants (4 APIs)
│   └── surveillance.py              # Surveillance de mots-clés
│
├── 📊 DONNÉES
│   ├── resultats/                   # Résultats bruts du scraping
│   ├── resultats_enrichis/          # Résultats avec emails/téléphones
│   ├── resultats_dirigeants/        # Résultats avec dirigeants
│   ├── mots_cles.csv               # Mots-clés à scraper
│   └── motsclesdejafait.csv        # Historique des scraping
│
├── 🧪 TESTS
│   └── tests/                       # Scripts de test des APIs
│       ├── test_apis.py
│       ├── test_multi_apis.py
│       ├── test_api_structure.py
│       └── test_pappers_scraping.py
│
├── 📚 DOCUMENTATION
│   ├── README.md                    # Documentation principale
│   ├── README_DIRIGEANTS.md         # Doc recherche dirigeants
│   └── README_INSTALL.md            # Installation
│
└── ⚙️ CONFIGURATION
    ├── requirements.txt             # Dépendances Python
    └── chromedriver/                # Driver Chrome

```

## 🚀 Lancement de l'application

### Application principale (RECOMMANDÉ)

```bash
cd scrapping
uv run streamlit run app_scrapper.py
```

Cette application contient **4 onglets** :

1. **🚀 Lancer la Prospection**
   - Scraping Google Maps
   - Upload CSV batch
   - Choix Firefox/Chrome

2. **📊 Voir les Résultats**
   - Affichage des prospects scrapés
   - Filtrage et recherche
   - Export CSV

3. **👔 Rechercher les Dirigeants**
   - Recherche automatique via 4 APIs
   - SIRET, Dirigeants, Code NAF
   - Liens Pappers

4. **🎯 Vue Consolidée** ⭐
   - Prospects + Dirigeants fusionnés
   - Filtres avancés (Email, Dirigeants, Complets)
   - 3 types d'exports optimisés

## 📖 Workflow complet

```
1. Scraping
   ↓
2. Enrichissement (Emails/Tél)
   ↓
3. Recherche Dirigeants
   ↓
4. Vue Consolidée & Export
```

### Étape par étape

#### 1️⃣ Scraping Google Maps

**Onglet "Lancer la Prospection"**

- **Option A** : Recherche simple
  ```
  Mot-clé : Restaurant
  Secteur : 69000
  ```

- **Option B** : Upload CSV batch
  ```csv
  Sociétés,Codes
  Restaurant,69000
  Plombier,69400
  ```

Cliquer sur **"🔍 Démarrer le Scraping"**

#### 2️⃣ Enrichissement

Cliquer sur **"✨ Enrichir les données existantes"**

→ Visite les sites web pour extraire emails et téléphones

#### 3️⃣ Recherche des Dirigeants

**Onglet "Rechercher les Dirigeants"**

Cliquer sur **"🚀 Lancer la recherche des dirigeants"**

→ Interroge 4 APIs pour trouver :
- SIRET
- Dirigeants (noms + fonctions)
- Code NAF
- Lien Pappers

#### 4️⃣ Export optimisé

**Onglet "Vue Consolidée"**

Filtrer selon vos besoins :
- ⭐ **Complets** (Email + Dirigeants) - Les meilleurs prospects
- 📧 Avec Email uniquement
- 👔 Avec Dirigeants uniquement

Exporter :
- **📥 Sélection** - Export filtré
- **⭐ Complets** - Uniquement Email + Dirigeants
- **🎯 Prospection** - Colonnes essentielles optimisées

## 🔧 Utilisation en ligne de commande

### Scraping

```bash
# Firefox (par défaut)
uv run python scraper.py 20

# Chrome
uv run python scraper_chrome.py 20
```

### Enrichissement

```bash
# Firefox
uv run python enrichisseur.py

# Chrome
uv run python enrichisseur_chrome.py
```

### Recherche dirigeants

```bash
uv run python recherche_dirigeants.py
```

## 📊 Fichiers de sortie

### `resultats_complets.csv`
Résultats bruts du scraping Google Maps
- Nom, Téléphone, Site web, Adresse

### `resultats_enrichis_complets.csv`
Résultats enrichis avec emails/téléphones
- + Email trouvé
- + Téléphone trouvé sur site

### `resultats_dirigeants.csv`
Résultats avec informations dirigeants
- + SIRET
- + Dirigeants
- + Code NAF
- + Lien Pappers
- + Source API
- + Status Recherche

## 🎯 Taux de réussite

| Étape | Taux moyen |
|-------|------------|
| Scraping Google Maps | ~100% |
| Enrichissement Email | ~60-70% |
| Enrichissement Téléphone | ~40-50% |
| Recherche Dirigeants | ~80% |
| **Complets (Email + Dirigeants)** | **~50-60%** |

## 🛠️ Configuration

### Navigateur

Choix dans la sidebar :
- **Firefox** (par défaut, plus stable)
- **Chrome** (plus rapide)

### Max fiches

Slider : 5 à 100 fiches par recherche

### Nettoyage des données

Bouton **"🧹 Effacer toutes les données"** dans la sidebar

## 📝 Notes importantes

### APIs utilisées (gratuites)

1. **API Recherche Entreprises** (Gouv)
   - https://recherche-entreprises.api.gouv.fr
   - Données : SIRET, Dirigeants, NAF

2. **Pappers Suggestions**
   - https://suggestions.pappers.fr
   - Données : SIREN, Nom

3. **Annuaire Entreprises**
   - https://annuaire-entreprises.data.gouv.fr
   - Données : SIREN, SIRET, Dirigeants

### Limitations

- **Scraping** : Limité par Google Maps (max ~100 fiches/recherche)
- **APIs** : Aucune limite de rate (APIs publiques)
- **Enrichissement** : Dépend de la présence d'emails sur les sites

### Performances

- **Scraping** : ~2-3 fiches/seconde
- **Enrichissement** : ~1 site/seconde
- **Dirigeants** : ~5 entreprises/seconde (parallélisé)

## 🆘 Dépannage

### Aucun résultat de scraping

1. Vérifier les captures de debug dans l'onglet "Diagnostics"
2. Essayer avec l'autre navigateur (Firefox ↔ Chrome)
3. Augmenter les temps d'attente dans le code

### Erreur "No such file or directory"

→ Les dossiers sont créés automatiquement, relancer l'opération

### Dirigeants non trouvés

→ Normal pour ~20% des entreprises (auto-entrepreneurs, franchises, etc.)

## 📞 Support

Pour toute question, consulter :
- `README.md` - Documentation générale
- `README_DIRIGEANTS.md` - Documentation dirigeants
- `README_INSTALL.md` - Installation

---

**Version** : 2.0  
**Dernière mise à jour** : 2026-01-20  
**Auteur** : Antigravity for Plouf Prospect
