import streamlit as st
import pandas as pd
import requests
import time

# --- P A G E   C O N F I G U R A T I O N ---
st.set_page_config(
    page_title="Plouf Prospect",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- C U S T O M   C S S   (Premium React-like Aesthetic) ---
st.markdown("""
    <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;600;700&display=swap');

        /* Global Variables */
        :root {
            --primary-red: #FF4B4B;
            --primary-red-hover: #EE3F3F;
            --bg-dark: #0A0F1C;
            --card-bg: #161C2C;
            --sidebar-bg: #111827;
            --border-color: #2D3748;
            --text-main: #F7FAFC;
            --text-muted: #A0AEC0;
        }

        /* General Styles */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            color: var(--text-main);
        }
        
        .stApp {
            background-color: var(--bg-dark);
        }

        /* Typography */
        h1, h2, h3 {
            font-family: 'Outfit', sans-serif;
            color: var(--text-main);
            font-weight: 700;
        }
        h1 {
            font-size: 3.5rem !important;
            background: linear-gradient(135deg, #FF4B4B 0%, #FF8F8F 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -0.02em;
            margin-bottom: 1rem !important;
        }

        /* Sidebar Customization */
        section[data-testid="stSidebar"] {
            background-color: var(--sidebar-bg);
            border-right: 1px solid var(--border-color);
        }
        section[data-testid="stSidebar"] div.stVerticalBlock {
            padding-top: 2rem;
        }

        /* Card and Container Styling */
        div.stMetric {
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            padding: 1.5rem !important;
            border-radius: 16px;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        }
        div.stMetric:hover {
            transform: translateY(-4px);
            border-color: var(--primary-red);
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.2);
        }

        /* Inputs and Selectboxes */
        .stTextInput input, .stSelectbox select, .stMultiSelect {
            background-color: #1F2937 !important;
            color: white !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 12px !important;
            padding: 0.5rem 1rem !important;
        }
        .stTextInput input:focus {
            border-color: var(--primary-red) !important;
            box-shadow: 0 0 0 2px rgba(255, 75, 75, 0.2) !important;
        }

        /* Buttons (The Red Focus) */
        .stButton button {
            background: linear-gradient(135deg, #FF4B4B 0%, #D32F2F 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 12px !important;
            font-weight: 600 !important;
            padding: 0.75rem 1.5rem !important;
            width: 100% !important;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
            text-transform: none !important;
            font-family: 'Outfit', sans-serif !important;
        }
        .stButton button:hover {
            background: linear-gradient(135deg, #FF5E5E 0%, #E53935 100%) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 10px 20px rgba(255, 75, 75, 0.3) !important;
            color: white !important;
        }
        .stButton button:active {
            transform: translateY(0px) !important;
        }

        /* Dataframe / Table Styling */
        [data-testid="stDataFrame"] {
            border: 1px solid var(--border-color);
            border-radius: 16px;
            overflow: hidden;
            background-color: var(--card-bg);
        }

        /* Custom Scrollbar */
        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }
        ::-webkit-scrollbar-track {
            background: var(--bg-dark);
        }
        ::-webkit-scrollbar-thumb {
            background: #374151;
            border-radius: 10px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #4B5563;
        }

        /* Expander Styling */
        .streamlit-expanderHeader {
            background-color: var(--card-bg) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 12px !important;
            color: var(--text-main) !important;
        }

        /* Status Messages */
        .stAlert {
            border-radius: 12px !important;
            border: none !important;
            background-color: rgba(31, 41, 55, 0.8) !important;
            backdrop-filter: blur(10px);
        }

        /* Hide Streamlit components */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

    </style>
""", unsafe_allow_html=True)


# --- F U N C T I O N S ---
@st.cache_data(ttl=600)  # Cache data for 10 minutes
def fetch_data():
    """Fetches data from the API."""
    url = "http://plouf.scopa.co:8000/results"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return pd.DataFrame(data)
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Erreur lors de la récupération des données : {e}")
        return pd.DataFrame() # Return empty DF

def filter_dataframe(df, search_text, sector_filter, city_filter):
    """Filters the dataframe based on user input."""
    filtered_df = df.copy()

    # Search Text (Global)
    if search_text:
        # Create a mask for all columns
        mask = filtered_df.astype(str).apply(
            lambda x: x.str.contains(search_text, case=False, na=False)
        ).any(axis=1)
        filtered_df = filtered_df[mask]

    # Sector Filter (Activité)
    if sector_filter and "Activité" in filtered_df.columns:
         if sector_filter != "Tous":
            filtered_df = filtered_df[filtered_df["Activité"] == sector_filter]

    # City Filter (Ville)
    if city_filter and "Ville" in filtered_df.columns:
        if city_filter != "Toutes":
             filtered_df = filtered_df[filtered_df["Ville"].astype(str).str.contains(city_filter, case=False, na=False)]
    
    return filtered_df

# --- M A I N   A P P ---

def main():
    # Helper to clean up columns if needed
    
    # 1. Header Section
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("# 🌊 Plouf Résultats")
        st.markdown("Explorez et filtrez les données de prospection en temps réel.")
    with col2:
        if st.button("🔄 Rafraîchir les données"):
            st.cache_data.clear()
            st.rerun()

    st.markdown("---")

    # 2. Data Loading
    with st.spinner("Chargement des données..."):
        df = fetch_data()

    if df.empty:
        st.warning("Aucune donnée disponible pour le moment.")
        return

    # Pre-processing to ensure links are usable strings
    if "Site Web" in df.columns:
        df["Site Web"] = df["Site Web"].fillna("")
    if "Lien Pappers" in df.columns:
        df["Lien Pappers"] = df["Lien Pappers"].fillna("")

    # 3. Sidebar Filters
    with st.sidebar:
        st.header("🎯 Filtres")
        st.markdown("Affinez votre recherche.")

        # Search Bar
        search_query = st.text_input("🔍 Recherche globale", placeholder="Nom, email, mot-clé...")
        
        st.markdown("### Critères spécifiques")
        
        # Sector Filter
        activities = ["Tous"] + sorted(df["Activité"].dropna().unique().tolist()) if "Activité" in df.columns else ["Tous"]
        selected_activity = st.selectbox("Activité", activities)

        # City Filter (Simplifying to filter by unique values or simple text search if too many)
        # Often "Ville" contains multiple cities (e.g. "Paris, Lyon"). We might want a robust extract, but for now simple select with unique full strings
        # OR better: extract unique cities if the string is comma separated.
        # Let's keep it simple: Use unique values from the column for now.
        cities = ["Toutes"] + sorted(df["Ville"].dropna().unique().tolist()) if "Ville" in df.columns else ["Toutes"]
        selected_city = st.selectbox("Ville", cities)
        
        st.markdown("---")
        st.markdown(f"**Total résultats:** {len(df)}")
        st.markdown("v1.0.0 | Plouf Prospect")

    # 4. Filtering Logic
    filtered_data = filter_dataframe(df, search_query, selected_activity, selected_city)

    # 5. KPI / Metrics Row
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric(label="Entreprises trouvées", value=len(filtered_data))
    with m2:
        # Calculate distinct emails if valid
        if "Email" in filtered_data.columns:
             valid_emails = filtered_data[filtered_data["Email"].str.contains("@", na=False)]
             st.metric(label="Emails disponibles", value=len(valid_emails))
        else:
            st.metric(label="Emails disponibles", value=0)
    with m3:
         if "Téléphone" in filtered_data.columns:
             valid_phones = filtered_data[filtered_data["Téléphone"].str.len() > 5]  # simple check
             st.metric(label="Téléphones disponibles", value=len(valid_phones))
         else:
             st.metric(label="Téléphones disponibles", value=0)

    # 6. Main Data Display
    st.subheader("📋 Liste des Résultats")

    # Column Configuration for LinkColumn
    column_config = {
        "Site Web": st.column_config.LinkColumn(
            "Site Web",
            display_text="Visiter le site",
            help="Cliquer pour ouvrir le site web"
        ),
        "Lien Pappers": st.column_config.LinkColumn(
            "Pappers",
            display_text="Voir sur Pappers",
            help="Consulter la fiche juridique"
        ),
        "Email": st.column_config.TextColumn(
            "Email",
            help="Email de contact",
            validate="^\\S+@\\S+\\.\\S+$"
        ),
        "SIRET": st.column_config.NumberColumn(
            "SIRET",
            format="%f" # Avoid comma formatting for ID-like numbers if possible, though string is safer for SIRET. 
                        # However, raw data had float SIRETs. Let's try to convert to string if possible before display.
        )
    }

    # Better SIRET formatting for display
    if "SIRET" in filtered_data.columns:
        # Convert to string, remove '.0' if present
        filtered_data["SIRET"] = filtered_data["SIRET"].apply(lambda x: str(int(x)) if pd.notnull(x) and x != "" else "")

    st.dataframe(
        filtered_data,
        use_container_width=True,
        column_config=column_config,
        hide_index=True,
        height=600
    )

if __name__ == "__main__":
    main()
