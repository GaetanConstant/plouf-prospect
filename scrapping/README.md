# Scraping Automatisé Google Maps

Ce projet permet d'extraire automatiquement des informations à partir de Google Maps pour différents types d'établissements (restaurants, pharmacies, dentistes, etc.) en fonction de mots-clés et codes postaux. Les données extraites sont ensuite enrichies avec des emails et numéros de téléphone trouvés sur les sites web des établissements.

## Fonctionnalités

- **Scraping automatisé** : Extraction des données de Google Maps sans intervention manuelle
- **Mode headless** : Fonctionne en arrière-plan sans perturber l'utilisateur
- **Fichier unique** : Toutes les données sont stockées dans un seul fichier CSV
- **Reprise automatique** : Peut reprendre le scraping là où il s'était arrêté en cas d'interruption
- **Gestion des erreurs** : Robuste face aux erreurs de connexion et aux blocages temporaires
- **Surveillance automatique** : Système qui relance le script s'il s'arrête
- **Enrichissement des données** : Extraction automatique des emails et téléphones depuis les sites web

## Prérequis

1. Python 3.6 ou supérieur
2. Environnement virtuel Python (recommandé)
3. Chrome installé sur le système
4. ChromeDriver compatible avec votre version de Chrome

## Installation

1. Cloner le dépôt ou télécharger les fichiers
2. Créer un environnement virtuel et l'activer :

```bash
python -m venv venv
source venv/bin/activate  # Sur macOS/Linux
```

3. Installer les dépendances :

```bash
pip install selenium requests beautifulsoup4
```

4. Télécharger ChromeDriver et le placer dans le dossier `chromedriver/chromedriver-mac-arm64/` (ajuster selon votre système)

## Structure du projet

- `mots_cles.csv` : Liste des mots-clés et codes postaux à rechercher sur Google Maps
- `scraper.py` : Script principal pour extraire les données de Google Maps
- `enrichisseur.py` : Script pour enrichir les données avec les emails et téléphones
- `surveillance.py` : Script qui surveille et relance automatiquement le scraper si nécessaire
- `resultats/` : Dossier où est stocké le fichier CSV de résultats bruts
  - `resultats_complets.csv` : Fichier unique contenant toutes les données scrapées
  - `progression.txt` : Fichier de suivi pour la reprise en cas d'interruption
- `resultats_enrichis/` : Dossier où est stocké le fichier CSV enrichi
  - `resultats_enrichis_complets.csv` : Fichier unique contenant toutes les données enrichies
- `chromedriver/` : Dossier contenant le pilote Chrome pour Selenium

## Utilisation

### 1. Préparer les mots-clés

Le fichier `mots_cles.csv` contient la liste des mots-clés à rechercher. Chaque ligne correspond à un mot-clé et un code postal.

Format du fichier :
```
mot_cle
salle de cinéma 38000 FR
dentiste 38000 FR
pharmacie 38000 FR
```

### 2. Lancer le scraping

Pour lancer le scraping avec surveillance automatique (recommandé) :

```bash
source venv/bin/activate
python surveillance.py
```

Ou pour lancer uniquement le scraper sans surveillance :

```bash
source venv/bin/activate
python scraper.py
```

### 3. Fonctionnement du scraper

Le script `scraper.py` :
- Lit les mots-clés depuis le fichier `mots_cles.csv`
- Pour chaque mot-clé, recherche sur Google Maps
- Extrait les informations (nom, téléphone, site web, adresse)
- Enregistre les données dans `resultats/resultats_complets.csv`
- Lance automatiquement l'enrichissement une fois terminé

### 4. Enrichissement des données

Le script `enrichisseur.py` :
- Lit les données du fichier `resultats/resultats_complets.csv`
- Pour chaque entrée avec un site web, visite le site
- Extrait les emails et numéros de téléphone supplémentaires
- Enregistre les données enrichies dans `resultats_enrichis/resultats_enrichis_complets.csv`

### 5. Surveillance automatique

Le script `surveillance.py` :
- Surveille l'exécution du script `scraper.py`
- Relance automatiquement le script s'il s'arrête
- Enregistre les événements dans un fichier log

## Configuration

Le script `scraper.py` contient plusieurs paramètres configurables :

```python
# Mode headless (true = invisible, false = visible)
MODE_HEADLESS = True

# Nombre maximum de fiches à traiter par mot-clé
MAX_FICHES_PAR_MOT_CLE = 20

# Délais d'attente (en secondes)
DELAI_CHARGEMENT_PAGE = 2
DELAI_SCROLL = 1
DELAI_TRAITEMENT_FICHE = 1

# Paramètres pour éviter le blocage
MOTS_CLES_AVANT_PAUSE = 100
DUREE_PAUSE = 30
```

## Optimisations

Le script inclut plusieurs optimisations pour améliorer la fiabilité et la performance :

1. **Rotation des user agents** : Utilise différents user agents pour éviter la détection
2. **Gestion automatique des cookies** : Accepte automatiquement les cookies de Google Maps
3. **Réinitialisation périodique** : Redémarre le navigateur régulièrement pour éviter les fuites mémoire
4. **Système de reprise** : Sauvegarde la progression pour pouvoir reprendre après une interruption
5. **Tentatives multiples** : Réessaie automatiquement en cas d'erreur de connexion
6. **Désactivation des images** : Accélère le chargement en désactivant les images

## Résolution des problèmes

- **Le script s'arrête sans erreur** : Vérifiez si Google Maps a détecté l'activité de scraping. Attendez quelques heures avant de relancer.
- **Erreurs de ChromeDriver** : Assurez-vous que votre version de ChromeDriver est compatible avec votre version de Chrome.
- **Résultats vides** : Si vous obtenez des résultats vides pour certains mots-clés, essayez de relancer le script avec une pause plus longue.

## Notes importantes

- Ce script est conçu pour un usage personnel ou éducatif.
- Le scraping intensif de Google Maps peut entraîner un blocage temporaire de votre adresse IP.
- Respectez les conditions d'utilisation de Google et les lois sur la protection des données.

## Exemples de données extraites

### Données brutes (resultats_complets.csv)
```
Mot-clé,Nom,Téléphone,Site web,Adresse
salle de cinéma 38000 FR,Cinéma La Nef,,https://www.cinefil.com/cinema/la-nef-grenoble/programmation,
salle de cinéma 38000 FR,Salle Rouge,,,
salle de cinéma 38000 FR,La basse cour,,http://www.labassecour.net/,
```

### Données enrichies (resultats_enrichis_complets.csv)
```
Mot-clé,Nom,Téléphone,Site web,Adresse,Email,Téléphone supplémentaire
salle de cinéma 38000 FR,Cinéma La Nef,,https://www.cinefil.com/cinema/la-nef-grenoble/programmation,,contact@cinefil.com,04 76 54 32 10
salle de cinéma 38000 FR,Salle Rouge,,,,,
salle de cinéma 38000 FR,La basse cour,,http://www.labassecour.net/,,info@labassecour.net,04 76 12 34 56
```

## Auteur

Ce projet a été développé pour automatiser la collecte de données d'établissements à partir de Google Maps.
