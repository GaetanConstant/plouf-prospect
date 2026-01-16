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

    st.markdown("---")
    st.subheader("📁 Ou importer un fichier CSV (Batch)")
    uploaded_file = st.file_uploader("Upload d'un CSV (Colonnes 'Sociétés' et 'Codes')", type=["csv"])
    
    if uploaded_file is not None:
        try:
            # Lire tout en string pour garder les zéros des codes postaux (ex: 01000)
            df_upload = pd.read_csv(uploaded_file, sep=None, engine='python', dtype=str)
            st.write("Aperçu du fichier :")
            st.dataframe(df_upload.head())
            
            # Normalisation des noms de colonnes (enlever espaces, minuscules)
            df_upload.columns = [c.strip() for c in df_upload.columns]
            
            col_soc = next((c for c in df_upload.columns if 'sociét' in c.lower()), None)
            col_code = next((c for c in df_upload.columns if 'code' in c.lower()), None)
            
            if col_soc and col_code:
                st.success(f"Colonnes détectées : '{col_soc}' et '{col_code}'")
                
                # Nettoyage et complétion des codes postaux (Garder 5 chiffres)
                df_upload[col_code] = df_upload[col_code].astype(str).str.strip().str.zfill(5)
                df_upload[col_soc] = df_upload[col_soc].astype(str).str.strip()
                
                queries = (df_upload[col_soc] + " " + df_upload[col_code] + " FR").tolist()
                st.info(f"{len(queries)} mots-clés prêts à être traités.")
            else:
                st.error("Colonnes 'Sociétés' et 'Codes' non trouvées. Vérifiez l'en-tête de votre CSV.")
                queries = None
        except Exception as e:
            st.error(f"Erreur de lecture : {e}")
            queries = None
    else:
        queries = None

    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        text_btn = "🔍 Démarrer le Scraping"
        if queries:
            text_btn = f"🔍 Scraper les {len(queries)} sociétés du CSV"
        launch_scraping = st.button(text_btn)
    
    with col_btn2:
        launch_enrich = st.button("✨ Enrichir les données existantes (Emails/Tél)")

    # LOGIC SCRAPING
    if launch_scraping:
        if not queries and (not keyword or not zipcode):
            st.error("Veuillez renseigner un mot-clé ET un secteur, ou uploader un CSV valide.")
        else:
            if not queries:
                query = f"{keyword} {zipcode} FR"
                pd.DataFrame({"mot_cle": [query]}).to_csv(MOTS_CLES_CSV, index=False)
                st.info(f"Démarrage du scraping (**{browser_type}**) pour : **{query}**")
            else:
                pd.DataFrame({"mot_cle": queries}).to_csv(MOTS_CLES_CSV, index=False)
                st.info(f"Démarrage du scraping (**{browser_type}**) pour **{len(queries)}** recherches...")
            
            script = "scraper.py" if browser_type == "Firefox" else "scraper_chrome.py"
            pbar = st.progress(0)
            status = st.empty()
            log_container = st.empty()
            
            try:
                process = subprocess.Popen(
                    ["uv", "run", "python", "-u", script, str(max_fiches)],
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
                        
                        if "🔍 Traitement du mot-clé" in line:
                            try:
                                # Extraire "1/14" et le mot-clé
                                parts = line.split(":")
                                current_info = parts[0].split(" ")[3] # "1/14"
                                current_keyword = parts[1].strip()
                                status.markdown(f"🚀 Recherche **{current_info}** : **{current_keyword}**")
                                # Calculer un progrès approximatif
                                current_idx, total_idx = map(int, current_info.split("/"))
                                pbar.progress(current_idx / total_idx)
                            except:
                                pass
                        elif "🌀 Scroll" in line: status.text("Maps: défilement et collecte...")
                        elif "| ✅" in line: status.text("Maps: extraction d'une fiche...")
                        elif "Enrichissement" in line: pbar.progress(95); status.text("Lancement de l'enrichissement...")

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

    # --- DEBUG SECTION ---
    with st.expander("🛠️ Diagnostics (Si 0 résultats)"):
        debug_dir = os.path.join(RESULTATS_DIR_RAW, "debug")
        if os.path.exists(debug_dir):
            screenshots = sorted([f for f in os.listdir(debug_dir) if f.endswith(".png")], reverse=True)
            if screenshots:
                st.warning(f"Dernière capture d'écran de débug ({screenshots[0]}) :")
                st.image(os.path.join(debug_dir, screenshots[0]))
                if st.button("🗑️ Effacer les captures de débug"):
                    import shutil
                    shutil.rmtree(debug_dir)
                    os.makedirs(debug_dir)
                    st.rerun()
            else:
                st.write("Aucun fichier de débug trouvé.")
        else:
            st.write("Le dossier de débug n'a pas encore été créé.")
