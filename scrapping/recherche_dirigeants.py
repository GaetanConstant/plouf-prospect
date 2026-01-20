import csv
import os
import time
import requests
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed

# === CONFIGURATION ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTATS_ENRICHIS_DIR = os.path.join(BASE_DIR, "resultats_enrichis")
INPUT_FILE = os.path.join(RESULTATS_ENRICHIS_DIR, "resultats_enrichis_complets.csv")

RESULTATS_DIRIGEANTS_DIR = os.path.join(BASE_DIR, "resultats_dirigeants")
OUTPUT_FILE = os.path.join(RESULTATS_DIRIGEANTS_DIR, "resultats_dirigeants.csv")

# Créer le dossier de sortie
if not os.path.exists(RESULTATS_DIRIGEANTS_DIR):
    os.makedirs(RESULTATS_DIRIGEANTS_DIR)

def clean_company_name(nom):
    """
    Nettoie le nom de l'entreprise :
    - Supprime les emojis
    - Supprime les caractères spéciaux
    - Normalise les espaces
    - Enlève les formes juridiques
    """
    import re
    
    # Suppression des emojis (tous les caractères Unicode non-ASCII courants)
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        u"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "]+", flags=re.UNICODE)
    nom = emoji_pattern.sub('', nom)
    
    # Suppression des formes juridiques
    formes_juridiques = ['SARL', 'SAS', 'EURL', 'SA', 'SCI', 'SASU', 'EIRL', 'SNC']
    for forme in formes_juridiques:
        nom = re.sub(r'\b' + forme + r'\b', '', nom, flags=re.IGNORECASE)
    
    # Suppression des caractères spéciaux sauf espaces et tirets
    nom = re.sub(r'[^\w\s\-]', ' ', nom)
    
    # Normalisation des espaces multiples
    nom = re.sub(r'\s+', ' ', nom)
    
    return nom.strip()

def search_via_api_gouv(query):
    """API 1: Recherche Entreprises (Gouv) - La plus complète"""
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"https://recherche-entreprises.api.gouv.fr/search?q={encoded_query}&per_page=1"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            
            if results and len(results) > 0:
                result = results[0]
                siren = result.get('siren', '')
                siret = result.get('siege', {}).get('siret', '') or siren
                
                # Dirigeants
                dirigeants_list = result.get('dirigeants', [])
                names = []
                for d in dirigeants_list:
                    nom_d = d.get('nom', '')
                    prenom_d = d.get('prenoms', '')
                    role_d = d.get('qualite', '')
                    full_name = f"{prenom_d} {nom_d}".strip()
                    if full_name:
                        names.append(f"{full_name} ({role_d})")
                
                dirigeants_str = " | ".join(names[:3]) if names else "Non listé"
                
                return {
                    "siret": siret,
                    "siren": siren,
                    "dirigeant": dirigeants_str,
                    "activite": result.get('activite_principale', ''),
                    "adresse_officielle": result.get('siege', {}).get('adresse', ''),
                    "pappers_url": f"https://www.pappers.fr/entreprise/{siren}" if siren else "",
                    "source": "API Gouv"
                }
    except Exception as e:
        pass
    return None

def search_via_pappers(query):
    """API 2: Pappers Suggestions"""
    try:
        url = f"https://suggestions.pappers.fr/v2?q={query}&cibles=nom_entreprise"
        response = requests.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('resultats_nom_entreprise', [])
            
            if results and len(results) > 0:
                result = results[0]
                siren = result.get('siren', '')
                
                return {
                    "siret": siren,
                    "siren": siren,
                    "dirigeant": "Voir sur Pappers",
                    "activite": "",
                    "adresse_officielle": result.get('siege', {}).get('adresse_ligne_1', ''),
                    "pappers_url": f"https://www.pappers.fr/entreprise/{siren}" if siren else "",
                    "source": "Pappers"
                }
    except Exception as e:
        pass
    return None

def search_via_annuaire(query):
    """API 3: Annuaire Entreprises (data.gouv.fr)"""
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"https://annuaire-entreprises.data.gouv.fr/api/v1/search?q={encoded_query}&per_page=1"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            
            if results and len(results) > 0:
                result = results[0]
                siren = result.get('siren', '')
                siret = result.get('siege', {}).get('siret', '') or siren
                
                # Dirigeants
                dirigeants = result.get('dirigeants', [])
                dirigeants_str = "Non listé"
                if dirigeants:
                    names = []
                    for d in dirigeants[:3]:
                        nom = d.get('nom', '')
                        prenom = d.get('prenom', '')
                        if nom or prenom:
                            names.append(f"{prenom} {nom}".strip())
                    if names:
                        dirigeants_str = " | ".join(names)
                
                return {
                    "siret": siret,
                    "siren": siren,
                    "dirigeant": dirigeants_str,
                    "activite": result.get('activite_principale', ''),
                    "adresse_officielle": result.get('siege', {}).get('adresse', ''),
                    "pappers_url": f"https://www.pappers.fr/entreprise/{siren}" if siren else "",
                    "source": "Annuaire Entreprises"
                }
    except Exception as e:
        pass
    return None

def search_via_pappers_scraping(query):
    """API 4: Scraping léger de Pappers.fr (dernier recours)"""
    try:
        from bs4 import BeautifulSoup
        
        # Recherche sur Pappers
        encoded_query = urllib.parse.quote(query)
        url = f"https://www.pappers.fr/recherche?q={encoded_query}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }
        
        response = requests.get(url, timeout=10, headers=headers)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Chercher le premier résultat
            # Structure Pappers : <a href="/entreprise/..."> avec SIREN dans l'URL
            first_result = soup.find('a', href=lambda x: x and '/entreprise/' in x)
            
            if first_result:
                href = first_result.get('href', '')
                # Extraire le SIREN de l'URL (format: /entreprise/nom-entreprise-SIREN)
                import re
                siren_match = re.search(r'/entreprise/[^/]+-(\d{9})', href)
                
                if siren_match:
                    siren = siren_match.group(1)
                    
                    # Essayer d'extraire le nom
                    nom_entreprise = first_result.get_text(strip=True)
                    
                    return {
                        "siret": siren,
                        "siren": siren,
                        "dirigeant": "Voir sur Pappers",
                        "activite": "",
                        "adresse_officielle": "",
                        "pappers_url": f"https://www.pappers.fr{href}",
                        "source": "Pappers Scraping"
                    }
    except Exception as e:
        pass
    return None

def search_company_info(nom, adresse):
    """
    Recherche en cascade avec 4 méthodes différentes.
    S'arrête dès qu'une méthode trouve un résultat.
    """
    if not nom:
        return None
    
    # Nettoyage avancé du nom
    clean_nom = clean_company_name(nom)
    
    # Si le nettoyage a tout supprimé, utiliser le nom original
    if not clean_nom or len(clean_nom) < 3:
        clean_nom = nom
    
    # Extraction code postal
    code_postal = ""
    import re
    cp_match = re.search(r'\b\d{5}\b', str(adresse))
    if cp_match:
        code_postal = cp_match.group(0)
    
    # Construction de la requête
    query = f"{clean_nom} {code_postal}".strip()
    
    # Cascade d'APIs
    apis = [
        ("API Gouv", search_via_api_gouv),
        ("Pappers API", search_via_pappers),
        ("Annuaire", search_via_annuaire),
        ("Pappers Scraping", search_via_pappers_scraping)
    ]
    
    for api_name, api_func in apis:
        try:
            result = api_func(query)
            if result:
                print(f"✅ {nom[:40]}... trouvé via {api_name}")
                return result
        except Exception as e:
            print(f"⚠️ Erreur {api_name} pour {nom[:40]}: {e}")
            continue
    
    print(f"❌ {nom[:40]}... non trouvé (4 méthodes testées)")
    return None

def process_row(row, header_map):
    """Traite une ligne CSV individuellement."""
    try:
        nom = row[header_map['Nom']] if 'Nom' in header_map else row[0]
        adresse = row[header_map['Adresse']] if 'Adresse' in header_map else ""
        
        info = search_company_info(nom, adresse)
        
        # On ajoute les infos trouvées aux données existantes
        row_data = list(row)
        if info:
            return row_data + [info['siret'], info['dirigeant'], info['activite'], info['pappers_url'], info['source'], "Trouvé"]
        else:
            return row_data + ["", "", "", "", "", "Non trouvé"]
    except Exception as e:
        return list(row) + ["", "", "", "", "", f"Erreur: {e}"]

def process_file(input_file, output_file, progress_callback=None):
    """
    Fonction principale pour traiter le fichier.
    progress_callback(current, total, message) est une fonction optionnelle pour le feedback UI.
    """
    if not os.path.exists(input_file):
        if progress_callback: progress_callback(0, 0, f"Erreur: Fichier introuvable {input_file}")
        return False

    # Créer le dossier de sortie si nécessaire
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Lecture du fichier d'entrée
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
            rows = list(reader)
        except StopIteration:
             if progress_callback: progress_callback(0, 0, "Erreur: Fichier vide")
             return False
        
    total_rows = len(rows)
    if progress_callback: progress_callback(0, total_rows, "Démarrage...")
    
    # Mapping des colonnes
    header_map = {col: i for i, col in enumerate(header)}
    
    # Nouvel en-tête
    new_header = header + ["SIRET", "Dirigeants", "Code NAF", "Lien Pappers", "Source", "Status Recherche"]
    
    processed_rows = []
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_row = {executor.submit(process_row, row, header_map): row for row in rows}
        
        for i, future in enumerate(as_completed(future_to_row)):
            try:
                result = future.result()
                processed_rows.append(result)
                if progress_callback:
                    progress_callback(i+1, total_rows, f"Traitement : {i+1}/{total_rows}")
                elif i % 10 == 0:
                    print(f"✅ Avancement : {i+1}/{total_rows}")
            except Exception as e:
                print(f"⚠️ Erreur thread : {e}")
    
    # Écriture du fichier de sortie
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(new_header)
        writer.writerows(processed_rows)
        
    if progress_callback: progress_callback(total_rows, total_rows, "Terminé !")
    return True

def main():
    print("🚀 Démarrage de la recherche des dirigeants...")
    process_file(INPUT_FILE, OUTPUT_FILE)
    print(f"\n🎉 Terminé ! Résultat sauvegardé dans : {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
