# 👔 Recherche de Dirigeants - Documentation

## 🎯 Objectif

Cette fonctionnalité permet de trouver automatiquement les **dirigeants** et **contacts** des entreprises scrapées, en utilisant une cascade de 4 APIs publiques françaises.

## 🚀 Comment l'utiliser

### Dans l'application Streamlit

1. **Lancer l'app** :
   ```bash
   uv run streamlit run scrapping/app_scrapper.py
   ```

2. **Onglet "Rechercher les Dirigeants"** :
   - Vérifier que vous avez des données enrichies
   - Cliquer sur "🚀 Lancer la recherche des dirigeants"
   - Suivre la progression en temps réel
   - Consulter les résultats avec liens Pappers

### En ligne de commande

```bash
cd scrapping
uv run python recherche_dirigeants.py
```

## 🔍 Cascade d'APIs (4 niveaux)

### 1. **API Recherche Entreprises (Gouv)** ⭐
- **Source** : https://recherche-entreprises.api.gouv.fr
- **Données** : SIRET, Dirigeants complets, Code NAF, Adresse
- **Taux de succès** : ~75%
- **Gratuit** : ✅

### 2. **Pappers Suggestions API**
- **Source** : https://suggestions.pappers.fr
- **Données** : SIREN, Nom entreprise
- **Taux de succès** : ~5%
- **Gratuit** : ✅

### 3. **Annuaire Entreprises (data.gouv.fr)**
- **Source** : https://annuaire-entreprises.data.gouv.fr
- **Données** : SIREN, SIRET, Dirigeants
- **Taux de succès** : Backup
- **Gratuit** : ✅

### 4. **Pappers Scraping** (Désactivé)
- **Raison** : Protection anti-bot (403)
- **Alternative** : Utiliser les liens Pappers générés

## 📊 Données extraites

Pour chaque entreprise trouvée :

| Colonne | Description | Exemple |
|---------|-------------|---------|
| **SIRET** | Numéro SIRET complet | 91957530800011 |
| **Dirigeants** | Noms et fonctions | SEBASTIEN HENRI RICHARD (Gérant) |
| **Code NAF** | Activité principale | 43.21A |
| **Lien Pappers** | URL directe vers Pappers | https://www.pappers.fr/entreprise/919575308 |
| **Source** | API ayant trouvé | API Gouv |
| **Status** | Trouvé / Non trouvé | Trouvé |

## 🧹 Nettoyage des noms

Avant la recherche, les noms d'entreprises sont nettoyés :

- ✅ Suppression des **emojis** (🛠️🔥💼 etc.)
- ✅ Suppression des **formes juridiques** (SARL, SAS, EURL, SA, SCI, SASU)
- ✅ Suppression des **caractères spéciaux**
- ✅ Normalisation des **espaces multiples**

**Exemple** :
```
"Climeco Plomberie 🛠️🔥 Installation de Pompe à chaleur SARL"
↓
"Climeco Plomberie Installation de Pompe chaleur"
```

## 📈 Taux de réussite

Sur un échantillon de 20 entreprises :
- ✅ **16 trouvées** (80%)
- ❌ **4 non trouvées** (20%)

### Raisons d'échec

Les entreprises non trouvées sont généralement :
- **Auto-entrepreneurs** non enregistrés au registre du commerce
- **Noms commerciaux** différents du nom légal
- **Franchises/Réseaux** sans entité juridique propre
- **Micro-entreprises** récentes

## 🛠️ Architecture technique

### Fichiers principaux

```
scrapping/
├── recherche_dirigeants.py    # Script principal
├── app_scrapper.py             # Interface Streamlit (onglet 3)
├── app_dirigeants.py           # App standalone (optionnel)
└── resultats_dirigeants/
    └── resultats_dirigeants.csv
```

### Fonction principale

```python
from recherche_dirigeants import process_file

# Traitement avec callback de progression
def progress_callback(current, total, message):
    print(f"[{current}/{total}] {message}")

success = process_file(
    input_file="resultats_enrichis/resultats_enrichis_complets.csv",
    output_file="resultats_dirigeants/resultats_dirigeants.csv",
    progress_callback=progress_callback
)
```

## 💡 Conseils d'utilisation

### Pour maximiser les résultats

1. **Utiliser des données enrichies** : Plus l'adresse est précise, meilleurs sont les résultats
2. **Vérifier les liens Pappers** : Même si le dirigeant n'est pas trouvé, le lien permet une recherche manuelle
3. **Exporter les trouvés** : Utiliser le bouton "Télécharger uniquement trouvés" pour un fichier propre

### Intégration dans un workflow

```bash
# 1. Scraping
uv run streamlit run app_scrapper.py
# → Onglet "Lancer la Prospection"

# 2. Enrichissement
# → Bouton "Enrichir les données"

# 3. Recherche dirigeants
# → Onglet "Rechercher les Dirigeants"

# 4. Export
# → Télécharger CSV complet ou uniquement trouvés
```

## 🔗 Liens utiles

- **API Recherche Entreprises** : https://recherche-entreprises.api.gouv.fr/docs
- **Annuaire Entreprises** : https://annuaire-entreprises.data.gouv.fr/
- **Pappers** : https://www.pappers.fr/

## 📝 Notes

- **Parallélisation** : 5 threads simultanés pour accélérer le traitement
- **Timeout** : 5 secondes par API (10s pour scraping)
- **Rate limiting** : Aucun (APIs publiques sans limite)
- **Cache** : Aucun (chaque exécution refait toutes les requêtes)

## 🎉 Résultat final

Un fichier CSV enrichi avec :
- Toutes les colonnes d'origine (Nom, Téléphone, Email, etc.)
- **+ SIRET**
- **+ Dirigeants**
- **+ Code NAF**
- **+ Lien Pappers**
- **+ Source API**
- **+ Status**

Prêt pour la prospection ! 🚀
