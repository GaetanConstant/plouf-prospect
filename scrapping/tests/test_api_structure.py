import requests
import urllib.parse
import json

def test_gouv_api(query):
    print(f"Testing API Gouv with query: {query}")
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"https://recherche-entreprises.api.gouv.fr/search?q={encoded_query}&per_page=1"
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Data Type: {type(data)}")
            if isinstance(data, list):
                print("Data is a LIST")
                if len(data) > 0:
                    print(f"First item keys: {data[0].keys()}")
            elif isinstance(data, dict):
                print(f"Data is a DICT with keys: {data.keys()}")
            
            # Print raw snippet
            print(f"Raw data snippet: {json.dumps(data, indent=2)[:300]}...")
        else:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error Gouv: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_gouv_api("La Clef de Voute")
