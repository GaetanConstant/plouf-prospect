import time
import csv
import urllib.parse
import subprocess
import sys
import os.path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import os

# === CONFIGURATION ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MOTS_CLES_CSV = os.path.join(BASE_DIR, "mots_cles.csv")
RESULTATS_DIR = os.path.join(BASE_DIR, "resultats")
FICHIER_RESULTAT = os.path.join(RESULTATS_DIR, "resultats_complets.csv")
FICHIER_PROGRESSION = os.path.join(RESULTATS_DIR, "progression.txt")
ENRICHISSEUR_SCRIPT = os.path.join(BASE_DIR, "enrichisseur.py")

# Mode headless (true = invisible, false = visible)
MODE_HEADLESS = True  # Le mode headless est activé pour éviter les perturbations

# Nombre maximum de fiches à traiter par mot-clé (pour accélérer le traitement)
MAX_FICHES_PAR_MOT_CLE = 20  # Limiter à 20 fiches par mot-clé pour aller plus vite

# Délais d'attente (en secondes) - augmenter pour la stabilité sur serveur
DELAI_CHARGEMENT_PAGE = 5  # Augmenté à 5 secondes pour le serveur
DELAI_SCROLL = 2  # Augmenté à 2 secondes
DELAI_TRAITEMENT_FICHE = 1  # Réduit de 3 à 1 seconde

# Paramètres pour éviter le blocage
MOTS_CLES_AVANT_PAUSE = 100  # Augmenté de 50 à 100 pour accélérer le traitement
DUREE_PAUSE = 30  # Réduit de 60 à 30 secondes pour accélérer le traitement
MAX_TENTATIVES_CONNEXION = 3  # Nombre de tentatives en cas d'erreur de connexion
DELAI_ENTRE_TENTATIVES = 60  # Délai entre les tentatives en cas d'erreur (secondes)

# Créer le dossier de résultats s'il n'existe pas
if not os.path.exists(RESULTATS_DIR):
    os.makedirs(RESULTATS_DIR)

# === Selenium Setup (Firefox) ===
options = FirefoxOptions()

if MODE_HEADLESS:
    options.add_argument("--headless")
    print("✅ Mode headless activé : Firefox s'exécutera en arrière-plan")
else:
    print("⚠️ Mode headless désactivé : Firefox sera visible")

# Options Firefox spécifiques
options.set_preference("dom.webdriver.enabled", False)
options.set_preference("useAutomationExtension", False)
options.set_preference("permissions.default.image", 2)  # Désactive les images pour accélérer

# Taille de la fenêtre indispensable pour le mode headless sur serveur
options.add_argument("--width=1920")
options.add_argument("--height=1080")
# Nettoyage des options Chrome inutiles pour Firefox
options.add_argument("--disable-gpu")

# Liste de user agents Firefox RÉALISTES (obligatoire pour Firefox)
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.1; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0"
]

# Utiliser un user agent aléatoire
import random
options.add_argument(f"--user-agent={random.choice(user_agents)}")

# Fonction pour initialiser le driver avec de nouvelles options
def initialiser_driver():
    try:
        from webdriver_manager.firefox import GeckoDriverManager
        service = FirefoxService(GeckoDriverManager().install())
        return webdriver.Firefox(service=service, options=options)
    except Exception as e:
        print(f"❌ Erreur critique d'initialisation du driver Firefox: {e}")
        return None

# Initialiser le driver
driver = initialiser_driver()
if driver is None:
    print("❌ Impossible d'initialiser le driver Chrome. Vérifiez votre installation.")
    sys.exit(1)

# Fonction pour gérer les consentements de cookies (uniquement sur la page principale)
def handle_cookie_consent():
    try:
        # Attendre que la page soit chargée et que le bouton de consentement soit visible
        wait = WebDriverWait(driver, 5)  # Réduit de 10 à 5 secondes
        
        # Sélecteurs robustes incluant l'anglais (fréquent sur serveur)
        consent_button_selectors = [
            "//button[contains(., 'Tout accepter')]",
            "//button[contains(., 'Accept all')]",
            "//button[contains(., 'I agree')]",
            "//button[contains(., 'Accéder')]",
            "//form//button",  # Souvent le seul bouton du formulaire de consentement
            "//button[@aria-label='Accept all']"
        ]
        
        for selector in consent_button_selectors:
            try:
                consent_button = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                print("✅ Bouton de consentement trouvé, clic en cours...")
                consent_button.click()
                time.sleep(1)  # Réduit de 2 à 1 seconde
                print("✅ Consentement accepté")
                return True
            except:
                continue
        
        print("⚠️ Aucun bouton de consentement trouvé, continuation...")
        return False
    except Exception as e:
        print(f"⚠️ Erreur lors de la gestion du consentement: {e}")
        return False

# Fonction pour sauvegarder la progression
def sauvegarder_progression(index_mot_cle):
    try:
        with open(FICHIER_PROGRESSION, 'w') as f:
            f.write(str(index_mot_cle))
        print(f"✅ Progression sauvegardée: mot-clé {index_mot_cle}")
    except Exception as e:
        print(f"⚠️ Erreur lors de la sauvegarde de la progression: {e}")
        # Tentative de sauvegarde dans un fichier de secours
        try:
            with open(f"{FICHIER_PROGRESSION}.backup", 'w') as f:
                f.write(str(index_mot_cle))
            print(f"✅ Progression sauvegardée dans le fichier de secours")
        except:
            pass

# Fonction pour charger la progression
def charger_progression():
    try:
        if os.path.exists(FICHIER_PROGRESSION):
            with open(FICHIER_PROGRESSION, 'r') as f:
                index = int(f.read().strip())
            print(f"✅ Progression chargée: reprise au mot-clé {index+1}")
            return index
        elif os.path.exists(f"{FICHIER_PROGRESSION}.backup"):
            # Utiliser le fichier de secours si le fichier principal est corrompu
            with open(f"{FICHIER_PROGRESSION}.backup", 'r') as f:
                index = int(f.read().strip())
            print(f"✅ Progression chargée depuis le fichier de secours: reprise au mot-clé {index+1}")
            return index
        else:
            print("✅ Aucune progression sauvegardée, démarrage depuis le début")
            return 0
    except Exception as e:
        print(f"⚠️ Erreur lors du chargement de la progression: {e}")
        return 0

# === Lire les mots-clés depuis le fichier CSV ===
mots_cles = []
try:
    with open(MOTS_CLES_CSV, 'r', encoding='utf-8') as csvfile:
        # Le fichier a une colonne 'mot_cle' avec un en-tête
        reader = csv.reader(csvfile)
        # Lire l'en-tête
        header = next(reader, None)
        for row in reader:
            if row and len(row) > 0 and row[0].strip():  # Vérifier que la ligne n'est pas vide et contient un mot-clé
                mots_cles.append(row[0].strip())
except Exception as e:
    print(f"⚠️ Erreur lors de la lecture du fichier CSV: {e}")
    exit(1)

if not mots_cles:
    print(f"⚠️ Aucun mot-clé trouvé dans {MOTS_CLES_CSV}")
    exit(1)

print(f"✅ {len(mots_cles)} mots-clés chargés depuis {MOTS_CLES_CSV}")
print(f"✅ Limitation à {MAX_FICHES_PAR_MOT_CLE} fiches par mot-clé pour accélérer le traitement")

# Charger la progression précédente
index_debut = charger_progression()

# Vérifier si le fichier de résultats existe déjà
fichier_existe = os.path.exists(FICHIER_RESULTAT)

# Préparer le fichier CSV unique pour tous les résultats
with open(FICHIER_RESULTAT, 'a' if fichier_existe else 'w', newline='', encoding='utf-8') as csvfile:
    csv_writer = csv.writer(csvfile)
    
    # Écrire l'en-tête seulement si le fichier n'existe pas déjà
    if not fichier_existe:
        csv_writer.writerow(["Mot-clé", "Nom", "Téléphone", "Site web", "Adresse"])
    
    # === Traiter chaque mot-clé ===
    for index, mot_cle in enumerate(mots_cles[index_debut:], start=index_debut):
        print(f"\n🔍 Traitement du mot-clé {index+1}/{len(mots_cles)}: {mot_cle}")
        
        # Sauvegarder la progression régulièrement
        if index % 5 == 0:
            sauvegarder_progression(index)
        
        # Faire une pause tous les MOTS_CLES_AVANT_PAUSE mots-clés pour éviter le blocage
        if index > 0 and index % MOTS_CLES_AVANT_PAUSE == 0:
            print(f"⏸️ Pause de {DUREE_PAUSE} secondes pour éviter le blocage...")
            time.sleep(DUREE_PAUSE)
            
            # Réinitialiser le driver périodiquement pour éviter les fuites de mémoire
            print("🔄 Réinitialisation périodique du driver...")
            driver.quit()
            driver = initialiser_driver()
            if driver is None:
                print("⚠️ Échec de la réinitialisation périodique du driver, tentative de récupération...")
                time.sleep(10)
                driver = initialiser_driver()
                if driver is None:
                    raise Exception("Impossible de réinitialiser le driver après plusieurs tentatives")
        
        try:
            # Créer l'URL Google Maps avec le mot-clé
            encoded_keyword = urllib.parse.quote(mot_cle)
            google_maps_url = f"https://www.google.fr/maps/search/{encoded_keyword}"
            
            # Tentatives multiples en cas d'erreur de connexion
            tentative = 0
            success = False
            
            while tentative < MAX_TENTATIVES_CONNEXION and not success:
                try:
                    # Ouvrir Google Maps avec le mot-clé
                    driver.get(google_maps_url)
                    time.sleep(DELAI_CHARGEMENT_PAGE)  # Attendre que la page se charge
                    success = True
                except Exception as e:
                    tentative += 1
                    print(f"⚠️ Erreur de connexion (tentative {tentative}/{MAX_TENTATIVES_CONNEXION}): {e}")
                    
                    if tentative >= MAX_TENTATIVES_CONNEXION:
                        raise Exception(f"Échec après {MAX_TENTATIVES_CONNEXION} tentatives")
                    
                    print(f"⏳ Attente de {DELAI_ENTRE_TENTATIVES} secondes avant nouvelle tentative...")
                    time.sleep(DELAI_ENTRE_TENTATIVES)
                    
                    # Réinitialiser le driver en cas d'erreur persistante
                    if tentative >= 2:
                        print("🔄 Réinitialisation du driver...")
                        driver.quit()
                        driver = initialiser_driver()
                        if driver is None:
                            raise Exception("Impossible de réinitialiser le driver")
            
            # Gérer le consentement des cookies
            time.sleep(2)
            handle_cookie_consent()
            time.sleep(2)

            # Vérifier si on est sur la page de résultats ou bloqué
            if "consent.google" in driver.current_url:
                print("⚠️ Toujours bloqué sur la page de consentement, tentative forcée...")
                driver.get(google_maps_url) # Recharger
                time.sleep(3)
            
            # Collecter les URLs des fiches
            urls = set()
            max_attempts = 3
            attempt = 0
            
            while attempt < max_attempts:
                try:
                    # Essayer différents sélecteurs pour trouver les résultats
                    selectors = [
                        '//div[@role="feed"]',
                        '//div[contains(@class, "section-result")]',
                        '//a[contains(@href, "/maps/place/")]',
                        '//div[contains(@class, "Nv2PK")]',
                        '//div[contains(@class, "lI9IFe")]',
                        '//div[contains(@class, "bfdHYd")]'
                    ]
                    
                    scrollable_div = None
                    for selector in selectors:
                        try:
                            elements = driver.find_elements(By.XPATH, selector)
                            if elements:
                                scrollable_div = elements[0]
                                break
                        except:
                            continue
                    
                    if not scrollable_div:
                        # Si aucun des sélecteurs ne fonctionne, utiliser le body pour scroller
                        scrollable_div = driver.find_element(By.TAG_NAME, 'body')
                    
                    # Scroll pour charger plus de résultats
                    previous_count = 0
                    same_count_tries = 0
                    max_scrolls = 10  # Réduit de 20 à 10 scrolls maximum par mot-clé
                    
                    for i in range(max_scrolls):
                        # Scroller dans la page
                        driver.execute_script("window.scrollBy(0, 500);")  # Scroll plus doux
                        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
                        time.sleep(DELAI_SCROLL)
                        
                        # Collecter les liens vers les fiches
                        links = driver.find_elements(By.XPATH, '//a[contains(@href, "/maps/place/")]')
                        for link in links:
                            href = link.get_attribute("href")
                            if href and "/maps/place/" in href:
                                urls.add(href)
                                # Si on a atteint le nombre maximum de fiches, on arrête
                                if len(urls) >= MAX_FICHES_PAR_MOT_CLE:
                                    break
                        
                        current_count = len(urls)
                        print(f"  🌀 Scroll {i+1} → {current_count} fiches collectées")
                        
                        # Si on a atteint le nombre maximum de fiches, on arrête
                        if current_count >= MAX_FICHES_PAR_MOT_CLE:
                            print(f"  ✅ Nombre maximum de fiches atteint ({MAX_FICHES_PAR_MOT_CLE}).")
                            break
                        
                        if current_count == previous_count:
                            same_count_tries += 1
                        else:
                            same_count_tries = 0
                            previous_count = current_count
                        
                        if same_count_tries >= 3:  # Réduit de 5 à 3 tentatives sans nouvelles fiches
                            print("  ✅ Fin du scroll : plus de nouvelles fiches après 3 tentatives.")
                            break
                    
                    # Si on a trouvé des URLs, on peut sortir de la boucle de tentatives
                    if urls:
                        break
                    
                    attempt += 1
                    print(f"  ⚠️ Tentative {attempt}/{max_attempts} échouée. Réessai...")
                    time.sleep(1)  # Réduit de 2 à 1 seconde
                    
                except Exception as e:
                    print(f"  ⚠️ Erreur lors du scroll: {e}")
                    attempt += 1
                    time.sleep(1)  # Réduit de 2 à 1 seconde
            
            # === Traitement des fiches ===
            urls = list(urls)[:MAX_FICHES_PAR_MOT_CLE]  # Limiter au nombre maximum de fiches
            print(f"  ✅ {len(urls)} fiches prêtes à être scrapées pour le mot-clé: {mot_cle}")
            
            if not urls:
                print(f"  ⚠️ Aucune fiche trouvée pour le mot-clé: {mot_cle}")
                # Écrire une ligne vide pour ce mot-clé pour indiquer qu'il a été traité
                csv_writer.writerow([mot_cle, "", "", "", ""])
                continue
            
            # En mode headless, pas besoin de créer un nouvel onglet, on peut directement naviguer
            if not MODE_HEADLESS:
                # Créer un nouvel onglet pour traiter les fiches
                driver.execute_script("window.open('about:blank', '_blank');")
            
            for i, url in enumerate(urls):
                try:
                    if MODE_HEADLESS:
                        # En mode headless, on peut simplement naviguer vers l'URL
                        driver.get(url)
                    else:
                        # En mode visible, utiliser le second onglet pour les fiches
                        driver.switch_to.window(driver.window_handles[1])
                        driver.get(url)
                    
                    time.sleep(DELAI_TRAITEMENT_FICHE)
                    
                    # Extraire les informations de la fiche
                    nom, tel, site, adresse = "", "", "", ""
                    
                    try:
                        nom_elements = driver.find_elements(By.XPATH, '//h1')
                        if nom_elements:
                            nom = nom_elements[0].text
                    except:
                        pass
                    
                    try:
                        tel_elements = driver.find_elements(By.XPATH, '//button[contains(@aria-label, "Appeler")]')
                        if tel_elements:
                            tel = tel_elements[0].text
                    except:
                        pass
                    
                    try:
                        site_elements = driver.find_elements(By.XPATH, '//a[contains(@data-item-id, "authority")]')
                        if site_elements:
                            site = site_elements[0].get_attribute("href")
                    except:
                        pass
                    
                    try:
                        adresse_elements = driver.find_elements(By.XPATH, '//button[contains(@aria-label, "Copier l\'adresse")]//div[1]')
                        if adresse_elements:
                            adresse = adresse_elements[0].text
                    except:
                        pass
                    
                    print(f"  ✅ {i+1}/{len(urls)} | {nom} | {tel} | {site}")
                    csv_writer.writerow([mot_cle, nom, tel, site, adresse])
                    csvfile.flush()  # Forcer l'écriture dans le fichier après chaque ligne
                    
                    if not MODE_HEADLESS:
                        # Revenir à l'onglet principal en mode visible
                        driver.switch_to.window(driver.window_handles[0])
                    
                except Exception as e:
                    print(f"  ⚠️ Erreur lors du traitement de la fiche {i+1}: {e}")
                    # Écrire une ligne avec le mot-clé mais des valeurs vides pour les autres colonnes
                    csv_writer.writerow([mot_cle, "", "", "", ""])
                    csvfile.flush()  # Forcer l'écriture dans le fichier après chaque ligne
                    if not MODE_HEADLESS:
                        try:
                            # S'assurer qu'on revient à l'onglet principal en cas d'erreur
                            driver.switch_to.window(driver.window_handles[0])
                        except:
                            pass
        
        except Exception as e:
            print(f"⚠️ Erreur lors du traitement du mot-clé {mot_cle}: {e}")
            # Écrire une ligne avec le mot-clé mais des valeurs vides pour les autres colonnes
            csv_writer.writerow([mot_cle, "", "", "", ""])
            csvfile.flush()  # Forcer l'écriture dans le fichier après chaque ligne
            
            # Vérifier si le driver est toujours fonctionnel
            try:
                driver.current_url  # Simple test pour voir si le driver répond
            except:
                print("⚠️ Le driver semble être en erreur, tentative de réinitialisation...")
                try:
                    driver.quit()
                except:
                    pass
                driver = initialiser_driver()
                if driver is None:
                    print("⚠️ Échec de la réinitialisation du driver, nouvelle tentative dans 30 secondes...")
                    time.sleep(30)
                    driver = initialiser_driver()
                    if driver is None:
                        print("❌ Impossible de réinitialiser le driver après plusieurs tentatives")
                        raise Exception("Échec critique: impossible de réinitialiser le driver")
        
        # Sauvegarder la progression après chaque mot-clé
        sauvegarder_progression(index + 1)

print("\n✅ Scraping terminé !")
driver.quit()

# Conserver le fichier de progression pour référence
if os.path.exists(FICHIER_PROGRESSION):
    # Renommer le fichier avec un timestamp au lieu de le supprimer
    import time
    timestamp = int(time.time())
    os.rename(FICHIER_PROGRESSION, f"{FICHIER_PROGRESSION}.{timestamp}.completed")
    print(f"✅ Fichier de progression sauvegardé comme {FICHIER_PROGRESSION}.{timestamp}.completed")

# Supprimer le fichier de secours s'il existe
if os.path.exists(f"{FICHIER_PROGRESSION}.backup"):
    os.remove(f"{FICHIER_PROGRESSION}.backup")

# === Lancer l'enrichissement automatiquement ===
print("\n🔄 Lancement automatique de l'enrichissement des données...")

try:
    # Vérifier que le script d'enrichissement existe
    if not os.path.exists(ENRICHISSEUR_SCRIPT):
        print(f"⚠️ Script d'enrichissement {ENRICHISSEUR_SCRIPT} non trouvé.")
        exit(1)
    
    # Lancer le script d'enrichissement avec le même interpréteur Python
    print(f"🚀 Exécution de {ENRICHISSEUR_SCRIPT}...")
    subprocess.run([sys.executable, ENRICHISSEUR_SCRIPT])
    
    print("\n✅ Processus complet terminé ! Les données ont été scrapées et enrichies.")
except Exception as e:
    print(f"⚠️ Erreur lors du lancement de l'enrichissement: {e}")
    print("Vous pouvez lancer manuellement l'enrichissement avec la commande: python enrichisseur.py")
