import streamlit as st
import pandas as pd
import subprocess
import os
import sys
import time
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Plouf Scraper",
    page_icon="🤖",
    layout="wide"
)

# Dossiers et fichiers
SCRAPPING_DIR = os.path.dirname(os.path.abspath(__file__))
MOTS_CLES_CSV = os.path.join(SCRAPPING_DIR, "mots_cles.csv")
RESULTATS_DIR_RAW = os.path.join(SCRAPPING_DIR, "resultats")
RESULTATS_DIR_ENRICHED = os.path.join(SCRAPPING_DIR, "resultats_enrichis")
FICHIER_RAW = os.path.join(RESULTATS_DIR_RAW, "resultats_complets.csv")
FICHIER_ENRICHI = os.path.join(RESULTATS_DIR_ENRICHED, "resultats_enrichis_complets.csv")

# Styles CSS
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #ff4b4b;
        color: white;
        font-weight: bold;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        font-size: 1.1rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("🤖 Plouf Scraper NextGen")

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Paramètres")
    max_fiches = st.slider("Max fiches par recherche", 5, 100, 20)
    browser_type = st.radio("Navigateur à utiliser", ["Firefox", "Chrome"], index=0)
    st.divider()
    if st.button("🧹 Effacer toutes les données"):
        for d in [RESULTATS_DIR_RAW, RESULTATS_DIR_ENRICHED]:
            if os.path.exists(d):
                import shutil
                shutil.rmtree(d)
        st.success("Toutes les données ont été effacées.")
        st.rerun()

# --- TABS ---
tab_launch, tab_results = st.tabs(["🚀 Lancer la Prospection", "📊 Voir les Résultats"])

# --- TAB 1: LAUNCH ---
with tab_launch:
    col1, col2 = st.columns(2)
    with col1:
        keyword = st.text_input("💎 Quel type d'entreprise ?", placeholder="Ex: Restaurant, Coworking, Plombier...")
    with col2:
        zipcode = st.text_input("📍 Dans quel secteur ?", placeholder="Ex: 69000, Lyon...")

    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        launch_scraping = st.button("🔍 Démarrer le Scraping Google Maps")
    
    with col_btn2:
        launch_enrich = st.button("✨ Enrichir les données existantes (Emails/Tél)")

    # LOGIC SCRAPING
    if launch_scraping:
        if not keyword or not zipcode:
            st.error("Veuillez renseigner un mot-clé ET un secteur.")
        else:
            query = f"{keyword} {zipcode} FR"
            pd.DataFrame({"mot_cle": [query]}).to_csv(MOTS_CLES_CSV, index=False)
            
            script = "scraper.py" if browser_type == "Firefox" else "scraper_chrome.py"
            st.info(f"Démarrage du scraping (**{browser_type}**) pour : **{query}**")
            
            pbar = st.progress(0)
            status = st.empty()
            log_container = st.empty()
            
            try:
                process = subprocess.Popen(
                    ["uv", "run", "python", "-u", script],
                    cwd=SCRAPPING_DIR,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
                
                full_logs = ""
                while True:
                    line = process.stdout.readline()
                    if not line and process.poll() is not None: break
                    if line:
                        full_logs += line
                        log_container.code("\n".join(full_logs.splitlines()[-15:]))
                        if "🌀 Scroll" in line: pbar.progress(30); status.text("Maps: défilement et collecte...")
                        elif "| ✅" in line: pbar.progress(60); status.text("Maps: extraction des fiches...")
                        elif "Enrichissement" in line: pbar.progress(90); status.text("Transition vers l'enrichissement...")

                process.wait()
                pbar.progress(100)
                if process.returncode == 0:
                    st.success("Scraping terminé !")
                    st.balloons()
                else:
                    st.error(f"Erreur script (Code {process.returncode})")
            except Exception as e:
                st.error(f"Frayeur technique : {e}")

    # LOGIC ENRICHMENT
    if launch_enrich:
        if not os.path.exists(FICHIER_RAW):
            st.warning("Aucune donnée brute à enrichir. Lancez d'abord un scraping.")
        else:
            script_enrich = "enrichisseur.py" if browser_type == "Firefox" else "enrichisseur_chrome.py"
            st.info("Lancement de l'enrichissement des données via les sites web...")
            pbar = st.progress(0)
            log_container = st.empty()
            
            try:
                process = subprocess.Popen(
                    ["uv", "run", "python", "-u", script_enrich],
                    cwd=SCRAPPING_DIR,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
                
                full_logs = ""
                while True:
                    line = process.stdout.readline()
                    if not line and process.poll() is not None: break
                    if line:
                        full_logs += line
                        log_container.code("\n".join(full_logs.splitlines()[-15:]))
                        pbar.progress(50) # Simple progress for enrich

                process.wait()
                pbar.progress(100)
                if process.returncode == 0:
                    st.success("Enrichissement terminé !")
                    st.rerun()
                else:
                    st.error("Erreur durant l'enrichissement.")
            except Exception as e:
                st.error(f"Erreur : {e}")

# --- TAB 2: RESULTS ---
with tab_results:
    st.subheader("📋 Récapitulatif des prospects trouvés")
    
    file_to_show = ""
    if os.path.exists(FICHIER_ENRICHI):
        file_to_show = FICHIER_ENRICHI
        st.write("✅ Données enrichies disponibles (avec Emails/Web)")
    elif os.path.exists(FICHIER_RAW):
        file_to_show = FICHIER_RAW
        st.write("⚠️ Uniquement des données brutes (pas encore enrichies)")
    
    if file_to_show:
        df = pd.read_csv(file_to_show)
        
        # Filtre rapide
        search = st.text_input("🔍 Rechercher dans les résultats", "")
        if search:
            df = df[df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)]
        
        # Affichage avec liens cliquables
        st.dataframe(
            df, 
            use_container_width=True, 
            height=500,
            column_config={
                "Site web": st.column_config.LinkColumn("Site Web", display_text="🌐 Visiter"),
                "Email trouvé": st.column_config.LinkColumn("Email", display_text="📧 Envoyer")
            }
        )
        
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Télécharger le CSV",
                csv,
                f"scraped_prospects_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv",
                use_container_width=True
            )
        with col_dl2:
            if st.button("🗑️ Vider cet historique", use_container_width=True):
                if os.path.exists(file_to_show): os.remove(file_to_show)
                st.rerun()
    else:
        st.info("Aucun résultat pour le moment. Allez dans l'onglet 'Lancement' !")
