import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import random
from datetime import datetime, timedelta
import os
from urllib.parse import quote

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Plouf CRM NextGen",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CUSTOM CSS (Aesthetics) ---
st.markdown("""
<style>
    /* Global Clean Look */
    .stApp {
        font-family: 'Inter', sans-serif;
        background-color: #0e1117;
    }
    
    /* Card Style */
    .prop-card {
        background-color: #1e2130;
        border-radius: 12px;
        padding: 24px;
        border: 1px solid #2e3b55;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease;
    }
    
    .prop-card:hover {
        transform: translateY(-2px);
        border-color: #4f8bf9;
    }

    /* Gradient Headers */
    h1, h2, h3 {
        background: linear-gradient(90deg, #4f8bf9 0%, #a259ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
    }

    /* Metrics */
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        color: #4f8bf9;
    }

    /* Buttons */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s;
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
        # Ensure 'Contacté' column is treated as object/string
        if 'Contacté' not in df.columns:
            df['Contacté'] = None
        else:
            df['Contacté'] = df['Contacté'].astype(str).replace('nan', None)
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
st.title("🌊 Plouf CRM • NextGen")

# Load Data
if 'df' not in st.session_state:
    st.session_state.df = load_data()

df = st.session_state.df

if df.empty:
    st.stop()

# Tabs
tab_prospect, tab_stats, tab_relance, tab_history = st.tabs(["🚀 Session Prospection", "📊 Analytics", "⏰ Relances Prioritaires", "🗂️ Historique"])

# --- TAB 1: PROSPECTION ---
with tab_prospect:
    
    # 1. Filter by Origin (Group)
    if 'origine_contact' in df.columns:
        origins = sorted(df['origine_contact'].dropna().astype(str).unique().tolist())
        selected_origin = st.selectbox("🎯 Filtrer par Source (Groupe)", ["Tous"] + origins)
    else:
        selected_origin = "Tous"
        st.warning("Colonne 'origine_contact' introuvable.")

    st.markdown("### 👤 Nouvelle Cible")
    
    # Filter: Not contacted yet
    prospects = df[df['Contacté'].isna() | (df['Contacté'] == "None")].copy()
    
    # Apply Origin Filter
    if selected_origin != "Tous":
        prospects = prospects[prospects['origine_contact'] == selected_origin]
    
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
                <div style="background-color: #262730; padding: 10px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #4f8bf9;">
                    <p style="margin:0; font-family: monospace; font-size: 1.2em;">📧 <strong>{row.get('Email', 'Email inconnu')}</strong></p>
                </div>
                <hr style="border-color: #333;">
                <p>🏭 <strong>Industrie:</strong> {row.get('Industry', 'N/A')}</p>
                <p>👥 <strong>Taille:</strong> {row.get('# Employees', 'N/A')}</p>
                <p>📍 <strong>Lieu:</strong> {row.get('Company Address', 'N/A')}</p>
                <p>🏷️ <strong>Groupe:</strong> {row.get('origine_contact', 'N/A')}</p>
                <div style="margin-top: 20px;">
                    <a href="{row.get('Person Linkedin Url', '#')}" target="_blank" style="text-decoration: none; color: #4f8bf9; margin-right: 15px;">🔗 Profil LinkedIn</a>
                    <a href="{row.get('Website', '#')}" target="_blank" style="text-decoration: none; color: #4f8bf9;">🌐 Site Web</a>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_actions:
            st.markdown("### Actions")
            
            # --- EMAIL BUTTON ---
            email_subject = "Plouf par SCOPA"
            
            # Pick a random template if not already set for this prospect
            if 'current_email_body' not in st.session_state:
                st.session_state.current_email_body = random.choice(EMAIL_TEMPLATES)
            
            email_body = st.session_state.current_email_body
            dest_email = row.get('Email', '')
            
            if dest_email and '@' in str(dest_email):
                mailto_link = f"mailto:{dest_email}?subject={quote(email_subject)}&body={quote(email_body)}"
                st.link_button("📧 Ouvrir Email Prerempli", mailto_link, use_container_width=True)
            else:
                st.warning("Email manquant ou invalide")

            comment = st.text_area("Notes / Commentaire", key="comment_area")
            
            col_act1, col_act2 = st.columns(2)
            
            with col_act1:
                if st.button("✉️ Email Envoyé", use_container_width=True, type="primary"):
                    df.at[idx, 'Contacté'] = f"Contacté le {datetime.now().strftime('%d/%m/%Y')}"
                    df.at[idx, 'Commentaire'] = comment
                    save_data(df)
                    st.session_state.df = df
                    if 'current_email_body' in st.session_state: del st.session_state.current_email_body
                    del st.session_state.current_prospect_idx
                    st.rerun()

            with col_act2:
                if st.button("🚫 Pas intéressé", use_container_width=True):
                    df.at[idx, 'Contacté'] = f"Contact off"
                    df.at[idx, 'Commentaire'] = comment
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
                color_discrete_sequence=px.colors.sequential.RdBu,
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
                color_continuous_scale='Viridis'
            )
            fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white", yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig_bar, use_container_width=True)

# --- TAB 3: RELANCES ---
with tab_relance:
    st.markdown("### ⏳ Top 10 Relances (Les plus anciens)")
    
    # Logic: Filter "Contacté" ones (that are not closed/off), extract date, sort ascending (oldest first)
    # We assume "Contacté" category means waiting for reply.
    
    search_df = df[df['Contacté'].notna() & (df['Contacté'] != "None")].copy()
    
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
                        save_data(df)
                        st.session_state.df = df
                        st.success("Statut mis à jour !")
                        st.rerun()

# --- TAB 4: HISTORIQUE ---
with tab_history:
    st.markdown("### 🗂️ Tous les contacts traités")
    
    # Reuse contacted_df from Stats tab logic (or re-filter)
    history_df = df[df['Contacté'].notna() & (df['Contacté'] != "None")].copy()
    
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
                'First Name', 'Last Name', 'Company Name for Emails', 'Email', 
                'Contacté', 'Commentaire', 'Industry', 'origine_contact'
            ]], 
            use_container_width=True,
            height=600
        )
        
        st.caption(f"Total: {len(display_df)} contacts trouvés.")

