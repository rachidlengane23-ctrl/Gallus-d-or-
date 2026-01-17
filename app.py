import streamlit as st
import pandas as pd
import json
import os
from datetime import date, timedelta

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Sasso Manager", layout="wide", page_icon="🐔")

# --- GESTION DE LA SAUVEGARDE (MÉMOIRE DU TÉLÉPHONE) ---
FICHIER_DONNEES = "donnees_elevage.json"

def charger_donnees():
    # Si le fichier existe, on le charge
    if os.path.exists(FICHIER_DONNEES):
        with open(FICHIER_DONNEES, "r") as f:
            return json.load(f)
    # Sinon, on crée les données par défaut
    else:
        return {
            "date_lancement": str(date.today()),
            "effectif_depart": 500,
            "mortalite_totale": 0,
            "stock_aliment": 0.0,
            "stock_medicament": {},
            "depenses_diverses": 0.0,
            "historique": []
        }

def sauvegarder_donnees(data):
    with open(FICHIER_DONNEES, "w") as f:
        json.dump(data, f)

# Initialisation des variables
if 'data' not in st.session_state:
    st.session_state.data = charger_donnees()

# Fonction raccourci pour sauvegarder
def save():
    sauvegarder_donnees(st.session_state.data)

# Calcul de l'âge
date_debut = date.fromisoformat(st.session_state.data['date_lancement'])
age_jours = (date.today() - date_debut).days + 1

# --- BARRE LATÉRALE (MENU) ---
st.sidebar.title("👤 Rachid Élevage")
menu = st.sidebar.radio("Menu", ["🏠 Tableau de Bord", "💉 Programme Sanitaire", "📦 Stocks & Aliment", "📝 Suivi Journalier", "💰 Rentabilité"])

st.sidebar.markdown("---")
with st.sidebar.expander("⚙️ Réglages Bande"):
    new_date = st.date_input("Date d'arrivée", date_debut)
    new_eff = st.number_input("Nombre de poussins", value=st.session_state.data['effectif_depart'])
    if st.button("Mettre à jour paramètres"):
        st.session_state.data['date_lancement'] = str(new_date)
        st.session_state.data['effectif_depart'] = new_eff
        save()
        st.rerun()

# --- PAGE 1 : TABLEAU DE BORD ---
if menu == "🏠 Tableau de Bord":
    st.title("📊 Vue d'ensemble")
    
    vivants = st.session_state.data['effectif_depart'] - st.session_state.data['mortalite_totale']
    pourcentage_survie = (vivants / st.session_state.data['effectif_depart']) * 100
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Âge Sasso", f"{age_jours} Jours", "Cycle 45 jours")
    col2.metric("Effectif Vivant", f"{vivants} têtes", f"Morts: {st.session_state.data['mortalite_totale']}")
    col3.metric("Stock Aliment", f"{st.session_state.data['stock_aliment']} kg", "Disponibles")
    
    st.write("### Progression du cycle")
    progression = min(age_jours / 45, 1.0)
    st.progress(progression)
    if age_jours >= 45:
        st.success("🎉 Le cycle est terminé ! Les poulets sont prêts à la vente.")

# --- PAGE 2 : PROGRAMME SANITAIRE ---
elif menu == "💉 Programme Sanitaire":
    st.title("💉 Planning Vaccinal Sasso 45J")
    st.info(f"Âge actuel : **{age_jours} jours**")
    
    # Liste des traitements
    programme = [
        {"Jour": "1-3", "Type": "💊 Traitement", "Nom": "Anti-stress + Démarrage", "Produit": "Vitamines + Antibio"},
        {"Jour": "7", "Type": "💉 VACCIN", "Nom": "Newcastle + Bronchite", "Produit": "HB1 + H120 (Goutte œil)"},
        {"Jour": "10-12", "Type": "💊 Traitement", "Nom": "Anticoccidien", "Produit": "Amprolium/Sulfamide"},
        {"Jour": "14", "Type": "💉 VACCIN", "Nom": "Gumboro", "Produit": "Intermédiaire (Eau)"},
        {"Jour": "19-21", "Type": "💊 Traitement", "Nom": "Vitamines", "Produit": "Renforcement Osseux"},
        {"Jour": "21", "Type": "💉 VACCIN", "Nom": "Newcastle (Rappel)", "Produit": "La Sota (Eau)"},
        {"Jour": "24-26", "Type": "💊 Traitement", "Nom": "Anticoccidien (Rappel)", "Produit": "Rotatif"},
        {"Jour": "35", "Type": "💊 Traitement", "Nom": "Déparasitage", "Produit": "Vermifuge"},
    ]
    
    df_sanitaire = pd.DataFrame(programme)
    
    def colorier_ligne(row):
        # Analyse les jours (ex: "1-3" ou "7")
        j_str = row['Jour'].split('-')
        debut = int(j_str[0])
        fin = int(j_str[1]) if len(j_str) > 1 else int(j_str[0])
        
        if debut <= age_jours <= fin:
            return ['background-color: #ff4b4b; color: white; font-weight: bold'] * len(row) # Rouge = A faire
        elif age_jours > fin:
            return ['background-color: #d4edda; color: green'] * len(row) # Vert = Fait
        return [''] * len(row) # Blanc = A venir

    st.table(df_sanitaire.style.apply(colorier_ligne, axis=1))

# --- PAGE 3 : STOCKS ---
elif menu == "📦 Stocks & Aliment":
    st.title("📦 Gestion des Stocks")
    
    tab1, tab2 = st.tabs(["Aliment", "Pharmacie"])
    
    with tab1:
        st.metric("Stock Aliment Actuel", f"{st.session_state.data['stock_aliment']} kg")
        
        with st.form("ajout_stock"):
            ajout = st.number_input("Ajouter des sacs (kg)", min_value=0.0, step=50.0)
            if st.form_submit_button("➕ Ajouter au stock"):
                st.session_state.data['stock_aliment'] += ajout
                save()
                st.success("Stock mis à jour !")
                st.rerun()

    with tab2:
        st.write("Médicaments en stock :")
        st.write(st.session_state.data['stock_medicament'])
        
        c1, c2, c3 = st.columns(3)
        nom = c1.text_input("Nom Produit")
        qte = c2.number_input("Quantité", step=1)
        action = c3.radio("Action", ["Ajouter", "Utiliser"])
        
        if st.button("Valider Pharmacie"):
            if nom:
                current = st.session_state.data['stock_medicament'].get(nom, 0)
                if action == "Ajouter":
                    st.session_state.data['stock_medicament'][nom] = current + qte
                else:
                    st.session_state.data['stock_medicament'][nom] = max(0, current - qte)
                save()
                st.rerun()

# --- PAGE 4 : SUIVI JOURNALIER ---
elif menu == "📝 Suivi Journalier":
    st.title("📝 Saisie Quotidienne")
    
    with st.form("journalier"):
        st.write(f"Date du jour : {date.today()}")
        morts = st.number_input("Nombre de décès aujourd'hui", min_value=0)
        conso = st.number_input("Aliment consommé (kg)", min_value=0.0)
        depense = st.number_input("Autres dépenses (CFA)", min_value=0.0)
        
        if st.form_submit_button("Enregistrer la journée"):
            st.session_state.data['mortalite_totale'] += morts
            st.session_state.data['stock_aliment'] -= conso
            st.session_state.data['depenses_diverses'] += depense
            
            # Historique (Optionnel)
            log = f"{date.today()}: -{morts} poulets, -{conso}kg alim."
            st.session_state.data['historique'].append(log)
            
            save()
            st.success("Données enregistrées avec succès !")
            st.rerun()

# --- PAGE 5 : RENTABILITÉ ---
elif menu == "💰 Rentabilité":
    st.title("💰 Bilan Financier")
    
    with st.expander("Paramètres des prix", expanded=True):
        c1, c2 = st.columns(2)
        p_poussin = c1.number_input("Prix Poussin (CFA)", value=500)
        p_sac = c2.number_input("Prix Sac 50kg (CFA)", value=17500)
        p_vente = c1.number_input("Prix Vente Poulet (CFA)", value=3000)
    
    nb_depart = st.session_state.data['effectif_depart']
    nb_vivants = nb_depart - st.session_state.data['mortalite_totale']
    
    # Dépenses
    cout_poussins = nb_depart * p_poussin
    cout_aliment_estime = (nb_vivants * 4.5 * (p_sac/50)) # Est. 4.5kg par tête
    cout_divers = st.session_state.data['depenses_diverses']
    total_depenses = cout_poussins + cout_aliment_estime + cout_divers
    
    # Recettes
    recettes = nb_vivants * p_vente
    marge = recettes - total_depenses
    
    st.write("---")
    k1, k2, k3 = st.columns(3)
    k1.error(f"Dépenses (Est.)\n{int(total_depenses):,} CFA")
    k2.info(f"Recettes Potentielles\n{int(recettes):,} CFA")
    
    if marge > 0:
        k3.success(f"Marge Bénéficiaire\n{int(marge):,} CFA")
        st.balloons()
    else:
        k3.error(f"Perte prévisionnelle\n{int(marge):,} CFA")
