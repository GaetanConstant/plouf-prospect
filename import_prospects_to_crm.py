import pandas as pd
import os
from datetime import datetime

# Paths
SOURCE_FILE = "scrapping/resultats_consolides/base_prospects_finale.csv"
DEST_FILE = "crm_scopa.csv"

def parse_dirigeant(dirigeant_str):
    """
    Parses 'NAME (Title) | ...' to extract first and last name.
    Takes the first person in the list.
    """
    if pd.isna(dirigeant_str) or not dirigeant_str:
        return "", ""
    
    # Get the first person before the pipe
    first_person = dirigeant_str.split("|")[0].strip()
    # Remove the title in parentheses
    name_only = first_person.split("(")[0].strip()
    
    # Simple split into first and last name
    parts = name_only.split(" ")
    if len(parts) >= 2:
        first_name = parts[0]
        last_name = " ".join(parts[1:])
    else:
        first_name = name_only
        last_name = ""
    
    return first_name, last_name

def main():
    if not os.path.exists(SOURCE_FILE):
        print(f"Erreur: Le fichier source {SOURCE_FILE} n'existe pas.")
        return

    if not os.path.exists(DEST_FILE):
        print(f"Erreur: Le fichier destination {DEST_FILE} n'existe pas.")
        return

    # Load data
    df_source = pd.read_csv(SOURCE_FILE)
    df_dest = pd.read_csv(DEST_FILE)

    print(f"Importation de {len(df_source)} prospects depuis {SOURCE_FILE}...")

    # Prepare new rows
    new_rows = []
    
    # Existing companies in CRM to avoid duplicates (by name)
    existing_companies = set(df_dest['Company Name for Emails'].dropna().str.lower().tolist())

    for _, row in df_source.iterrows():
        company_name = str(row.get('Nom Entreprise', '')).strip()
        
        # Simple duplicate check
        if company_name.lower() in existing_companies:
            print(f"Skipping duplicate: {company_name}")
            continue
            
        first_name, last_name = parse_dirigeant(row.get('Dirigeant', ''))
        
        # Mapping: Activité -> origine_contact
        origin = str(row.get('Activité', 'Plouf Scraper')).strip()
        
        # Website priority: Site Web > Lien Pappers
        website = row.get('Site Web')
        if pd.isna(website) or not str(website).strip():
            website = row.get('Lien Pappers')
        
        # Phone priority: Téléphone > Téléphone Secondaire
        phone = row.get('Téléphone')
        if pd.isna(phone) or not str(phone).strip():
            phone = row.get('Téléphone Secondaire')

        # Build address
        addr_parts = [
            str(row.get('Adresse', '')).strip(),
            str(row.get('Code Postal', '')).strip(),
            str(row.get('Ville', '')).strip()
        ]
        full_address = ", ".join([p for p in addr_parts if p and p != 'nan' and p != ''])

        # Build commentary
        commentary = f"SIRET: {row.get('SIRET', '')}"
        # If we used pappers as website, or if we have it separately, keep note
        if row.get('Lien Pappers') and row.get('Lien Pappers') != website:
            commentary += f"\nLien Pappers: {row.get('Lien Pappers')}"
        if row.get('Téléphone Secondaire') and row.get('Téléphone Secondaire') != phone:
            commentary += f"\nTél Sec: {row.get('Téléphone Secondaire')}"

        new_row = {
            'Contacté': None,
            'First Name': first_name,
            'Last Name': last_name,
            'Title': None,
            'Company Name for Emails': company_name,
            'Email': row.get('Email', None),
            '# Employees': None,
            'Industry': origin,
            'Person Linkedin Url': None,
            'Website': website,
            'Company Address': full_address,
            'Commentaire': commentary,
            'Commercial': None,
            'Statut': 'Non contacté',
            'origine_contact': origin,
            'Phone': phone
        }
        new_rows.append(new_row)

    if not new_rows:
        print("Aucun nouveau prospect à importer.")
        return

    df_new = pd.DataFrame(new_rows)
    
    # Append to destination
    df_final = pd.concat([df_dest, df_new], ignore_index=True)
    
    # Save back
    df_final.to_csv(DEST_FILE, index=False)
    
    print(f"Succès ! {len(new_rows)} prospects importés dans {DEST_FILE}.")

if __name__ == "__main__":
    main()
