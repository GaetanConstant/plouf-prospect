import re
import csv
import os
import requests
from bs4 import BeautifulSoup
import glob
from datetime import datetime

# ========== CONFIGURATION ==========
RESULTATS_DIR = "resultats"
ENRICHIS_DIR = "resultats_enrichis"
FICHIER_RESULTAT = f"{RESULTATS_DIR}/resultats_complets.csv"
FICHIER_ENRICHI = f"{ENRICHIS_DIR}/resultats_enrichis_complets.csv"

# Créer le dossier de résultats enrichis s'il n'existe pas
if not os.path.exists(ENRICHIS_DIR):
    os.makedirs(ENRICHIS_DIR)

# ========== FONCTIONS ==========

def get_page_text(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        return soup.get_text()
    except Exception as e:
        print(f"⚠️ Erreur lors de la récupération de {url} : {e}")
        return ""

def extract_email_and_phone_from_text(text):
    # Email classique
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text)
    
    # Téléphone français (formats variés)
    phone_patterns = [
        r'0\d[\s.-]?\d{2}[\s.-]?\d{2}[\s.-]?\d{2}[\s.-]?\d{2}',  # 01 23 45 67 89
        r'\+33[\s.-]?[1-9][\s.-]?\d{2}[\s.-]?\d{2}[\s.-]?\d{2}[\s.-]?\d{2}'  # +33 1 23 45 67 89
    ]
    
    phones = []
    for pattern in phone_patterns:
        phones.extend(re.findall(pattern, text))
    
    return emails[0] if emails else "", phones[0] if phones else ""

def extract_from_site(base_url):
    urls_to_check = [
        base_url,
        f"{base_url}/contact" if not base_url.endswith('/') else f"{base_url}contact",
        f"{base_url}/mentions-legales" if not base_url.endswith('/') else f"{base_url}mentions-legales"
    ]

    for url in urls_to_check:
        text = get_page_text(url)
        email, phone = extract_email_and_phone_from_text(text)
        if email or phone:
            return email, phone
    return "", ""

# ========== TRAITEMENT DU FICHIER ==========
# Vérifier si le fichier de résultats existe
if not os.path.exists(FICHIER_RESULTAT):
    print(f"⚠️ Le fichier de résultats {FICHIER_RESULTAT} n'existe pas.")
    
    # Si le fichier unique n'existe pas, chercher les anciens fichiers individuels
    csv_files = glob.glob(f"{RESULTATS_DIR}/*.csv")
    if not csv_files:
        print(f"⚠️ Aucun fichier CSV trouvé dans le dossier {RESULTATS_DIR}")
        exit()
    
    print(f"✅ {len(csv_files)} fichiers CSV individuels trouvés à traiter")
    
    # Traiter les anciens fichiers individuels
    all_data = []
    for csv_index, csv_file in enumerate(csv_files):
        print(f"\n🔍 Lecture du fichier {csv_index+1}/{len(csv_files)}: {csv_file}")
        
        # Lire les données du fichier CSV
        with open(csv_file, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                all_data.append(row)
    
    print(f"✅ Total de {len(all_data)} entrées trouvées dans les fichiers individuels")
else:
    print(f"✅ Fichier de résultats unique trouvé: {FICHIER_RESULTAT}")
    
    # Lire les données du fichier CSV unique
    all_data = []
    with open(FICHIER_RESULTAT, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            all_data.append(row)
    
    print(f"✅ Total de {len(all_data)} entrées trouvées dans le fichier unique")

# Créer le fichier CSV enrichi unique
with open(FICHIER_ENRICHI, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ["Mot-clé", "Nom", "Téléphone", "Site web", "Adresse", "Email trouvé", "Téléphone trouvé sur site"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    
    # Traiter chaque ligne
    for i, row in enumerate(all_data):
        url = row.get("Site web", "").strip()
        email_trouve = ""
        telephone_trouve = ""
        
        if url:
            print(f"  🔎 [{i+1}/{len(all_data)}] Lecture de : {url}")
            email_trouve, telephone_trouve = extract_from_site(url)
            print(f"    ➜ Email : {email_trouve} | Téléphone : {telephone_trouve}")
        else:
            print(f"  ⏭️ [{i+1}/{len(all_data)}] Pas de site web")
        
        # Écrire la ligne enrichie
        writer.writerow({
            "Mot-clé": row.get("Mot-clé", ""),
            "Nom": row.get("Nom", ""),
            "Téléphone": row.get("Téléphone", ""),
            "Site web": url,
            "Adresse": row.get("Adresse", ""),
            "Email trouvé": email_trouve,
            "Téléphone trouvé sur site": telephone_trouve
        })

print(f"\n✅ Enrichissement terminé ! Résultats enregistrés dans {FICHIER_ENRICHI}")
