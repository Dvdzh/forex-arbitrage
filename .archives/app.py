import streamlit as st
import pandas as pd
import numpy as np
import requests
import networkx as nx
import matplotlib.pyplot as plt
from datetime import datetime
import dataloader

# Configuration 
access_token = "24c6631769cafdcd3d79ce1d9cb3738d-e9b57872e0b4597ca1d7d2b28426431a"
account_id = "101-002-30836297-001"

# Configuration dataloader 
loader = dataloader.DataLoader(access_token, account_id)
list_currency, instruments = loader.info_instrument()
df = loader.get_instrument_price_df()
fig = loader.visualize_currency_graph(df, show=False)
cleaned_df = loader.clean_df(df)
fig_clean = loader.visualize_currency_graph(cleaned_df, show=False)

# Set page configuration
st.set_page_config(page_title="Forex Arbitrage Detector", layout="wide")

# Initialiser l'état de la session
if 'sidebar_visible' not in st.session_state:
    st.session_state.sidebar_visible = False

# App header
st.title("Forex Arbitrage Opportunity Detector")
st.markdown("""
This application helps identify arbitrage opportunities in the forex market by analyzing exchange rates between multiple currencies.
""")

# Rajouter side bar 
st.sidebar.title("Configuration")
st.sidebar.write("### Paramètres")
with st.sidebar.expander("Informations sur les devises", expanded=True):
    st.write("### Informations sur les devises")
    st.write("Liste des devises disponibles: ", list_currency)
    st.write("Nombre de paires de devises disponibles: ", len(instruments))
api_option = st.sidebar.selectbox("API", ["OANDA API", "Demo (Random Data)"])
# list_currency = st.sidebar.multiselect("Select Currencies", list_currency, default=list_currency[:3])
# selected_currencies = st.sidebar.multiselect("Select Currencies", loader.list_currency, default=loader.list_currency[:3])

st.divider()
st.write("### Acquisition des données")

st.caption("Tableau des prix des paires de devises, données brutes")
st.dataframe(df)

col1, col2 = st.columns(2)
with col1:
    st.caption("Graphique des prix des paires de devises")
    st.plotly_chart(fig)    
with col2:
    st.caption("Tableau des prix des paires de devises après nettoyage")
    st.plotly_chart(fig_clean)

st.divider()
# Utilisation de différents solveurs


st.write("### Formulation du problème d'optimisation")
st.latex(r'''
\begin{align*}
\text{Minimize} \quad & \sum_{i=1}^{n} \sum_{j=1}^{n} c_{ij} x_{ij} \\
\text{Subject to} \quad & \sum_{j=1}^{n} x_{ij} = 1, \quad i = 1, \ldots, n \\
& \sum_{i=1}^{n} x_{ij} = 1, \quad j = 1, \ldots, n \\
& x_{ij} \in \{0, 1\}, \quad i, j = 1, \ldots, n
\end{align*}
''')

st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.write("### Utilisation du solveur de Gurobi")
    st.write("Le solveur de Gurobi est un solveur d'optimisation linéaire et mixte entier.")
    # st button lancer optimisation
    st.button("Lancer l'optimisation de Gurobi")
with col2:
    st.write("### Utilisation du solveur de CPLEX")
    st.write("Le solveur de CPLEX est un solveur d'optimisation linéaire et mixte entier.")
    # st button lancer optimisation
    st.button("Lancer l'optimisation de CPLEX")
with col3:
    st.write("### Utilisation du solveur de Dwave")
    st.write("Le solveur de Dwave est un solveur quantique.")
    # st button lancer optimisation
    st.button("Lancer l'optimisation de Dwave")
