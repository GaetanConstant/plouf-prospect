# Instructions de Lancement : Plouf Prospect

Ce projet est composé d'une API **FastAPI** (Backend) et d'une application **React + Vite** (Frontend).

## 🚀 Lancement Rapide

### 1. Backend (API FastAPI)
L'API gère le scraping et l'enrichissement des prospects.

**Prérequis :** Python 3.10+

1. **Installation des dépendances :**
   ```bash
   pip install -r scrapping/requirements.txt
   ```
   *(Note: Assurez-vous également d'avoir les dépendances de base si nécessaire via `pip install -r requirements.txt`)*

2. **Lancement de l'API :**
   Depuis la racine du projet :
   ```bash
   python api/main.py
   ```
   *L'API sera lancée sur [http://localhost:8000](http://localhost:8000). Vous pouvez accéder à la documentation interactive (Swagger) sur [http://localhost:8000/docs](http://localhost:8000/docs).*

---

### 2. Frontend (React + Vite)
L'interface utilisateur pour piloter les recherches.

**Prérequis :** Node.js & npm

1. **Installation des dépendances :**
   ```bash
   cd front
   npm install
   ```

2. **Lancement du Frontend :**
   Depuis le dossier `front/` :
   ```bash
   npm start
   ```
   *L'application sera accessible sur [http://localhost:3000](http://localhost:3000).*

---

## 🛠️ Structure du Projet

- `api/` : Contient le point d'entrée de l'API (`main.py`).
- `front/` : Contient l'application React.
- `scrapping/` : Contient les scripts de scraping et d'enrichissement utilisés par l'API.
- `resultats/` : (Généré) Dossier où sont stockés les fichiers CSV produits.
