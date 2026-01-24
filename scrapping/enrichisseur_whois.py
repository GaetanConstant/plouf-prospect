
import os
import csv
import time
import requests
import random
import whois
import tldextract
from datetime import datetime

# === CONFIGURATION ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# On prend le fichier enrichi par GMB comme entrée
INPUT_FILE = os.path.join(BASE_DIR, "resultats_dirigeants", "resultats_dirigeants_enrichis_gmb.csv")
# Si le fichier GMB n'existe pas, on prend le fichier de base
if not os.path.exists(INPUT_FILE):
    INPUT_FILE = os.path.join(BASE_DIR, "resultats_dirigeants", "resultats_dirigeants.csv")

OUTPUT_FILE = os.path.join(BASE_DIR, "resultats_dirigeants", "resultats_finaux_complets.csv")

def extract_domain(url_or_email):
    """Extrait le domaine principal d'une URL ou d'un email."""
    if not url_or_email:
        return None
    
    # Nettoyage basique
    url_or_email = url_or_email.strip().lower()
    
    # Si c'est un email
    if "@" in url_or_email and not url_or_email.startswith("http"):
        return url_or_email.split("@")[-1]
    
    # Si c'est une URL
    extracted = tldextract.extract(url_or_email)
    if extracted.domain and extracted.suffix:
        return f"{extracted.domain}.{extracted.suffix}"
    return None

def get_whois_info(domain):
    """Récupère les infos WHOIS pour un domaine."""
    try:
        w = whois.whois(domain)
        return w
    except Exception as e:
        # print(f"  ⚠️ Erreur WHOIS pour {domain}: {e}")
        return None

def format_date(date_obj):
    """Formate une date en string (si c'est une liste, prend la première)."""
    if isinstance(date_obj, list):
        date_obj = date_obj[0]
    if isinstance(date_obj, datetime):
        return date_obj.strftime("%Y-%m-%d")
    return str(date_obj) if date_obj else ""

def format_list(item):
    """Formate une liste en string séparée par des virgules."""
    if isinstance(item, list):
        return ", ".join([str(i) for i in item if i])
    return str(item) if item else ""

def get_rdap_info_fr(domain):
    """
    Récupère les infos RDAP via l'AFNIC pour les domaines en .fr
    Retourne un dictionnaire avec les infos trouvées ou None.
    """
    if not domain.endswith('.fr'):
        return None
        
    try:
        url = f"https://rdap.nic.fr/domain/{domain}"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            info = {
                'creation_date': None,
                'updated_date': None,
                'expiration_date': None,
                'registrar': None,
                'emails': [],
                'phones': [],
                'address': [],
                'city': [],
                'zipcode': [],
                'country': []
            }
            
            # Dates (events)
            for event in data.get('events', []):
                evt_action = event.get('eventAction')
                evt_date = event.get('eventDate')
                if evt_action == 'registration':
                    info['creation_date'] = evt_date[:10] # YYYY-MM-DD
                elif evt_action == 'last changed':
                    info['updated_date'] = evt_date[:10]
                elif evt_action == 'expiration':
                    info['expiration_date'] = evt_date[:10]
            
            # Entities (contacts)
            for entity in data.get('entities', []):
                roles = entity.get('roles', [])
                
                # Registrar
                if 'registrar' in roles:
                     # Parfois le nom est dans vcardArray
                     vcard = entity.get('vcardArray', [])
                     if len(vcard) > 1:
                         for item in vcard[1]:
                             if item[0] == 'fn':
                                 info['registrar'] = item[3]

                # Registrant / Admin / Tech -> On cherche les infos de contact
                if any(r in roles for r in ['registrant', 'administrative', 'technical']):
                    vcard = entity.get('vcardArray', [])
                    if len(vcard) > 1:
                        for item in vcard[1]:
                            # Email
                            if item[0] == 'email':
                                info['emails'].append(item[3])
                            # Tel
                            elif item[0] == 'tel':
                                # uri "tel:+33.xxx"
                                uri = item[3] if len(item) > 3 else ""
                                if uri.startswith('tel:'):
                                    info['phones'].append(uri.replace('tel:', '').replace('.', ' '))
                            # Adresse
                            elif item[0] == 'adr':
                                # ["", "", "rue", "ville", "", "cp", "pays"]
                                vals = item[3]
                                if len(vals) >= 7:
                                    # Parfois c'est une liste de listes ou une chaine
                                    addr = vals[2]
                                    if isinstance(addr, list): addr = " ".join([str(x) for x in addr])
                                    if addr: info['address'].append(str(addr))
                                    
                                    city = vals[3]
                                    if isinstance(city, list): city = " ".join([str(x) for x in city])
                                    if city: info['city'].append(str(city))
                                    
                                    zipc = vals[5]
                                    if isinstance(zipc, list): zipc = " ".join([str(x) for x in zipc])
                                    if zipc: info['zipcode'].append(str(zipc))
                                    
                                    country = vals[6]
                                    if isinstance(country, list): country = " ".join([str(x) for x in country])
                                    if country: info['country'].append(str(country))

            # Deduplicate
            info['emails'] = list(set(info['emails']))
            info['phones'] = list(set(info['phones']))
            info['address'] = list(set(info['address']))
            
            return info
            
    except Exception as e:
        print(f"⚠️ Erreur RDAP pour {domain}: {e}")
    
    return None

def sauvegarder_resultats(file_path, fieldnames, rows):
    with open(file_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def main():
    print("🚀 Démarrage de l'enrichissement WHOIS...")
    
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Fichier d'entrée non trouvé : {INPUT_FILE}")
        return

    rows = []
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        # Ajouter les nouvelles colonnes si elles n'existent pas
        new_columns = ['Whois_Domain', 'Whois_Creation_Date', 'Whois_Expiration_Date', 'Whois_Registrar', 'Whois_Emails', 'Whois_Name', 'Whois_Org', 'Whois_Address', 'Whois_City', 'Whois_Zipcode', 'Whois_Country', 'Whois_Updated_Date', 'Whois_Phone']
        for col in new_columns:
            if col not in fieldnames:
                fieldnames.append(col)
        
        for row in reader:
            rows.append(row)

    print(f"📋 {len(rows)} lignes chargées depuis {INPUT_FILE}.")
    
    processed_count = 0
    
    for i, row in enumerate(rows):
        # On essaie de trouver un domaine via le site web, sinon via l'email
        site_web = row.get('Site web', '') or row.get('Site Web', '')
        # Si pas de site web, on peut essayer de déduire d'autres champs si dispo, mais ici on reste simple
        
        domain = extract_domain(site_web)
        
        # Si on a déjà les infos, on ne refait pas (sauf si on veut forcer)
        # if row.get('Whois_Domain') and row.get('Whois_Creation_Date'):
        #     continue
            
        if domain:
            print(f"Terminé ({i+1}/{len(rows)}) : Enrichment pour {domain}...")
            
            # 1. Tentative RDAP (Prioritaire pour .fr)
            rdap_data = get_rdap_info_fr(domain)
            
            if rdap_data:
                 print(f"  ✨ RDAP Success (AFNIC) !")
                 row['Whois_Domain'] = domain
                 row['Whois_Creation_Date'] = rdap_data['creation_date']
                 row['Whois_Expiration_Date'] = rdap_data['expiration_date']
                 row['Whois_Updated_Date'] = rdap_data['updated_date']
                 row['Whois_Registrar'] = rdap_data['registrar']
                 row['Whois_Emails'] = format_list(rdap_data['emails'])
                 row['Whois_Phone'] = format_list(rdap_data['phones'])
                 row['Whois_Address'] = format_list(rdap_data['address'])
                 row['Whois_City'] = format_list(rdap_data['city'])
                 row['Whois_Zipcode'] = format_list(rdap_data['zipcode'])
                 row['Whois_Country'] = format_list(rdap_data['country'])
                 print(f"  ✅ Données trouvées (Créé le: {row['Whois_Creation_Date']}, Tel: {row['Whois_Phone']})")
                 
            else:
                # 2. Fallback WHOIS Standard
                w_info = get_whois_info(domain)
                
                if w_info:
                    row['Whois_Domain'] = domain
                    row['Whois_Creation_Date'] = format_date(w_info.creation_date)
                    row['Whois_Expiration_Date'] = format_date(w_info.expiration_date)
                    row['Whois_Registrar'] = w_info.registrar
                    row['Whois_Emails'] = format_list(w_info.emails)
                    row['Whois_Name'] = format_list(w_info.name)
                    row['Whois_Org'] = format_list(w_info.org)
                    row['Whois_Address'] = format_list(w_info.address)
                    row['Whois_City'] = format_list(w_info.city)
                    row['Whois_Zipcode'] = format_list(w_info.zipcode)
                    row['Whois_Country'] = format_list(w_info.country)
                    row['Whois_Updated_Date'] = format_date(w_info.updated_date)
                    
                    # Tentative de récupération des téléphones (champs variables selon les TLD)
                    phones = []
                    for p_field in ['phone', 'registrant_phone', 'admin_phone', 'tech_phone', 'registrar_phone']:
                        val = getattr(w_info, p_field, None) or w_info.get(p_field)
                        if val:
                            phones.append(str(val))
                    row['Whois_Phone'] = ", ".join(list(set(phones)))
                    
                    print(f"  ✅ Données trouvées (Créé le: {row['Whois_Creation_Date']})")
                else:
                    row['Whois_Domain'] = domain
                    print(f"  ❌ Pas de données WHOIS trouvées.")
            
            # Petite pause pour être gentil avec les serveurs WHOIS
            time.sleep(random.uniform(0.5, 1.5))
        else:
            # print(f"  ⚠️ Pas de domaine extractible pour la ligne {i+1}")
            pass
            
        processed_count += 1
        
        # Sauvegarde régulière (toutes les 5 lignes)
        if processed_count % 5 == 0:
            sauvegarder_resultats(OUTPUT_FILE, fieldnames, rows)

    # Sauvegarde finale
    sauvegarder_resultats(OUTPUT_FILE, fieldnames, rows)
    print(f"💾 Enrichissement terminé. Fichier sauvegardé : {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
