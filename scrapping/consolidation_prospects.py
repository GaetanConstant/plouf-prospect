
import csv
import os
import re

# === CONFIGURATION ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Liste de priorité des fichiers d'entrée (du plus enrichi au moins enrichi)
CANDIDATE_INPUT_FILES = [
    os.path.join(BASE_DIR, "resultats_dirigeants", "resultats_finaux_complets.csv"),          # 1. Enrichi Whois
    os.path.join(BASE_DIR, "resultats_dirigeants", "resultats_dirigeants_enrichis_gmb.csv"),  # 2. Enrichi GMB
    os.path.join(BASE_DIR, "resultats_dirigeants", "resultats_dirigeants.csv"),               # 3. Enrichi Dirigeants
    os.path.join(BASE_DIR, "resultats_enrichis", "resultats_enrichis_complets.csv"),          # 4. Enrichi Web
    os.path.join(BASE_DIR, "resultats", "resultats_complets.csv")                             # 5. Raw Scraping
]

INPUT_FILE = None
for f in CANDIDATE_INPUT_FILES:
    if os.path.exists(f):
        INPUT_FILE = f
        print(f"✅ Fichier d'entrée trouvé pour consolidation : {os.path.basename(INPUT_FILE)}")
        break

if not INPUT_FILE:
    # Fallback par défaut pour affichage d'erreur plus tard
    INPUT_FILE = CANDIDATE_INPUT_FILES[0]

OUTPUT_FILE = os.path.join(BASE_DIR, "resultats_consolides", "base_prospects_finale.csv")

def clean_phone(phone):
    if not phone:
        return ""
    # Garder seulement les chiffres et le +
    return re.sub(r'[^\d+]', '', str(phone))

def is_mobile(phone):
    clean = clean_phone(phone)
    # Check français mobile (06, 07)
    if clean.startswith('06') or clean.startswith('07') or clean.startswith('+336') or clean.startswith('+337'):
        return True
    return False

def main():
    print("🚀 Consolidation de la base prospects...")
    
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Fichier d'entrée non trouvé : {INPUT_FILE}")
        return

    prospects = []
    
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 1. Priorisation Téléphone
            # Ordre de préférence : Mobile Site > Mobile Whois > Mobile GMB > Fixe Site > Fixe Whois > Fixe GMB
            tel_gmb = row.get('Téléphone', '').strip()
            tel_site = row.get('Téléphone trouvé sur site', '').strip()
            tel_whois = row.get('Whois_Phone', '').strip()
            
            # Nettoyer tel_whois (il peut y en avoir plusieurs séparés par des virgules)
            tels_whois_list = [t.strip() for t in tel_whois.split(',')] if tel_whois else []
            
            # Trouver le meilleur tel whois (mobile en priorité)
            best_tel_whois = ""
            for t in tels_whois_list:
                if is_mobile(t):
                    best_tel_whois = t
                    break
            if not best_tel_whois and tels_whois_list:
                best_tel_whois = tels_whois_list[0]
            
            # Algorithme de sélection
            tels_candidats = [
                ('site', tel_site),
                ('whois', best_tel_whois),
                ('gmb', tel_gmb)
            ]
            
            telephone = ""
            telephone_secondaire = ""
            
            # 1. Chercher un mobile
            for source, tel in tels_candidats:
                if tel and is_mobile(tel):
                    if not telephone:
                        telephone = tel
                    elif not telephone_secondaire and tel != telephone:
                        telephone_secondaire = tel
            
            # 2. Si pas de mobile principal, prendre un fixe
            if not telephone:
                for source, tel in tels_candidats:
                    if tel:
                        telephone = tel
                        break
            
            # 3. Remplir le secondaire si vide
            if not telephone_secondaire:
                 for source, tel in tels_candidats:
                    if tel and tel != telephone:
                        telephone_secondaire = tel
                        break

            # 2. Priorisation Email
            # Email du site > Email Whois
            email = row.get('Email trouvé', '').strip()
            email_whois = row.get('Whois_Emails', '').strip()
            
            if not email and email_whois:
                # Whois peut contenir une liste, on prend le premier qui ne soit pas "abuse" ou "tech" si possible
                parts = [e.strip() for e in email_whois.split(',')]
                valid_emails = [e for e in parts if 'abuse' not in e and 'tech' not in e]
                if valid_emails:
                    email = valid_emails[0]
                elif parts:
                    email = parts[0]
            
            # 3. Dirigeant
            dirigeant = row.get('Dirigeants', '').strip()
            if dirigeant == "Non listé" or dirigeant == "Voir sur Pappers":
                dirigeant = ""
                
            # Création de l'objet prospect consolidé
            prospect = {
                "Nom Entreprise": row.get('Nom', ''),
                "Activité": row.get('Mot-clé', ''), # Ou Code NAF si dispo
                "Dirigeant": dirigeant,
                "Email": email,
                "Téléphone": telephone,
                "Téléphone Secondaire": telephone_secondaire,
                "Site Web": row.get('Site web', ''),
                "Adresse": row.get('Adresse', ''),
                "Code Postal": row.get('Whois_Zipcode', '') or row.get('Adresse', '')[-5:] if row.get('Adresse') and row.get('Adresse')[-1].isdigit() else "", # Tentative simple
                "Ville": row.get('Whois_City', ''),
                "SIRET": row.get('SIRET', ''),
                "Date Création": row.get('Whois_Creation_Date', ''),
                "Lien Pappers": row.get('Lien Pappers', '')
            }
            
            prospects.append(prospect)

    # Sauvegarde
    if prospects:
        fieldnames = list(prospects[0].keys())
        with open(OUTPUT_FILE, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(prospects)
            
        print(f"✅ Consolidation terminée ! {len(prospects)} prospects exportés.")
        print(f"💾 Fichier final : {OUTPUT_FILE}")
    else:
        print("⚠️ Aucun prospect à exporter.")

if __name__ == "__main__":
    main()
