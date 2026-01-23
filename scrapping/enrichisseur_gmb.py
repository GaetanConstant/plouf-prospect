import os
import csv
import time
import random
import urllib.parse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# === CONFIGURATION ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(BASE_DIR, "resultats_dirigeants", "resultats_dirigeants.csv")
OUTPUT_FILE = os.path.join(BASE_DIR, "resultats_dirigeants", "resultats_dirigeants_enrichis_gmb.csv")

MODE_HEADLESS = True
WAIT_TIME = 2

# === Selenium Setup ===
def initialiser_driver():
    # 1. Tentative avec Chrome
    try:
        from selenium.webdriver.chrome.options import Options as ChromeOptions
        from selenium.webdriver.chrome.service import Service as ChromeService
        from webdriver_manager.chrome import ChromeDriverManager
        
        chrome_options = ChromeOptions()
        if MODE_HEADLESS:
            chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        ]
        chrome_options.add_argument(f"--user-agent={random.choice(user_agents)}")
        
        print("🌐 Tentative d'initialisation de Chrome...")
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        print(f"⚠️ Chrome non disponible ou erreur : {e}")

    # 2. Tentative avec Firefox
    try:
        from selenium.webdriver.firefox.options import Options as FirefoxOptions
        from selenium.webdriver.firefox.service import Service as FirefoxService
        from webdriver_manager.firefox import GeckoDriverManager
        
        firefox_options = FirefoxOptions()
        if MODE_HEADLESS:
            firefox_options.add_argument("-headless")
        
        print("🦊 Tentative d'initialisation de Firefox...")
        service = FirefoxService(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service, options=firefox_options)
        return driver
    except Exception as e:
        print(f"❌ Firefox non disponible ou erreur : {e}")
        
    return None

def handle_cookie_consent(driver):
    try:
        wait = WebDriverWait(driver, 3)
        consent_button_selectors = [
            "//button[contains(., 'Tout accepter')]",
            "//button[contains(., 'J'accepte')]",
            "//button[contains(., 'Accepter')]"
        ]
        for selector in consent_button_selectors:
            try:
                button = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                button.click()
                return True
            except:
                continue
    except:
        pass
    return False

def get_gmb_phone(driver, query):
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"https://www.google.com/maps/search/{encoded_query}"
        driver.get(url)
        time.sleep(WAIT_TIME)
        
        handle_cookie_consent(driver)
        
        # S'il y a plusieurs résultats, on prend le premier s'il semble correspondre
        # Mais souvent avec une recherche précise "Nom + Ville", on tombe soit sur la fiche directe, soit sur une liste
        
        # Tentative d'extraire le téléphone sur une fiche directe
        try:
            # Sélecteurs pour le téléphone sur Google Maps
            tel_selectors = [
                '//button[contains(@aria-label, "Appeler")]',
                '//button[contains(@data-item-id, "phone:tel:")]',
                '//div[contains(@aria-label, "Appeler")]'
            ]
            for selector in tel_selectors:
                elements = driver.find_elements(By.XPATH, selector)
                if elements:
                    tel = elements[0].get_attribute("aria-label") or elements[0].text
                    if tel:
                        # Nettoyer le numéro (enlever "Appeler le ", "Numéro de téléphone: ", etc.)
                        tel = tel.replace("Appeler le ", "").replace("Appeler ", "").replace("Numéro de téléphone: ", "").replace("Numero de telephone: ", "").strip()
                        return tel
        except:
            pass
            
        # Si on est sur une liste de résultats, on clique sur le premier
        try:
            results = driver.find_elements(By.XPATH, '//a[contains(@href, "/maps/place/")]')
            if results:
                results[0].click()
                time.sleep(WAIT_TIME)
                # Ré-essayer d'extraire le téléphone
                for selector in tel_selectors:
                    elements = driver.find_elements(By.XPATH, selector)
                    if elements:
                        tel = elements[0].get_attribute("aria-label") or elements[0].text
                        if tel:
                            tel = tel.replace("Appeler le ", "").replace("Appeler ", "").replace("Numéro de téléphone: ", "").replace("Numero de telephone: ", "").strip()
                            return tel
        except:
            pass
            
    except Exception as e:
        print(f"⚠️ Erreur lors de la recherche pour '{query}' : {e}")
    
    return ""
    
def sauvegarder_resultats(file_path, fieldnames, rows):
    with open(file_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Fichier non trouvé : {INPUT_FILE}")
        return

    rows = []
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            rows.append(row)

    print(f"📋 {len(rows)} lignes chargées.")
    
    # Identifier les lignes à enrichir
    to_enrich = []
    for i, row in enumerate(rows):
        tel = row.get('Téléphone', '').strip()
        tel_site = row.get('Téléphone trouvé sur site', '').strip()
        if not tel and not tel_site:
            to_enrich.append(i)
    
    print(f"🔍 {len(to_enrich)} lignes n'ont pas de téléphone. Début de l'enrichissement GMB...")
    
    if not to_enrich:
        print("✅ Toutes les lignes ont déjà un téléphone.")
        return

    driver = initialiser_driver()
    if not driver:
        return

    try:
        count = 0
        for idx in to_enrich:
            row = rows[idx]
            nom = row.get('Nom', '')
            mot_cle = row.get('Mot-clé', '')
            
            # Nettoyer le mot-clé pour la recherche (enlever "coiffeurs" si redondant ?)
            # On va garder Nom + Mot-clé c'est souvent efficace
            query = f"{nom} {mot_cle}"
            
            print(f"🔎 [{count+1}/{len(to_enrich)}] Recherche GMB pour : {query}")
            phone = get_gmb_phone(driver, query)
            
            if phone:
                print(f"  ✅ Téléphone trouvé : {phone}")
                row['Téléphone'] = phone
                row['Status Recherche'] = "Enrichi GMB"
            else:
                print(f"  ❌ Pas de téléphone trouvé.")
            
            count += 1
            # Sauvegarde incrémentale
            sauvegarder_resultats(OUTPUT_FILE, fieldnames, rows)
            
            # Petite pause pour éviter le blocage
            time.sleep(random.uniform(1, 2))
            
    finally:
        driver.quit()

    print(f"💾 Fin de l'enrichissement. Résultats finaux dans : {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
