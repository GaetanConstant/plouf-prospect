import requests
import pandas as pd
import json
import os
from datetime import datetime

def scrape_business_calade():
    print("🚀 Début du scraping des membres de Business Calade...")
    
    url = "https://api.groupconnect.app/rest/v1/rpc/api_get_members"
    headers = {
        "Content-Type": "application/json",
        "apikey": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoiYW5vbiIsImlzcyI6InN1cGFiYXNlIiwiaWF0IjoxNzU1NTU0NDAwLCJleHAiOjE5MTMzMjA4MDB9.R3wnW7xqCp7qtl53jGXhnD53H9dbnqtKtwwoRlwl-qg"
    }
    payload = {
        "in_api_token": "f66d1580-feda-4cee-b925-371b4da4cd14",
        "in_has_active_membership": True
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        
        print(f"📦 {len(data)} entreprises reçues de l'API.")
        
        all_members = []
        
        for company in data:
            # L'API renvoie une liste d'entreprises, chacune ayant une liste d'utilisateurs
            company_name = company.get("name", "N/A")
            activity = company.get("activity", "N/A")
            address = company.get("address", "N/A")
            cp_city = company.get("cp_city", "N/A")
            company_phone = company.get("phone", "N/A")
            website = company.get("website", "N/A")
            
            users = company.get("users", [])
            if not users:
                # Si pas d'utilisateurs, on garde quand même l'entreprise
                all_members.append({
                    "Entreprise": company_name,
                    "Activité": activity,
                    "Adresse": f"{address} {cp_city}".strip(),
                    "Téléphone Entreprise": company_phone,
                    "Site Web": website,
                    "Nom Dirigeant": "N/A",
                    "Poste": "N/A",
                    "Email": "N/A",
                    "Téléphone Dirigeant": "N/A"
                })
            else:
                for user in users:
                    # On ignore certains profils si nécessaire (comme dans le script original)
                    if user.get("email") == "adesjobert@adefipatrimoine.fr":
                        continue
                        
                    all_members.append({
                        "Entreprise": company_name,
                        "Activité": activity,
                        "Adresse": f"{address} {cp_city}".strip(),
                        "Téléphone Entreprise": company_phone,
                        "Site Web": website,
                        "Nom Dirigeant": f"{user.get('first_name', '')} {user.get('last_name', '')}".strip(),
                        "Poste": user.get("company_position", "N/A"),
                        "Email": user.get("email", "N/A"),
                        "Téléphone Dirigeant": user.get("phone", "N/A")
                    })
        
        df = pd.DataFrame(all_members)
        
        # Sauvegarde
        output_dir = "resultats_business_calade"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        filename = f"{output_dir}/membres_business_calade_{datetime.now().strftime('%Y%m%d')}.csv"
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        
        print(f"✅ Scraping terminé ! {len(all_members)} contacts extraits.")
        print(f"📄 Fichier sauvegardé : {filename}")
        
        return filename

    except Exception as e:
        print(f"❌ Erreur lors du scraping : {e}")
        return None

if __name__ == "__main__":
    scrape_business_calade()
