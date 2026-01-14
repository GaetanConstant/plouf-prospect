import streamlit as st
import os
import pandas as pd
from datetime import datetime
import random
import plotly.express as px
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

app_title = 'CRM Plouf 💧'
st.set_page_config(page_title=app_title, initial_sidebar_state='collapsed', page_icon="📞")

# === Chargement des données CSV locales ===
def load_data_scopa(local_file):
    data = pd.read_csv(local_file)
    return data

def create_crm_df():
    local_file = 'crm_scopa.csv'
    crm = load_data_scopa(local_file)

    # Ajouter colonne Commercial si absente
    if 'Commercial' not in crm.columns:
        crm['Commercial'] = None

    # Ajouter colonne Commentaire si absente
    if 'Commentaire' not in crm.columns:
        crm['Commentaire'] = ""

    return crm


MAIL_TEMPLATES = [
    "Bonjour {prenom} {nom},\n\nEn découvrant votre profil, je me suis dit que vous perdiez sûrement beaucoup de temps à gérer votre activité avec des fichiers Excel. Chez Plouf, on aide les équipes comme la vôtre à automatiser ces tâches chronophages. On échange à ce sujet ?",
    
    "Salut {prenom},\n\nJe suis tombé sur votre profil et je pense que Plouf pourrait vraiment vous simplifier la vie. Si vous en avez assez des tableaux Excel interminables, notre solution peut vraiment faire la différence. Partant pour un appel rapide ?",

    "Bonjour {prenom},\n\nJe me permets de vous contacter car j’ai pensé que Plouf pourrait vous faire gagner pas mal de temps. Notre outil permet d'automatiser une grande partie des tâches que beaucoup font encore sur Excel. Un moment pour en parler ?",

    "Bonjour {prenom} {nom},\n\nVous avez l’air d’avoir une activité bien structurée. Justement, Plouf peut vous aider à aller encore plus loin en réduisant la charge liée aux outils Excel classiques. Ça vous dit qu’on échange ?",

    "Bonjour {prenom},\n\nSi comme beaucoup, vous passez un temps fou à manipuler des fichiers Excel, Plouf peut vraiment vous aider. On propose une solution simple pour automatiser ça. Vous seriez dispo pour un rapide échange ?",

    "Bonjour {prenom} {nom},\n\nJe vous écris rapidement pour vous parler de Plouf, une solution qui permet de gagner un temps précieux en automatisant les tâches encore gérées sur Excel. Curieux(se) d’en savoir plus ?",

    "Salut {prenom},\n\nVous cherchez à gagner du temps et fiabiliser votre suivi ? C’est exactement ce que fait Plouf. Je pense que ça pourrait coller avec vos besoins. Un appel rapide pour en parler ?",

    "Bonjour {prenom},\n\nJe vois que vous êtes actif(ve) dans votre domaine et je me suis dit que Plouf pourrait vous être utile. Notre solution permet de dire adieu aux tableurs pour certaines tâches. Ça vous tente d’en discuter ?",

    "Bonjour {prenom},\n\nJe pense que vous pourriez être intéressé(e) par Plouf, notre outil d’automatisation qui remplace efficacement les Excel manuels. Ça vous dirait de découvrir comment ça fonctionne ?",

    "Bonjour {prenom} {nom},\n\nJe vous contacte car je pense que Plouf peut vraiment optimiser certaines tâches que vous gérez probablement sur Excel aujourd’hui. Est-ce qu’on peut s’appeler rapidement à ce sujet ?"
    
    "Bonjour {prenom} {nom},\n\nEn tant que professionnel(le), vous savez combien Excel peut vite devenir chronophage. Plouf permet de gagner un temps fou en automatisant tout ça. Partant(e) pour en parler ?",

    "Salut {prenom},\n\nVous en avez marre de vous battre avec des tableaux Excel ? Plouf automatise tout ça et simplifie la vie des équipes comme la vôtre. On échange ?",

    "Bonjour {prenom},\n\nJe me demandais si vous utilisiez encore Excel pour certaines tâches répétitives ? Si oui, Plouf pourrait vraiment vous faire gagner du temps. Un appel rapide pour vous montrer ?",

    "Bonjour {prenom} {nom},\n\nVous semblez bien organisé(e) dans votre activité. Plouf peut vous faire passer un cap en automatisant ce que vous faites peut-être encore sur Excel. Curieux(se) d’en savoir plus ?",

    "Salut {prenom},\n\nChez Plouf, on aide les pros à gagner du temps sur les tâches pénibles. Si Excel fait toujours partie de votre quotidien, on a peut-être une solution pour vous. On échange ?",

    "Bonjour {prenom},\n\nPlouf aide à automatiser les tâches qu’on fait encore à la main dans Excel. J’ai pensé que ça pouvait vous intéresser. On se parle ?",

    "Bonjour {prenom} {nom},\n\nVous utilisez Excel pour piloter certaines activités ? Plouf peut rendre tout ça plus fluide et automatique. Partant(e) pour un échange ?",

    "Salut {prenom},\n\nOn accompagne des équipes comme la vôtre pour passer d’Excel à une solution automatisée simple et efficace. Vous avez 15 minutes cette semaine pour en discuter ?",

    "Bonjour {prenom},\n\nSi vous cherchez à gagner du temps sur les tâches répétitives, Plouf pourrait bien être la solution. Je serais ravi(e) d’échanger si vous êtes curieux(se).",

    "Bonjour {prenom} {nom},\n\nVous êtes sûrement sollicité(e), alors je vais faire court : Plouf automatise ce que vous faites sur Excel, sans prise de tête. On en parle ?",

    "Salut {prenom},\n\nBeaucoup de nos clients ont commencé comme vous : Excel partout, du temps perdu. Aujourd’hui, ils utilisent Plouf. Ça vous tente d’essayer ?",

    "Bonjour {prenom},\n\nPlouf permet de transformer des process manuels (souvent sur Excel) en automatisations simples. Je pense que ça pourrait vous intéresser. Un moment pour en parler ?",

    "Bonjour {prenom} {nom},\n\nVous avez sans doute mieux à faire que de manipuler des tableaux. Plouf automatise ces tâches pour vous libérer du temps. Un rapide échange ?",

    "Salut {prenom},\n\nJe pense que Plouf peut vraiment vous faire gagner du temps sur les suivis Excel. Et si on prenait 10 minutes pour voir ça ensemble ?",

    "Bonjour {prenom},\n\nJe suis convaincu(e) que Plouf peut vous apporter de la valeur, surtout si Excel est encore très présent dans votre quotidien. Un échange rapide ?",

    "Bonjour {prenom} {nom},\n\nJe vous contacte car vous avez sûrement des process encore gérés sur Excel. Avec Plouf, on automatise tout ça simplement. Partant(e) pour en discuter ?",

    "Bonjour {prenom},\n\nSi vous cherchez à structurer vos activités autrement qu’avec des tableurs, je peux vous montrer comment Plouf aide nos clients. Ça vous tente ?",

    "Salut {prenom},\n\nJe pense que vous pourriez aimer Plouf : moins d’Excel, plus de temps pour le reste. On se cale un moment ?",

    "Bonjour {prenom},\n\nPlouf aide les pros à automatiser les tâches répétitives qu’ils font encore sur Excel. Je pense que ça peut vraiment vous servir. Vous avez un créneau ?",

    "Bonjour {prenom} {nom},\n\nVous semblez gérer pas mal de choses ! Plouf peut alléger votre charge en automatisant ce que vous faites encore sur Excel. Ça vous dit d’en discuter ?"
]




# === Authentification ===
config_file = 'config.yaml' if os.path.exists('config.yaml') else 'config_dev.yaml'
with open(config_file) as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

st.title("📞 Prospection commerciale Plouf")

try:
    authenticator.login()

    if st.session_state['authentication_status']:
        current_user = st.session_state['username']
        st.divider()
        st.write(f"Bienvenue *{st.session_state['name']}*")

        with st.spinner("Chargement des données..."):
            crm_df = create_crm_df()

        df = crm_df[(crm_df['Contacté'].isna()) & (crm_df['Commercial'].isna())].copy()

        if 'shuffled_indexes' not in st.session_state or 'current_index' not in st.session_state:
            st.session_state.shuffled_indexes = random.sample(list(df.index), len(df))
            st.session_state.current_index = 0

        #tab1, tab2, tab3 = st.tabs(["📋 Prospection", "📌 Suivi des contacts", "📊 Vue globale"])
        tabs = ["📋 Prospection", "📌 Suivi des contacts", "📊 Vue globale"]
        if current_user == "gconstant":
            tabs.append("🔐 Admin")
        
        tab1, tab2, tab3, *optional_tabs = st.tabs(tabs)
        tab_admin = optional_tabs[0] if optional_tabs else None

        st.divider()
        authenticator.logout()

        #st.info(f"Fiches restantes : {len(st.session_state.shuffled_indexes) - st.session_state.current_index}")
        with tab1:
            st.subheader("🎯 Filtrer les contacts")
        
            origines_disponibles = crm_df['origine_contact'].dropna().unique().tolist()
            origine_selectionnee = st.selectbox("Origine du contact :", options=origines_disponibles)
        
            # Filtrer les index des fiches valides dans crm_df (pas df)
            matching_indexes = crm_df[
                (crm_df['Contacté'].isna()) &
                (crm_df['Commercial'].isna()) &
                (crm_df['origine_contact'] == origine_selectionnee)
            ].index.tolist()
        
            # Si nouvelle origine sélectionnée → mélanger les index
            if ('last_selected_origine' not in st.session_state or
                st.session_state.last_selected_origine != origine_selectionnee):
                st.session_state.shuffled_indexes = random.sample(matching_indexes, len(matching_indexes))
                st.session_state.current_index = 0
                st.session_state.last_selected_origine = origine_selectionnee
        
            current_pos = st.session_state.current_index
        
            if current_pos < len(st.session_state.shuffled_indexes):
                idx = st.session_state.shuffled_indexes[current_pos]
                row = crm_df.loc[idx]
        
                st.subheader("Fiche à traiter")
                st.markdown(f"""
                ### 👤 {row['First Name']} {row['Last Name']} — *{row['Title']}*
                **🏢 Société :** {row['Company Name for Emails']}  
                **📧 Email :** {row['Email']}  
                **👥 Taille :** {row['# Employees']}  
                **🏫 Industrie :** {row['Industry']}  
                **🌐 Site Web :** [{row['Website']}]({row['Website']})  
                **🔗 LinkedIn :** [{row['Person Linkedin Url']}]({row['Person Linkedin Url']})  
                **📍 Adresse :** {row['Company Address']}  
                """, unsafe_allow_html=True)
        
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Contacté / Suivant"):
                        contact_date = datetime.now().strftime("oui le %d/%m/%Y")
                        crm_df.at[idx, 'Contacté'] = contact_date
                        crm_df.at[idx, 'Commercial'] = current_user
                        crm_df.to_csv("crm_scopa.csv", index=False)
                        st.session_state.current_index += 1
        
                with col2:
                    if st.button("⏭️ Passer cette fiche"):
                        contact_date = datetime.now().strftime("Passé le %d/%m/%Y")
                        crm_df.at[idx, 'Contacté'] = contact_date
                        crm_df.at[idx, 'Commercial'] = current_user
                        crm_df.to_csv("crm_scopa.csv", index=False)
                        st.session_state.current_index += 1
        
                if 'current_template' not in st.session_state:
                    st.session_state.current_template = random.choice(MAIL_TEMPLATES)
        
                if st.button("🔁 Générer un autre message"):
                    st.session_state.current_template = random.choice(MAIL_TEMPLATES)
        
                st.markdown("### ✉️ Exemple de message à envoyer")
                message = st.session_state.current_template.format(prenom=row['First Name'], nom=row['Last Name'])
                st.text_area("Modèle de message :", value=message, height=200)
        
            else:
                st.success("🎉 Toutes les fiches ont été traitées pour cette origine !")

        with tab2:
            st.subheader("📌 Suivi des personnes contactées")
            # --- Ajouter un prospect ---
            with st.expander("➕ Ajouter un prospect", expanded=False):
                with st.form(key="ajouter_prospect_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        prospect_prenom = st.text_input("Prénom")
                        prospect_nom = st.text_input("Nom")
                        prospect_titre = st.text_input("Titre")
                        prospect_industry = st.text_input("Industrie")
                        prospect_site = st.text_input("Site Web")
                    with col2:
                        prospect_societe = st.text_input("Société")
                        prospect_email = st.text_input("Email")
                        prospect_employees = st.text_input("Nombre d'employés")
                        prospect_linkedin = st.text_input("LinkedIn")
                        prospect_adresse = st.text_input("Adresse")
                    prospect_commentaire = st.text_area("Commentaire")
                    
                    submit_prospect = st.form_submit_button("Ajouter prospect")
                
                if submit_prospect:
                    # Création d'une nouvelle ligne avec les infos du prospect
                    new_row = {
                        "First Name": prospect_prenom,
                        "Last Name": prospect_nom,
                        "Title": prospect_titre,
                        "Company Name for Emails": prospect_societe,
                        "Email": prospect_email,
                        "# Employees": prospect_employees,
                        "Industry": prospect_industry,
                        "Website": prospect_site,
                        "Person Linkedin Url": prospect_linkedin,
                        "Company Address": prospect_adresse,
                        "Commentaire": prospect_commentaire,
                        "Contacté": f"Contacté le {datetime.now().strftime('%d/%m/%Y')}",
                        "Commercial": current_user  # l'utilisateur connecté
                    }
                    # Ajout de la nouvelle ligne dans le DataFrame
                    crm_df = pd.concat([crm_df, pd.DataFrame([new_row])], ignore_index=True)
                    # Sauvegarde dans le CSV
                    crm_df.to_csv("crm_scopa.csv", index=False)
                    st.success("Prospect ajouté avec succès !")
        
            #suivi_df = crm_df[crm_df['Contacté'].notna()].copy()
            suivi_df = crm_df[(crm_df['Contacté'].notna()) & (crm_df['Commercial'] == current_user)].copy()

        
            def extraire_statut(contacte):
                if isinstance(contacte, str):
                    if "le" in contacte:
                        return contacte.split(" le")[0]
                    else:
                        return contacte
                return "Contacté"
        
            suivi_df["Statut Simple"] = suivi_df["Contacté"].apply(extraire_statut)
        
            industries = ["Toutes"] + sorted(suivi_df['Industry'].dropna().unique())
            statuts = ["Tous"] + sorted(suivi_df["Statut Simple"].dropna().unique())
        
            col1, col2 = st.columns(2)
            selected_industry = col1.selectbox("🏭 Filtrer par industrie :", industries)
            selected_statut = col2.selectbox("📌 Filtrer par statut :", statuts)
        
            filtered_df = suivi_df.copy()
            if selected_industry != "Toutes":
                filtered_df = filtered_df[filtered_df['Industry'] == selected_industry]
            if selected_statut != "Tous":
                filtered_df = filtered_df[filtered_df["Statut Simple"] == selected_statut]
        
            # S'assurer que la colonne Commentaire existe
            if 'Commentaire' not in crm_df.columns:
                crm_df['Commentaire'] = ""
        
            def statut_badge(statut):
                if "Réponse" in statut:
                    return "🟡 Réponse"
                elif "RDV" in statut:
                    return "🟠 RDV pris"
                elif "Proposition" in statut:
                    return "🟣 Proposition"
                elif "Contact off" in statut:
                    return "🔴 Contact off"
                elif "oui" in statut:
                    return "🟢 Contacté"
                else:
                    return "🟢 Contacté"
        
            for idx, row in filtered_df.iterrows():
                badge = statut_badge(row["Contacté"])
                with st.expander(f"{badge} — {row['First Name']} {row['Last Name']} — {row['Company Name for Emails']}"):
                    key_prefix = f"{idx}_"
        
                    # Initialisation propre de l'état d'édition
                    if f"edit_{idx}" not in st.session_state:
                        st.session_state[f"edit_{idx}"] = False
        
                    # === MODE LECTURE ===
                    if not st.session_state[f"edit_{idx}"]:
                        st.markdown(f"""
                        ### 👤 {row['First Name']} {row['Last Name']} — *{row['Title']}*
                        **🏢 Société :** {row['Company Name for Emails']}  
                        **📧 Email :** {row['Email']}  
                        **👥 Taille :** {row['# Employees']}  
                        **🏭 Industrie :** {row['Industry']}  
                        **🌐 Site Web :** [{row['Website']}]({row['Website']})  
                        **🔗 LinkedIn :** [{row['Person Linkedin Url']}]({row['Person Linkedin Url']})  
                        **📍 Adresse :** {row['Company Address']}  
                        **🗒️ Commentaire :** {row.get('Commentaire', '')}  
                        **📅 Statut :** {row['Contacté']}  
                        """, unsafe_allow_html=True)
        
                        if st.button("✏️ Modifier la fiche", key=f"edit_btn_{idx}"):
                            st.session_state[f"edit_{idx}"] = True
        
                    # === MODE ÉDITION ===
                    else:
                        col1, col2 = st.columns(2)
                        with col1:
                            prenom = st.text_input("🧍‍♂️ Prénom", row['First Name'], key=key_prefix+"prenom")
                            nom = st.text_input("🧍‍♀️ Nom", row['Last Name'], key=key_prefix+"nom")
                            titre = st.text_input("💼 Titre", row['Title'], key=key_prefix+"titre")
                            societe = st.text_input("🏢 Société", row['Company Name for Emails'], key=key_prefix+"societe")
                            email = st.text_input("📧 Email", row['Email'], key=key_prefix+"email")
                        with col2:
                            taille = st.text_input("👥 Taille entreprise", str(row['# Employees']), key=key_prefix+"taille")
                            secteur = st.text_input("🏭 Industrie", row['Industry'], key=key_prefix+"secteur")
                            linkedin = st.text_input("🔗 LinkedIn", row['Person Linkedin Url'], key=key_prefix+"linkedin")
                            siteweb = st.text_input("🌐 Site Web", row['Website'], key=key_prefix+"siteweb")
                            adresse = st.text_area("📍 Adresse", row['Company Address'], key=key_prefix+"adresse")
        
                        commentaire = st.text_area("🗒️ Commentaire", row.get('Commentaire', ''), key=key_prefix+"commentaire")
        
                        statut_options = [
                            row['Contacté'] if pd.notna(row['Contacté']) else "Contacté",
                            f"Réponse le {datetime.now().strftime('%d/%m/%Y')}",
                            f"RDV pris le {datetime.now().strftime('%d/%m/%Y')}",
                            f"Proposition envoyée le {datetime.now().strftime('%d/%m/%Y')}",
                            f"Affaire conclue le {datetime.now().strftime('%d/%m/%Y')}",
                            "Contact off"
                        ]
                        selected_statut = st.selectbox("📝 Statut :", statut_options, index=0, key=key_prefix+"statut")
        
                        col_save, col_cancel = st.columns([1, 1])
                        if col_save.button("✅ Enregistrer", key=key_prefix+"save"):
                            crm_df.at[idx, 'First Name'] = prenom
                            crm_df.at[idx, 'Last Name'] = nom
                            crm_df.at[idx, 'Title'] = titre
                            crm_df.at[idx, 'Company Name for Emails'] = societe
                            crm_df.at[idx, 'Email'] = email
                            crm_df.at[idx, '# Employees'] = taille
                            crm_df.at[idx, 'Industry'] = secteur
                            crm_df.at[idx, 'Person Linkedin Url'] = linkedin
                            crm_df.at[idx, 'Website'] = siteweb
                            crm_df.at[idx, 'Company Address'] = adresse
                            crm_df.at[idx, 'Contacté'] = selected_statut
                            crm_df.at[idx, 'Commentaire'] = commentaire
        
                            crm_df.to_csv("crm_scopa.csv", index=False)
                            st.success("✅ Modifications enregistrées")
                            st.session_state[f"edit_{idx}"] = False
        
                        if col_cancel.button("❌ Annuler", key=key_prefix+"cancel"):
                            st.session_state[f"edit_{idx}"] = False

        with tab3:
            st.subheader("📊 Vue d’ensemble du CRM")
            df_stats = crm_df[(crm_df['Contacté'].notna()) & (crm_df['Commercial'] == current_user)].copy()

            def clean_statut(statut):
                if pd.isna(statut):
                    return "Non contacté"
                elif "Réponse" in statut:
                    return "Réponse"
                elif "RDV" in statut:
                    return "RDV pris"
                elif "Proposition" in statut:
                    return "Proposition"
                elif "Contact off" in statut:
                    return "Contact off"
                else:
                    return "Contacté"

            df_stats["Statut"] = df_stats["Contacté"].apply(clean_statut)
            count_statuts = df_stats["Statut"].value_counts().reset_index()
            count_statuts.columns = ["Statut", "Nombre"]

            fig = px.pie(count_statuts, names='Statut', values='Nombre', title='Répartition des statuts', hole=0.4)
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("👥 Personnes déjà contactées")
            st.dataframe(df_stats, use_container_width=True)

            




        if current_user == "gconstant" and tab_admin:
            with tab_admin:
                st.subheader("📊 Statistiques globales")
                st.info(f"Fiches restantes : {len(st.session_state.shuffled_indexes) - st.session_state.current_index}")
        
                # Répartition des statuts pour TOUS les commerciaux
                crm_df["Statut"] = crm_df["Contacté"].apply(clean_statut)
                count_all = crm_df[crm_df['Contacté'].notna()]["Statut"].value_counts().reset_index()
                count_all.columns = ["Statut", "Nombre"]
        
                fig_admin = px.pie(count_all, names='Statut', values='Nombre', title='Répartition globale des statuts', hole=0.4)
                st.plotly_chart(fig_admin, use_container_width=True)
        
                st.subheader("📋 Toutes les fiches contactées")
                all_contacts = crm_df[crm_df["Contacté"].notna()][["First Name", "Last Name", "Company Name for Emails", "Commercial", "Contacté"]]
                st.dataframe(all_contacts, use_container_width=True)

                st.subheader("🔍 Rechercher un contact dans la base complète")
                
                search_query = st.text_input("Tapez un mot-clé (nom, entreprise, email...) pour rechercher :", "")
                
                if search_query:
                    #mask = crm_df.apply(lambda row: row.astype(str).str.contains(search_query, case=False, na=False).any(), axis=1)
                    mask = crm_df.apply(
                        lambda row: any(search_query.lower() in str(value).lower() for value in row), axis=1
                    )

                    #search_results = crm_df[mask].sample(20)
                    search_results = crm_df[mask].sample(n=min(20, len(crm_df[mask])))

                    
                    st.write(f"Résultats pour **{search_query}** : {len(search_results)} ligne(s) trouvée(s)")
                    st.dataframe(search_results, use_container_width=True)
                    if not search_results.empty and st.button("✅ Marquer toutes ces fiches comme 'Contacté le ...'"):
                        contact_date = f"Contacté le {datetime.now().strftime('%d/%m/%Y')}"
                        for idx in search_results.index:
                            crm_df.at[idx, "Contacté"] = contact_date
                            if pd.isna(crm_df.at[idx, "Commercial"]) or crm_df.at[idx, "Commercial"] == "":
                                crm_df.at[idx, "Commercial"] = current_user  # optionnel, ou mettre "gconstant"
                        crm_df.to_csv("crm_scopa.csv", index=False)
                        st.success(f"Toutes les fiches affichées ({len(search_results)}) ont été marquées comme contactées.")

                    def statut_badge(statut):
                        statut_str = str(statut) if pd.notna(statut) else ""
                        if "Réponse" in statut_str:
                            return "🟡 Réponse"
                        elif "RDV" in statut_str:
                            return "🟠 RDV pris"
                        elif "Proposition" in statut_str:
                            return "🟣 Proposition"
                        elif "Contact off" in statut_str:
                            return "🔴 Contact off"
                        else:
                            return "🟢 Contacté"

                    
                    for idx, row in search_results.iterrows():
                        badge = statut_badge(row["Contacté"])
                        with st.expander(f"{badge} — {row['First Name']} {row['Last Name']} — {row['Company Name for Emails']}"):
                            key_prefix = f"admin_{idx}_"
                    
                            if f"edit_{key_prefix}" not in st.session_state:
                                st.session_state[f"edit_{key_prefix}"] = False
                    
                            if not st.session_state[f"edit_{key_prefix}"]:
                                st.markdown(f"""
                                ### 👤 {row['First Name']} {row['Last Name']} — *{row['Title']}*
                                **🏢 Société :** {row['Company Name for Emails']}  
                                **📧 Email :** {row['Email']}  
                                **👥 Taille :** {row['# Employees']}  
                                **🏭 Industrie :** {row['Industry']}  
                                **🌐 Site Web :** [{row['Website']}]({row['Website']})  
                                **🔗 LinkedIn :** [{row['Person Linkedin Url']}]({row['Person Linkedin Url']})  
                                **📍 Adresse :** {row['Company Address']}  
                                **👤 Commercial :** {row.get('Commercial', '')}  
                                **🗒️ Commentaire :** {row.get('Commentaire', '')}  
                                **📅 Statut :** {row['Contacté']}  
                                """, unsafe_allow_html=True)
                    
                                if st.button("✏️ Modifier la fiche", key=f"edit_btn_{key_prefix}"):
                                    st.session_state[f"edit_{key_prefix}"] = True
                    
                            else:
                                col1, col2 = st.columns(2)
                                with col1:
                                    prenom = st.text_input("🧍‍♂️ Prénom", row['First Name'], key=key_prefix+"prenom")
                                    nom = st.text_input("🧍‍♀️ Nom", row['Last Name'], key=key_prefix+"nom")
                                    titre = st.text_input("💼 Titre", row['Title'], key=key_prefix+"titre")
                                    societe = st.text_input("🏢 Société", row['Company Name for Emails'], key=key_prefix+"societe")
                                    email = st.text_input("📧 Email", row['Email'], key=key_prefix+"email")
                                    commercial = st.text_input("👤 Commercial", row.get('Commercial', ''), key=key_prefix+"commercial")
                                with col2:
                                    taille = st.text_input("👥 Taille entreprise", str(row['# Employees']), key=key_prefix+"taille")
                                    secteur = st.text_input("🏭 Industrie", row['Industry'], key=key_prefix+"secteur")
                                    linkedin = st.text_input("🔗 LinkedIn", row['Person Linkedin Url'], key=key_prefix+"linkedin")
                                    siteweb = st.text_input("🌐 Site Web", row['Website'], key=key_prefix+"siteweb")
                                    adresse = st.text_area("📍 Adresse", row['Company Address'], key=key_prefix+"adresse")
                    
                                commentaire = st.text_area("🗒️ Commentaire", row.get('Commentaire', ''), key=key_prefix+"commentaire")
                    
                                statut_options = [
                                    row['Contacté'] if pd.notna(row['Contacté']) else "Contacté",
                                    f"Réponse le {datetime.now().strftime('%d/%m/%Y')}",
                                    f"RDV pris le {datetime.now().strftime('%d/%m/%Y')}",
                                    f"Proposition envoyée le {datetime.now().strftime('%d/%m/%Y')}",
                                    "Contact off"
                                ]
                                selected_statut = st.selectbox("📝 Statut :", statut_options, index=0, key=key_prefix+"statut")
                    
                                col_save, col_cancel = st.columns([1, 1])
                                if col_save.button("✅ Enregistrer", key=key_prefix+"save"):
                                    crm_df.at[idx, 'First Name'] = prenom
                                    crm_df.at[idx, 'Last Name'] = nom
                                    crm_df.at[idx, 'Title'] = titre
                                    crm_df.at[idx, 'Company Name for Emails'] = societe
                                    crm_df.at[idx, 'Email'] = email
                                    crm_df.at[idx, '# Employees'] = taille
                                    crm_df.at[idx, 'Industry'] = secteur
                                    crm_df.at[idx, 'Person Linkedin Url'] = linkedin
                                    crm_df.at[idx, 'Website'] = siteweb
                                    crm_df.at[idx, 'Company Address'] = adresse
                                    crm_df.at[idx, 'Contacté'] = selected_statut
                                    crm_df.at[idx, 'Commentaire'] = commentaire
                                    crm_df.at[idx, 'Commercial'] = commercial
                    
                                    crm_df.to_csv("crm_scopa.csv", index=False)
                                    st.success("✅ Modifications enregistrées")
                                    st.session_state[f"edit_{key_prefix}"] = False
                    
                                if col_cancel.button("❌ Annuler", key=key_prefix+"cancel"):
                                    st.session_state[f"edit_{key_prefix}"] = False

                else:
                    st.info("Tapez un mot-clé pour lancer une recherche.")

        
                if st.button("♻️ Réinitialiser toutes les fiches (Admin)"):
                    crm_df['Contacté'] = None
                    crm_df['Commercial'] = None
                    crm_df.to_csv("crm_scopa.csv", index=False)
                    st.success("Base de données réinitialisée.")

    elif st.session_state['authentication_status'] is False:
        st.error("Erreur sur l'identifiant ou le mot de passe")
    elif st.session_state['authentication_status'] is None:
        st.warning('Merci de renseigner votre identifiant et mot de passe')

except Exception as e:
    st.error(e)