import streamlit as st
import pandas as pd
import subprocess
import os
import sys
import time
from datetime import datetime

# Import du module de recherche de dirigeants
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import recherche_dirigeants

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
RESULTATS_DIR_DIRIGEANTS = os.path.join(SCRAPPING_DIR, "resultats_dirigeants")
FICHIER_RAW = os.path.join(RESULTATS_DIR_RAW, "resultats_complets.csv")
FICHIER_ENRICHI = os.path.join(RESULTATS_DIR_ENRICHED, "resultats_enrichis_complets.csv")
FICHIER_DIRIGEANTS = os.path.join(RESULTATS_DIR_DIRIGEANTS, "resultats_dirigeants.csv")

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
        for d in [RESULTATS_DIR_RAW, RESULTATS_DIR_ENRICHED, RESULTATS_DIR_DIRIGEANTS]:
            if os.path.exists(d):
                import shutil
                shutil.rmtree(d)
        st.success("Toutes les données ont été effacées.")
        st.rerun()

# --- TABS ---
tab_launch, tab_results, tab_dirigeants, tab_consolidated = st.tabs([
    "🚀 Lancer la Prospection", 
    "📊 Voir les Résultats",
    "👔 Rechercher les Dirigeants",
    "🎯 Vue Consolidée"
])

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

# --- TAB 3: DIRIGEANTS ---
with tab_dirigeants:
    st.subheader("👔 Recherche des Dirigeants et Contacts")
    st.markdown("Cette fonctionnalité utilise **4 APIs publiques** pour trouver les dirigeants de vos prospects.")
    
    # Vérifier si on a des données enrichies
    if not os.path.exists(FICHIER_ENRICHI):
        st.warning("⚠️ Aucune donnée enrichie trouvée. Veuillez d'abord :")
        st.markdown("1. Lancer un **scraping** dans l'onglet 'Lancer la Prospection'")
        st.markdown("2. **Enrichir** les données avec le bouton d'enrichissement")
        st.info("Les données enrichies sont nécessaires pour extraire les dirigeants.")
    else:
        # Afficher un aperçu des données sources
        df_source = pd.read_csv(FICHIER_ENRICHI)
        st.success(f"✅ {len(df_source)} entreprises prêtes à être analysées")
        
        with st.expander("📋 Aperçu des données sources"):
            st.dataframe(df_source.head(5), use_container_width=True)
        
        st.markdown("---")
        
        # Bouton de lancement
        col_btn, col_info = st.columns([1, 2])
        with col_btn:
            launch_dirigeants = st.button("🚀 Lancer la recherche des dirigeants", use_container_width=True)
        with col_info:
            st.info("🔍 Cascade de 4 APIs : Gouv → Pappers → Annuaire → Scraping")
        
        # Lancement de la recherche
        if launch_dirigeants:
            progress_bar = st.progress(0)
            status_text = st.empty()
            log_area = st.empty()
            
            logs = []
            
            def progress_callback(current, total, message):
                if total > 0:
                    progress_bar.progress(current / total)
                status_text.markdown(f"**{message}**")
                logs.append(f"[{current}/{total}] {message}")
                log_area.code("\n".join(logs[-10:]))  # Afficher les 10 derniers logs
            
            try:
                start_time = time.time()
                success = recherche_dirigeants.process_file(
                    FICHIER_ENRICHI, 
                    FICHIER_DIRIGEANTS, 
                    progress_callback=progress_callback
                )
                
                duration = round(time.time() - start_time, 2)
                
                if success:
                    st.balloons()
                    st.success(f"✅ Recherche terminée en {duration}s !")
                    st.rerun()
                else:
                    st.error("❌ Une erreur est survenue pendant le traitement.")
                    
            except Exception as e:
                st.error(f"Erreur critique : {e}")
        
        # Affichage des résultats si disponibles
        if os.path.exists(FICHIER_DIRIGEANTS):
            st.markdown("---")
            st.subheader("📊 Résultats de la recherche")
            
            df_dirigeants = pd.read_csv(FICHIER_DIRIGEANTS)
            
            # Statistiques
            col_stat1, col_stat2, col_stat3 = st.columns(3)
            with col_stat1:
                total = len(df_dirigeants)
                st.metric("Total entreprises", total)
            with col_stat2:
                trouves = len(df_dirigeants[df_dirigeants['Status Recherche'] == 'Trouvé'])
                st.metric("Dirigeants trouvés", trouves, f"{round(trouves/total*100)}%")
            with col_stat3:
                with_siret = len(df_dirigeants[df_dirigeants['SIRET'].notna() & (df_dirigeants['SIRET'] != '')])
                st.metric("Avec SIRET", with_siret)
            
            # Filtre de recherche
            search_dir = st.text_input("🔍 Rechercher dans les résultats", "", key="search_dirigeants")
            if search_dir:
                df_dirigeants = df_dirigeants[df_dirigeants.apply(
                    lambda row: row.astype(str).str.contains(search_dir, case=False).any(), axis=1
                )]
            
            # Affichage du tableau
            st.dataframe(
                df_dirigeants,
                use_container_width=True,
                height=500,
                column_config={
                    "Site web": st.column_config.LinkColumn(
                        "Site Web",
                        help="Site web de l'entreprise",
                        display_text="🌐 Visiter"
                    ),
                    "Lien Pappers": st.column_config.LinkColumn(
                        "Pappers",
                        help="Cliquer pour voir la fiche complète sur Pappers",
                        display_text="🔗 Voir"
                    ),
                    "SIRET": st.column_config.TextColumn("SIRET", help="Numéro SIRET de l'entreprise"),
                    "Dirigeants": st.column_config.TextColumn("Dirigeants", help="Noms et fonctions des dirigeants"),
                    "Source": st.column_config.TextColumn("Source", help="API ayant trouvé l'information")
                }
            )
            
            # Téléchargement
            col_dl1, col_dl2, col_dl3 = st.columns(3)
            with col_dl1:
                csv_dirigeants = df_dirigeants.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "📥 Télécharger CSV complet",
                    csv_dirigeants,
                    f"dirigeants_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    "text/csv",
                    use_container_width=True
                )
            with col_dl2:
                # Export uniquement les trouvés
                df_found = df_dirigeants[df_dirigeants['Status Recherche'] == 'Trouvé']
                csv_found = df_found.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "✅ Télécharger uniquement trouvés",
                    csv_found,
                    f"dirigeants_trouves_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    "text/csv",
                    use_container_width=True
                )
            with col_dl3:
                if st.button("🗑️ Supprimer ces résultats", use_container_width=True):
                    os.remove(FICHIER_DIRIGEANTS)
                    st.rerun()

# --- TAB 4: VUE CONSOLIDÉE ---
with tab_consolidated:
    st.subheader("🎯 Vue Consolidée : Prospects + Dirigeants")
    st.markdown("Cette vue affiche la **base de données consolidée** (historique complet).")
    
    FICHIER_CONSOLIDE = os.path.join(SCRAPPING_DIR, "resultats_consolides", "base_prospects_finale.csv")
    SCRIPT_CONSOLIDATION = os.path.join(SCRAPPING_DIR, "consolidation_prospects.py")

    col_action, col_status = st.columns([1, 2])
    with col_action:
        if st.button("🔄 Mettre à jour la consolidation"):
             with st.spinner("Consolidation en cours..."):
                try:
                    process = subprocess.run(
                        ["uv", "run", "python", SCRIPT_CONSOLIDATION],
                        cwd=SCRAPPING_DIR,
                        capture_output=True,
                        text=True
                    )
                    if process.returncode == 0:
                        st.success("Consolidation terminée !")
                        st.code(process.stdout)
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Erreur lors de la consolidation")
                        st.code(process.stderr)
                except Exception as e:
                    st.error(f"Erreur : {e}")

    # Vérifier si le fichier consolidé existe
    if not os.path.exists(FICHIER_CONSOLIDE):
        st.warning("⚠️ Aucune base consolidée trouvée. Veuillez lancer la consolidation.")
    else:
        try:
            df_consolide = pd.read_csv(FICHIER_CONSOLIDE)
            
            # Mapping des colonnes pour correspondre à l'affichage habituel
            # Base: Nom Entreprise,Activité,Dirigeant,Email,Téléphone,Téléphone Secondaire,Site Web,Adresse,Code Postal,Ville,SIRET,Date Création,Lien Pappers
            column_mapping = {
                "Nom Entreprise": "Nom",
                "Email": "Email trouvé",
                "Dirigeant": "Dirigeants",
                "Site Web": "Site web"
            }
            df_display = df_consolide.rename(columns=column_mapping)
            
            # Ajout colonnes manquantes pour éviter erreurs si absentes
            for col in ["SIRET", "Lien Pappers", "Téléphone"]:
                if col not in df_display.columns:
                    df_display[col] = ""

            st.success(f"✅ {len(df_display)} prospects dans la base historique")
            
            # Statistiques en haut
            col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
            with col_stat1:
                total = len(df_display)
                st.metric("Total Prospects", total)
            with col_stat2:
                with_email = len(df_display[df_display['Email trouvé'].notna() & (df_display['Email trouvé'] != '')])
                st.metric("Avec Email", with_email, f"{round(with_email/total*100) if total > 0 else 0}%")
            with col_stat3:
                # On considère qu'un dirigeant est 'trouvé' s'il y a du texte dans la colonne
                with_dirigeants = len(df_display[df_display['Dirigeants'].notna() & (df_display['Dirigeants'] != '') & (df_display['Dirigeants'] != 'Non listé')])
                st.metric("Avec Dirigeants", with_dirigeants, f"{round(with_dirigeants/total*100) if total > 0 else 0}%")
            with col_stat4:
                complete = len(df_display[
                    (df_display['Email trouvé'].notna() & (df_display['Email trouvé'] != '')) &
                    (df_display['Dirigeants'].notna() & (df_display['Dirigeants'] != ''))
                ])
                st.metric("Complets", complete, f"{round(complete/total*100) if total > 0 else 0}%")
            
            st.markdown("---")
            
            # Filtres
            col_filter1, col_filter2 = st.columns(2)
            with col_filter1:
                filter_option = st.selectbox(
                    "🔍 Filtrer par",
                    ["Tous", "Avec Email uniquement", "Avec Dirigeants uniquement", "Complets (Email + Dirigeants)", "Incomplets"],
                    key="filter_consolidated_base"
                )
            with col_filter2:
                search_consolidated = st.text_input("🔎 Rechercher", "", key="search_consolidated_base")
            
            # Application des filtres
            df_filtered = df_display.copy()
            
            if filter_option == "Avec Email uniquement":
                df_filtered = df_filtered[df_filtered['Email trouvé'].notna() & (df_filtered['Email trouvé'] != '')]
            elif filter_option == "Avec Dirigeants uniquement":
                df_filtered = df_filtered[df_filtered['Dirigeants'].notna() & (df_filtered['Dirigeants'] != '')]
            elif filter_option == "Complets (Email + Dirigeants)":
                df_filtered = df_filtered[
                    (df_filtered['Email trouvé'].notna() & (df_filtered['Email trouvé'] != '')) &
                    (df_filtered['Dirigeants'].notna() & (df_filtered['Dirigeants'] != ''))
                ]
            elif filter_option == "Incomplets":
                 df_filtered = df_filtered[
                    (df_filtered['Email trouvé'].isna() | (df_filtered['Email trouvé'] == '')) |
                    (df_filtered['Dirigeants'].isna() | (df_filtered['Dirigeants'] == ''))
                ]
            
            if search_consolidated:
                df_filtered = df_filtered[df_filtered.apply(
                    lambda row: row.astype(str).str.contains(search_consolidated, case=False).any(), axis=1
                )]
            
            st.info(f"📊 Affichage de **{len(df_filtered)}** prospects sur {total}")
            
            # Affichage du tableau consolidé
            st.dataframe(
                df_filtered,
                use_container_width=True,
                height=600,
                column_config={
                    "Site web": st.column_config.LinkColumn(
                        "Site Web",
                        display_text="🌐 Visiter"
                    ),
                    "Email trouvé": st.column_config.LinkColumn(
                        "Email",
                        display_text="📧 Envoyer"
                    ),
                    "Lien Pappers": st.column_config.LinkColumn(
                        "Pappers",
                        display_text="🔗 Voir"
                    ),
                    "Téléphone": st.column_config.TextColumn("Téléphone"),
                    "Dirigeants": st.column_config.TextColumn("Dirigeants"),
                    "SIRET": st.column_config.TextColumn("SIRET")
                }
            )
            
            # Export
            st.markdown("---")
            col_export1, col_export2 = st.columns(2)
            
            with col_export1:
                csv_all = df_filtered.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "📥 Télécharger la sélection",
                    csv_all,
                    f"prospects_base_finale_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    "text/csv",
                    use_container_width=True
                )
            
            with col_export2:
                # Créer un fichier optimisé pour la prospection
                cols_voulues = ['Nom', 'Téléphone', 'Email trouvé', 'Site web', 'Adresse', 'SIRET', 'Dirigeants', 'Lien Pappers', 'Activité', 'Ville']
                # Garder seulement celles qui existent
                cols_presentes = [c for c in cols_voulues if c in df_filtered.columns]
                
                df_prospect = df_filtered[cols_presentes].copy()
                csv_prospect = df_prospect.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "🎯 Export Prospection Optimisé",
                    csv_prospect,
                    f"export_prospection_final_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    "text/csv",
                    use_container_width=True
                )

        except Exception as e:
            st.error(f"Erreur de lecture du fichier consolidé : {e}")
