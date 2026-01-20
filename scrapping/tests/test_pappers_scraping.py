import requests
from bs4 import BeautifulSoup
import urllib.parse

def test_pappers_scraping(query):
    print(f"\n{'='*60}")
    print(f"Test Pappers Scraping pour: {query}")
    print(f"{'='*60}")
    
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"https://www.pappers.fr/recherche?q={encoded_query}"
        print(f"URL: {url}")
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }
        
        response = requests.get(url, timeout=10, headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Sauvegarder un extrait du HTML pour debug
            with open('/tmp/pappers_debug.html', 'w', encoding='utf-8') as f:
                f.write(response.text[:5000])
            print("HTML sauvegardé dans /tmp/pappers_debug.html")
            
            # Chercher tous les liens vers des entreprises
            all_links = soup.find_all('a', href=lambda x: x and '/entreprise/' in x)
            print(f"Nombre de liens /entreprise/ trouvés: {len(all_links)}")
            
            if all_links:
                for i, link in enumerate(all_links[:3]):
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    print(f"  [{i+1}] {text[:50]} -> {href}")
                    
                    # Essayer d'extraire le SIREN
                    import re
                    siren_match = re.search(r'/entreprise/[^/]+-(\d{9})', href)
                    if siren_match:
                        print(f"      SIREN trouvé: {siren_match.group(1)}")
            else:
                print("Aucun lien trouvé, essayons une autre structure...")
                # Chercher des divs ou autres éléments
                results_div = soup.find_all('div', class_=lambda x: x and 'result' in str(x).lower())
                print(f"Divs 'result' trouvés: {len(results_div)}")
                
    except Exception as e:
        print(f"Erreur: {type(e).__name__}: {e}")

# Test avec les entreprises non trouvées
queries = [
    "Climeco Plomberie 69400",
    "PMPC Plomberie Chauffage 69400",
    "Prestagaz Villefranche 69400"
]

for q in queries:
    test_pappers_scraping(q)
