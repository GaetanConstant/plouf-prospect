import requests
import urllib.parse

def test_gouv_api(query):
    print(f"Testing API Gouv with query: {query}")
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"https://recherche-entreprises.api.gouv.fr/search?q={encoded_query}&per_page=1"
        print(f"URL: {url}")
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Results found: {len(data)}")
            if len(data) > 0:
                print(f"First result: {data[0].get('nom_complet')}")
        else:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error Gouv: {type(e).__name__}: {e}")

def test_pappers_suggestions(query):
    print(f"\nTesting Pappers Suggestions with query: {query}")
    try:
        # Pappers suggestions API is often open for frontend autocomplete
        url = f"https://suggestions.pappers.fr/v2?q={query}&cibles=nom_entreprise"
        print(f"URL: {url}")
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            # The structure might vary, usually a list of results
            results = data.get('resultats_nom_entreprise', [])
            print(f"Results found: {len(results)}")
            if len(results) > 0:
                print(f"First result: {results[0].get('nom_entreprise')} - {results[0].get('siren')}")
        else:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error Pappers: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_query = "La Clef de Voute"
    test_gouv_api(test_query)
    test_pappers_suggestions(test_query)
