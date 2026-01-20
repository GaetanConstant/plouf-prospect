# 🤖 Plouf Scraper - Guide de Démarrage Rapide

## 🚀 Lancement en 1 commande

```bash
cd scrapping
uv run streamlit run app_scrapper.py
```

Puis ouvrir : **http://localhost:8501**

## 📱 L'Application

**Une seule application avec 4 onglets** :

### 1️⃣ 🚀 Lancer la Prospection
- Scraping Google Maps
- Upload CSV batch
- Choix Firefox/Chrome

### 2️⃣ 📊 Voir les Résultats
- Affichage prospects
- Filtrage et recherche
- Export CSV

### 3️⃣ 👔 Rechercher les Dirigeants
- Recherche automatique (4 APIs)
- SIRET, Dirigeants, Code NAF
- Liens Pappers

### 4️⃣ 🎯 Vue Consolidée ⭐
- **Prospects + Dirigeants fusionnés**
- **Filtres avancés** (Email, Dirigeants, Complets)
- **3 exports optimisés**

## 🎯 Workflow en 4 étapes

```
1. Scraping (Onglet 1)
   ↓
2. Enrichissement (Bouton dans Onglet 1)
   ↓
3. Recherche Dirigeants (Onglet 3)
   ↓
4. Export Optimisé (Onglet 4)
```

## 📊 Résultats attendus

| Étape | Données obtenues | Taux |
|-------|------------------|------|
| **Scraping** | Nom, Téléphone, Site, Adresse | 100% |
| **Enrichissement** | + Email, Téléphone web | 60-70% |
| **Dirigeants** | + SIRET, Dirigeants, NAF | 80% |
| **Complets** | Email + Dirigeants | **50-60%** |

## 🎯 Export final recommandé

**Onglet 4 "Vue Consolidée"** → Filtrer "Complets" → **"⭐ Télécharger les complets"**

Vous obtenez un fichier avec :
- ✅ Nom entreprise
- ✅ Téléphone
- ✅ **Email**
- ✅ Site web
- ✅ Adresse
- ✅ **SIRET**
- ✅ **Dirigeants** (noms + fonctions)
- ✅ Code NAF
- ✅ Lien Pappers

## 📚 Documentation complète

- **STRUCTURE.md** - Architecture du projet
- **README_DIRIGEANTS.md** - Détails recherche dirigeants
- **README_INSTALL.md** - Installation
- **README.md** - Documentation générale

## 🛠️ Fichiers principaux

```
app_scrapper.py              # ⭐ APPLICATION PRINCIPALE
recherche_dirigeants.py      # Module recherche dirigeants
scraper.py                   # Scraper Firefox
enrichisseur.py              # Enrichisseur Firefox
```

## ⚙️ Configuration

**Sidebar de l'app** :
- Max fiches : 5-100
- Navigateur : Firefox/Chrome
- Bouton nettoyage

## 🆘 Problème ?

1. Vérifier les **Diagnostics** (onglet 2)
2. Essayer l'autre navigateur
3. Consulter **STRUCTURE.md**

---

**Prêt à prospecter !** 🚀
