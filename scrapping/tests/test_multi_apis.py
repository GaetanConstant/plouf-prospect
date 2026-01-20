import requests
import urllib.parse
import json

def test_api_1_gouv(query):
    """API Recherche Entreprises (déjà utilisée)"""
    print(f"\n{'='*60}")
    print(f"API 1: Recherche Entreprises (Gouv)")
    print(f"Query: {query}")
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"https://recherche-entreprises.api.gouv.fr/search?q={encoded_query}&per_page=1"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            if results:
                r = results[0]
                print(f"✅ Trouvé: {r.get('nom_complet')}")
                print(f"   SIRET: {r.get('siege', {}).get('siret', 'N/A')}")
                print(f"   Dirigeants: {len(r.get('dirigeants', []))} trouvés")
                return True
        print(f"❌ Non trouvé")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_api_2_pappers(query):
    """Pappers Suggestions"""
    print(f"\n{'='*60}")
    print(f"API 2: Pappers Suggestions")
    print(f"Query: {query}")
    try:
        url = f"https://suggestions.pappers.fr/v2?q={query}&cibles=nom_entreprise"
        response = requests.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code == 200:
            data = response.json()
            results = data.get('resultats_nom_entreprise', [])
            if results:
                r = results[0]
                print(f"✅ Trouvé: {r.get('nom_entreprise')}")
                print(f"   SIREN: {r.get('siren')}")
                return True
        print(f"❌ Non trouvé")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_api_3_annuaire(query):
    """Annuaire Entreprises API (data.gouv.fr)"""
    print(f"\n{'='*60}")
    print(f"API 3: Annuaire Entreprises Data.gouv")
    print(f"Query: {query}")
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"https://annuaire-entreprises.data.gouv.fr/api/v1/search?q={encoded_query}&per_page=1"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            if results:
                r = results[0]
                print(f"✅ Trouvé: {r.get('nom_complet')}")
                print(f"   SIREN: {r.get('siren')}")
                return True
        print(f"❌ Non trouvé")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_api_4_sirene(query):
    """API Sirene (INSEE)"""
    print(f"\n{'='*60}")
    print(f"API 4: API Sirene (INSEE)")
    print(f"Query: {query}")
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"https://api.insee.fr/entreprises/sirene/V3/siret?q=denominationUniteLegale:{encoded_query}&nombre=1"
        headers = {
            "Accept": "application/json"
        }
        response = requests.get(url, timeout=5, headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('header', {}).get('total', 0) > 0:
                print(f"✅ Trouvé via INSEE")
                return True
        elif response.status_code == 401:
            print(f"⚠️ Nécessite authentification (clé API)")
        print(f"❌ Non trouvé")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

# Test avec les entreprises non trouvées
test_queries = [
    "Climeco Plomberie",
    "Prestagaz Agence Villefranche",
    "PMPC Plomberie Chauffage",
    "Reseau Plombier Villefranche",
    "KMF Plomberie"
]

print("="*60)
print("TEST DES APIS SUR LES ENTREPRISES NON TROUVÉES")
print("="*60)

for query in test_queries:
    print(f"\n\n{'#'*60}")
    print(f"ENTREPRISE: {query}")
    print(f"{'#'*60}")
    
    found = False
    found = test_api_1_gouv(query) or found
    if not found:
        found = test_api_2_pappers(query) or found
    if not found:
        found = test_api_3_annuaire(query) or found
    if not found:
        found = test_api_4_sirene(query) or found
    
    if found:
        print(f"\n✅ SUCCÈS pour {query}")
    else:
        print(f"\n❌ ÉCHEC pour {query} - Aucune API n'a trouvé")
