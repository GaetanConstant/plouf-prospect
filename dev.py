import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import random
from datetime import datetime, timedelta
import os
from urllib.parse import quote
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
import re

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Plouf CRM",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- AUTHENTICATION ---
with open('config_dev.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# Affichage du formulaire de connexion
# Note: authentication_status peut être True, False ou None
authenticator.login()

if st.session_state["authentication_status"] is False:
    st.error('Utilisateur/Mot de passe incorrect')
    st.stop()
elif st.session_state["authentication_status"] is None:
    st.warning('Veuillez entrer vos identifiants')
    st.stop()

# Si on arrive ici, l'utilisateur est authentifié
user_username = st.session_state['username']
user_role = config['credentials']['usernames'][user_username].get('role', 'usr')
st.session_state['role'] = user_role

st.sidebar.title(f"Bienvenue {st.session_state['name']}")
st.sidebar.info(f"Rôle : {user_role.capitalize()}")
authenticator.logout('Se déconnecter', 'sidebar')

# --- CUSTOM CSS (Aesthetics) ---
st.markdown("""
<style>
    /* Full Screen & Fixed Layout */
    html, body, [data-testid="stAppViewContainer"] {
        overflow: hidden !important;
        height: 100vh !important;
        width: 100vw !important;
    }

    .stApp {
        font-family: 'Inter', sans-serif;
        background-color: #0e1117;
    }

    /* Force Full Width */
    [data-testid="stAppViewContainer"] > section:nth-child(2) > div:nth-child(1) {
        max-width: none !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
    }

    /* Main content padding adjustment - Fill all width */
    .main .block-container {
        max-width: 100% !important;
        padding-top: 0.5rem !important;
        padding-bottom: 0rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        height: 100vh !important;
    }

    /* Hide top header to gain space */
    header[data-testid="stHeader"] {
        display: none !important;
    }

    /* Hide footer */
    footer {
        display: none !important;
    }
    
    /* Card Style - Adaptive Width */
    .prop-card {
        background-color: #1e2130;
        border-radius: 10px;
        padding: 15px;
        border: 1px solid #2e3b55;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease;
        width: 100%;
    }
    
    .prop-card h2 {
        font-size: 1.6rem !important;
        margin-bottom: 5px !important;
    }

    .prop-card p {
        margin-bottom: 4px !important;
        font-size: 1rem !important;
    }
    
    .prop-card:hover {
        transform: translateY(-2px);
        border-color: #ff4b4b;
    }

    /* Gradient Headers */
    h1 {
        font-size: 2.2rem !important;
        background: linear-gradient(90deg, #ff4b4b 0%, #9b1b30 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        margin-bottom: 0.2rem !important;
        padding-top: 0 !important;
    }

    h3 {
        font-size: 1.4rem !important;
        margin-bottom: 0.5rem !important;
    }

    /* Metrics */
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        color: #ff4b4b;
    }

    /* Buttons */
    .stButton>button {
        border-radius: 6px;
        font-weight: 600;
        padding: 0.4rem 1rem !important;
    }

    /* Tabs customization */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 20px !important;
        font-size: 1rem !important;
    }

    /* Spacing between streamlit elements */
    .stVerticalBlock {
        gap: 0.6rem !important;
    }
</style>
""", unsafe_allow_html=True)

# --- CONSTANTS ---
EMAIL_TEMPLATES = [
    """Bonjour,

Il est probable que vous rencontriez des difficultés avec :

-   La gestion complexe des données sur Excel qui génère des erreurs et perd du temps
-   Le pilotage de projets et d’équipes qui manque de visibilité
-   La multiplication des tâches administratives répétitives

Avec Plouf par SCOPA, dites adieu à ces contraintes ! Grâce à l’IA et à l’automatisation, vous centralisez vos données, optimisez vos processus et suivez vos projets en temps réel. Fini la gestion dispersée et place à l’efficacité !

Vous souhaitez en savoir plus sur comment l’IA de Plouf peut vous aider à améliorer vos performances ?

Bonne journée !""",
    
    """Bonjour,

Est-ce que vous êtes confronté à ces challenges ?

-   Des données dispersées sur Excel, ce qui vous fait perdre un temps précieux
-   Un pilotage de projets et d’équipes peu fluide
-   Des tâches administratives répétitives qui freinent votre productivité

Plouf par SCOPA simplifie tout grâce à l’IA. Centralisez vos informations, automatisez vos processus et suivez vos projets en temps réel, sans erreurs. En quelques clics, vous gagnez en productivité et en précision.

Découvrez comment l'IA de Plouf peut transformer vos processus métiers !

Bonne journée !""",
    
    """Bonjour,

Voici quelques défis que vous connaissez sûrement :

-   La gestion fastidieuse des données sur Excel
-   Des projets difficiles à piloter et des équipes difficiles à coordonner
-   Des tâches administratives répétitives qui impactent votre productivité

Avec Plouf par SCOPA, l’IA est au cœur de la solution pour centraliser vos données, automatiser vos tâches et suivre vos projets en temps réel. Vous n’avez plus à choisir entre efficacité et précision : vous les avez toutes les deux !

Si vous êtes prêt à booster votre productivité, discutons ensemble de ce que Plouf peut faire pour vous !

Bonne journée !""",

    """Bonjour,

Vous passez trop de temps à gérer des données Excel, à piloter vos projets et à faire des tâches administratives répétitives ? C’est un frein à votre productivité.

Plouf par SCOPA intègre l’IA pour centraliser, automatiser et suivre vos projets en temps réel. Plus d’erreurs, plus de pertes de temps !

Découvrez comment Plouf peut libérer votre potentiel en quelques clics.

Bonne journée !""",

    """Bonjour,

Vous faites face à des problèmes récurrents avec :

-   La gestion complexe de vos données et la perte de temps liée à Excel
-   Des projets difficiles à suivre efficacement
-   Des tâches administratives répétitives qui ralentissent vos équipes

Grâce à l’IA de Plouf par SCOPA, vous transformez ces obstacles en opportunités. Centralisation, automatisation, suivi en temps réel… Votre travail devient plus fluide, plus rapide et plus précis.

Êtes-vous prêt à découvrir comment l’IA peut révolutionner votre manière de travailler ?

Bonne journée !"""
]

# --- DATA MANAGEMENT ---
FILE_PATH = 'crm_scopa.csv'

def load_data():
    if os.path.exists(FILE_PATH):
        df = pd.read_csv(FILE_PATH)
        # S'assurer que les colonnes nécessaires existent
        for col in ['Contacté', 'Phone', 'Commercial']:
            if col not in df.columns:
                df[col] = None
        
        # Nettoyage robuste : on convertit les différentes formes de "vide" en None
        df['Contacté'] = df['Contacté'].astype(object).replace(['nan', 'None', '', 'nan'], None)
        df['Phone'] = df['Phone'].astype(object).replace(['nan', 'None', '', 'nan'], None)
        df['Commercial'] = df['Commercial'].astype(object).replace(['nan', 'None', '', 'nan'], None)
        
        # S'assurer que les valeurs nulles de pandas sont bien traitées
        df.loc[df['Contacté'].isnull(), 'Contacté'] = None
        df.loc[df['Phone'].isnull(), 'Phone'] = None
        df.loc[df['Commercial'].isnull(), 'Commercial'] = None
        
        return df
    else:
        st.error(f"Fichier {FILE_PATH} introuvable.")
        return pd.DataFrame()

def save_data(df):
    df.to_csv(FILE_PATH, index=False)

def extract_date(status_str):
    """Extracts date object from status strings like 'oui le 14/01/2026' or 'Contacté le ...'"""
    if not isinstance(status_str, str):
        return None
    try:
        # Search for date pattern DD/MM/YYYY
        import re
        match = re.search(r'\d{2}/\d{2}/\d{4}', status_str)
        if match:
            return datetime.strptime(match.group(), '%d/%m/%Y')
    except:
        pass
    return None

# --- APP LAYOUT ---
st.title("🌊 Plouf CRM")

# Load Data
if 'df' not in st.session_state:
    st.session_state.df = load_data()

df = st.session_state.df

if df.empty:
    st.stop()

# Tabs
tab_list = ["🚀 Session Prospection", "⏰ Relances Prioritaires", "🗂️ Historique"]
if st.session_state['role'] == 'admin':
    tab_list.insert(1, "📊 Analytics")

tabs = st.tabs(tab_list)

if st.session_state['role'] == 'admin':
    tab_prospect, tab_stats, tab_relance, tab_history = tabs
else:
    tab_prospect, tab_relance, tab_history = tabs
    tab_stats = None

# --- TAB 1: PROSPECTION ---
with tab_prospect:
    
    # 1. Filter by Origin (Group)
    if 'origine_contact' in df.columns:
        def normalize_origin(s):
            # Supprime le code postal (5 chiffres) et tout ce qui suit
            return re.sub(r'\s*\d{5}.*', '', str(s)).strip()

        # Récupération des origines brutes
        raw_origins = df['origine_contact'].dropna().unique().tolist()
        
        # Création du mapping Groupe -> Liste de valeurs brutes
        origin_groups = {}
        for r in raw_origins:
            g = normalize_origin(r)
            if g not in origin_groups:
                origin_groups[g] = []
            origin_groups[g].append(r)
            
        groups = sorted(origin_groups.keys())
        
        # Restriction rôle usr : pas de llbb
        if st.session_state['role'] != 'admin':
            groups = [g for g in groups if g.lower() != 'llbb']
            
        selected_origin = st.selectbox("🎯 Filtrer par Source (Groupe)", ["Tous"] + groups)
    else:
        selected_origin = "Tous"
        origin_groups = {}
        st.warning("Colonne 'origine_contact' introuvable.")

    st.markdown("### 👤 Nouvelle Cible")
    
    # Filter: Not contacted yet
    prospects = df[df['Contacté'].isna()].copy()
    
    # Restriction rôle usr : pas de llbb
    if st.session_state['role'] != 'admin':
        prospects = prospects[prospects['origine_contact'] != 'llbb']
    
    # Apply Origin Filter
    if selected_origin != "Tous":
        allowed_raw_values = origin_groups.get(selected_origin, [selected_origin])
        prospects = prospects[prospects['origine_contact'].isin(allowed_raw_values)]
    
    if prospects.empty:
        st.success(f"🎉 Incroyable ! Vous avez traité tous les prospects de la base (Filtre: {selected_origin}) !")
    else:
        # Session state to hold the current random prospect
        # Reset if the current index is no longer in the filtered list
        if 'current_prospect_idx' not in st.session_state or st.session_state.current_prospect_idx not in prospects.index:
            st.session_state.current_prospect_idx = random.choice(prospects.index)

        idx = st.session_state.current_prospect_idx
        row = df.loc[idx]

        # Display Card
        col_card, col_actions = st.columns([2, 1])
        
        with col_card:
            st.markdown(f"""
            <div class="prop-card">
                <h2>{row.get('First Name', '')} {row.get('Last Name', '')}</h2>
                <p style="font-size: 1.1em; color: #aaa;">{row.get('Title', 'Poste inconnu')} @ <strong>{row.get('Company Name for Emails', 'Unknown Company')}</strong></p>
                <div style="background-color: #262730; padding: 10px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #ff4b4b;">
                    <p style="margin:0; font-family: monospace; font-size: 1.2em;">📧 <strong>{row.get('Email') if pd.notna(row.get('Email')) else 'Email inconnu'}</strong></p>
                    <p style="margin:5px 0 0 0; font-family: monospace; font-size: 1.1em;">📞 <strong>{row.get('Phone') if pd.notna(row.get('Phone')) else 'N/A'}</strong></p>
                </div>
                <hr style="border-color: #333;">
                <p>🏭 <strong>Entreprise:</strong> {row.get('Industry', 'N/A')}</p>
                <p>👥 <strong>Taille:</strong> {row.get('# Employees', 'N/A')}</p>
                <p>📍 <strong>Lieu:</strong> {row.get('Company Address', 'N/A')}</p>
                <p>🏷️ <strong>Groupe:</strong> {row.get('origine_contact', 'N/A')}</p>
                <div style="margin-top: 20px;">
                    <a href="{row.get('Person Linkedin Url', '#')}" target="_blank" style="text-decoration: none; color: #ff4b4b; margin-right: 15px;">🔗 Profil LinkedIn</a>
                    <a href="{row.get('Website', '#')}" target="_blank" style="text-decoration: none; color: #ff4b4b; margin-right: 15px;">🌐 Site Web</a>
                    {f'<a href="tel:{row.get("Phone")}" style="text-decoration: none; color: #ff4b4b;">📞 Appeler</a>' if pd.notna(row.get('Phone')) else ''}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander("🛠️ Modifier les informations de la fiche"):
                new_first_name = st.text_input("Prénom", value=str(row.get('First Name', '')), key=f"fn_{idx}")
                new_last_name = st.text_input("Nom", value=str(row.get('Last Name', '')) if pd.notna(row.get('Last Name')) else '', key=f"ln_{idx}")
                new_email = st.text_input("Email", value=str(row.get('Email', '')) if pd.notna(row.get('Email')) else '', key=f"em_{idx}")
                new_phone = st.text_input("Téléphone", value=str(row.get('Phone', '')) if pd.notna(row.get('Phone')) else '', key=f"ph_{idx}")
                new_title = st.text_input("Poste", value=str(row.get('Title', '')) if pd.notna(row.get('Title')) else '', key=f"ti_{idx}")
                new_company = st.text_input("Entreprise", value=str(row.get('Company Name for Emails', '')), key=f"co_{idx}")
                new_industry = st.text_input("Industrie", value=str(row.get('Industry', '')), key=f"in_{idx}")
                new_employees = st.text_input("Taille (# Employees)", value=str(row.get('# Employees', '')), key=f"sz_{idx}")
                new_address = st.text_input("Lieu", value=str(row.get('Company Address', '')), key=f"ad_{idx}")
                new_linkedin = st.text_input("LinkedIn URL", value=str(row.get('Person Linkedin Url', '')), key=f"li_{idx}")
                new_website = st.text_input("Site Web", value=str(row.get('Website', '')), key=f"ws_{idx}")
                
                if st.button("💾 Enregistrer les modifications uniquement", use_container_width=True):
                    df.at[idx, 'First Name'] = new_first_name
                    df.at[idx, 'Last Name'] = new_last_name
                    df.at[idx, 'Email'] = new_email
                    df.at[idx, 'Phone'] = new_phone
                    df.at[idx, 'Title'] = new_title
                    df.at[idx, 'Company Name for Emails'] = new_company
                    df.at[idx, 'Industry'] = new_industry
                    df.at[idx, '# Employees'] = new_employees
                    df.at[idx, 'Company Address'] = new_address
                    df.at[idx, 'Person Linkedin Url'] = new_linkedin
                    df.at[idx, 'Website'] = new_website
                    # On ne change pas le commercial sur une simple modification
                    save_data(df)
                    st.session_state.df = df
                    st.success("Informations mises à jour !")
                    st.rerun()

        with col_actions:
            st.markdown("### Actions")
            
            # Use the possibly updated email for the mailto link
            dest_email = new_email if 'new_email' in locals() else row.get('Email', '')
            
            # --- EMAIL BUTTON ---
            email_subject = "Plouf par SCOPA"
            
            if 'current_email_body' not in st.session_state:
                st.session_state.current_email_body = random.choice(EMAIL_TEMPLATES)
            
            email_body = st.session_state.current_email_body
            
            if dest_email and '@' in str(dest_email):
                mailto_link = f"mailto:{dest_email}?subject={quote(email_subject)}&body={quote(email_body)}"
                st.link_button("📧 Ouvrir Email Prerempli", mailto_link, use_container_width=True)
            else:
                st.warning("Email manquant ou invalide")

            comment = st.text_area("Notes / Commentaire", key="comment_area")
            
            col_act1, col_act2 = st.columns(2)
            
            with col_act1:
                if st.button("✉️ Email Envoyé", use_container_width=True, type="primary"):
                    # Save changes too
                    df.at[idx, 'First Name'] = new_first_name
                    df.at[idx, 'Last Name'] = new_last_name
                    df.at[idx, 'Email'] = new_email
                    df.at[idx, 'Phone'] = new_phone
                    df.at[idx, 'Title'] = new_title
                    df.at[idx, 'Company Name for Emails'] = new_company
                    df.at[idx, 'Contacté'] = f"Contacté le {datetime.now().strftime('%d/%m/%Y')}"
                    df.at[idx, 'Commentaire'] = comment
                    df.at[idx, 'Commercial'] = st.session_state['username']
                    save_data(df)
                    st.session_state.df = df
                    if 'current_email_body' in st.session_state: del st.session_state.current_email_body
                    del st.session_state.current_prospect_idx
                    st.rerun()

            with col_act2:
                if st.button("🚫 Pas intéressé", use_container_width=True):
                    # Save changes too
                    df.at[idx, 'Email'] = new_email 
                    df.at[idx, 'Phone'] = new_phone
                    df.at[idx, 'Contacté'] = f"Contact off"
                    df.at[idx, 'Commentaire'] = comment
                    df.at[idx, 'Commercial'] = st.session_state['username']
                    save_data(df)
                    st.session_state.df = df
                    if 'current_email_body' in st.session_state: del st.session_state.current_email_body
                    del st.session_state.current_prospect_idx
                    st.rerun()

            if st.button("🎲 Passer (Suivant Aléatoire)", use_container_width=True):
                # Only pick from the filtered prospects
                if not prospects.empty:
                    if 'current_email_body' in st.session_state: del st.session_state.current_email_body
                    st.session_state.current_prospect_idx = random.choice(prospects.index)
                st.rerun()

# --- TAB 2: ANALYTICS ---
if tab_stats:
    with tab_stats:
        st.markdown("### 📈 Performance & Suivi")
    
    # Filter contacted
    contacted_df = df[df['Contacté'].notna() & (df['Contacté'] != "None")].copy()
    
    if contacted_df.empty:
        st.info("Aucune donnée de contact pour le moment.")
    else:
        # Extract basic status category
        def get_status_category(s):
            s = str(s).lower()
            if 'off' in s or 'pas intéressé' in s: return 'Stop'
            if 'réponse' in s: return 'Réponse'
            if 'rdv' in s: return 'RDV'
            if 'oui' in s or 'contacté' in s: return 'Contacté'
            return 'Autre'

        contacted_df['Status_Cat'] = contacted_df['Contacté'].apply(get_status_category)
        
        # Metrics Row
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Contactés", len(contacted_df))
        m2.metric("Réponses", len(contacted_df[contacted_df['Status_Cat'] == 'Réponse']))
        m3.metric("RDV Pris", len(contacted_df[contacted_df['Status_Cat'] == 'RDV']))
        ratio = (len(contacted_df[contacted_df['Status_Cat'].isin(['Réponse', 'RDV'])]) / len(contacted_df) * 100)
        m4.metric("Taux de Retour", f"{ratio:.1f}%")
        
        st.divider()
        
        # Charts
        c1, c2 = st.columns(2)
        
        with c1:
            # Pie Chart
            fig_pie = px.pie(
                contacted_df, 
                names='Status_Cat', 
                title='Répartition des Status',
                color_discrete_sequence=px.colors.sequential.Reds_r,
                hole=0.4
            )
            fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white")
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with c2:
            # Bar Chart by Industry
            top_inds = contacted_df['Industry'].value_counts().head(8).reset_index()
            top_inds.columns = ['Industry', 'Count']
            
            fig_bar = px.bar(
                top_inds, 
                x='Count', 
                y='Industry', 
                orientation='h', 
                title='Top Industries Contactées',
                color='Count',
                color_continuous_scale='Reds'
            )
            fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white", yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig_bar, use_container_width=True)

# --- TAB 3: RELANCES ---
with tab_relance:
    st.markdown("### ⏳ Top 10 Relances (Les plus anciens)")
    
    # Logic: Filter "Contacté" ones (that are not closed/off), extract date, sort ascending (oldest first)
    # We assume "Contacté" category means waiting for reply.
    
    search_df = df[df['Contacté'].notna() & (df['Contacté'] != "None")].copy()
    
    # Filtrage par commercial et origine si pas admin
    if st.session_state['role'] != 'admin':
        search_df = search_df[search_df['Commercial'] == st.session_state['username']]
        search_df = search_df[search_df['origine_contact'] != 'llbb']
    
    # Filter only those that need follow up (e.g., status contains 'Contacté' or 'oui' but NOT 'off', 'RDV', 'Réponse')
    # Use a simpler filter for now: just exclude explicit "Stop" signals if you want, 
    # but user said 'aleatoire parmis les plus vieux', so let's take those with dates.
    
    search_df['DateObj'] = search_df['Contacté'].apply(extract_date)
    
    # Filter valid dates
    valid_dates_df = search_df.dropna(subset=['DateObj']).sort_values(by='DateObj')
    
    # Filter out those who replied or said NO (assuming we just want to follow up on silence)
    # Adjust this logic based on your real needs. For now, we take anything that has a date.
    # Refinement: exclude "Contact off"
    valid_dates_df = valid_dates_df[~valid_dates_df['Contacté'].str.contains('off', case=False, na=False)]
    
    if valid_dates_df.empty:
        st.info("Aucun contact éligible à la relance trouvé (pas de dates détectées).")
    else:
        # User wants "les 10 plus vieux aléatoires". 
        # Strategy: Take the oldest 50, then pick 10 random from them.
        pool_size = min(50, len(valid_dates_df))
        oldest_pool = valid_dates_df.head(pool_size)
        
        # Sample 10
        sample_size = min(10, pool_size)
        # Using a deterministic seed based on date could be nice, but user said random.
        # We want the selection to stay stable during the session? 
        # Let's just sample randomly.
        relance_list = oldest_pool.sample(n=sample_size)
        
        for i, (idx, row) in enumerate(relance_list.iterrows()):
            days_ago = (datetime.now() - row['DateObj']).days
            
            with st.expander(f"🔴 Relance #{i+1} : {row['First Name']} {row['Last Name']} (Contacté il y a {days_ago} jours)"):
                c_a, c_b = st.columns([3, 1])
                with c_a:
                    st.markdown(f"""
                    **Société:** {row.get('Company Name for Emails')}  
                    **Email:** {row.get('Email')}  
                    **Dernier Statut:** {row['Contacté']}  
                    **Note:** {row.get('Commentaire', '')}
                    """)
                with c_b:
                    if st.button("✅ Relancé !", key=f"relance_{idx}"):
                        new_note = f"{row.get('Commentaire', '')} | Relancé le {datetime.now().strftime('%d/%m/%Y')}"
                        df.at[idx, 'Commentaire'] = new_note
                        # Update status? Maybe keep it simple or change to "Relancé le..."
                        df.at[idx, 'Contacté'] = f"Relancé le {datetime.now().strftime('%d/%m/%Y')}"
                        df.at[idx, 'Commercial'] = st.session_state['username']
                        save_data(df)
                        st.session_state.df = df
                        st.success("Statut mis à jour !")
                        st.rerun()

# --- TAB 4: HISTORIQUE ---
with tab_history:
    st.markdown("### 🗂️ Tous les contacts traités")
    
    # Reuse contacted_df from Stats tab logic (or re-filter)
    history_df = df[df['Contacté'].notna() & (df['Contacté'] != "None")].copy()
    
    # Filtrage par commercial et origine si pas admin
    if st.session_state['role'] != 'admin':
        history_df = history_df[history_df['Commercial'] == st.session_state['username']]
        history_df = history_df[history_df['origine_contact'] != 'llbb']
    
    if history_df.empty:
        st.info("Aucun historique disponible.")
    else:
        # Search Box
        search_term = st.text_input("🔍 Rechercher (Nom, Entreprise, Email...)", "")
        
        if search_term:
            # Simple case-insensitive search
            mask = history_df.apply(lambda x: x.astype(str).str.contains(search_term, case=False).any(), axis=1)
            display_df = history_df[mask]
        else:
            display_df = history_df
            
        # Display Dataframe
        st.dataframe(
            display_df[[
                'First Name', 'Last Name', 'Company Name for Emails', 'Email', 'Phone',
                'Contacté', 'Commentaire', 'Industry', 'origine_contact', 'Commercial',
                'Person Linkedin Url', 'Website'
            ]], 
            use_container_width=True,
            height=600,
            column_config={
                "Person Linkedin Url": st.column_config.LinkColumn("LinkedIn", display_text="🔗 Profil"),
                "Website": st.column_config.LinkColumn("Site Web", display_text="🌐 Visiter")
            }
        )
        
        st.caption(f"Total: {len(display_df)} contacts trouvés.")

