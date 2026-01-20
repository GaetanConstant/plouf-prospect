# 🧪 Tests - APIs de Recherche d'Entreprises

Ce dossier contient les scripts de test pour valider les différentes APIs utilisées pour la recherche de dirigeants.

## 📁 Fichiers

### `test_apis.py`
Test basique des 2 APIs principales :
- API Recherche Entreprises (Gouv)
- Pappers Suggestions

**Usage** :
```bash
uv run python tests/test_apis.py
```

### `test_api_structure.py`
Analyse de la structure de réponse de l'API Gouv pour debug.

**Usage** :
```bash
uv run python tests/test_api_structure.py
```

### `test_multi_apis.py`
Test complet de la cascade de 4 APIs sur des entreprises non trouvées.

**Usage** :
```bash
uv run python tests/test_multi_apis.py
```

### `test_pappers_scraping.py`
Test du scraping Pappers (actuellement bloqué par protection anti-bot).

**Usage** :
```bash
uv run python tests/test_pappers_scraping.py
```

## 🎯 Objectif

Ces scripts permettent de :
- ✅ Valider que les APIs fonctionnent
- ✅ Comprendre la structure des réponses
- ✅ Tester de nouvelles sources de données
- ✅ Débugger les problèmes de recherche

## ⚠️ Note

Ces fichiers sont **uniquement pour le développement et les tests**. L'application principale (`app_scrapper.py`) n'en a pas besoin pour fonctionner.
