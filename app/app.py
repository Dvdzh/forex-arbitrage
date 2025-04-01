import sys
import os
import streamlit as st 
from st_link_analysis import st_link_analysis, NodeStyle, EdgeStyle
import pandas as pd 
import json 

# Style node & edge groups
NODE_STYLE = [
    NodeStyle("CURRENCY", "#FF7F3E", "name"),
]

EDGE_STYLE = [
    EdgeStyle("PAIR_DIRECT", directed=True, color="#83B256", caption="rate"),
    EdgeStyle("PAIR_INVERSE", directed=True, color="#B29D56", caption="rate"),
]

# st.metric(label="Temp", value="273 K", delta="1.2 K")

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

### ------------------- Read data ------------------- ###
# Lecture des données
prices_df = pd.read_csv("data/dataloader/prices_temporal.csv", index_col=0, header=0)
q_df = pd.read_csv("data/problem/Q_2025-03-28 00:00:00+00:00.csv", index_col=0, header=0)
with open("data/dataloader/list_currency.json", "r") as f:
    list_currency = json.load(f)

# Set page configuration
st.set_page_config(page_title="Forex Arbitrage Detector", layout="wide")

# ### ------------------- Sidebar ------------------- ###
# with st.sidebar:
#     st.title("Configuration")
#     st.write("### Paramètres")
#     list_currency = st.multiselect("Select Currencies", list_currency, default=list_currency)
#     period = st.selectbox("Select Period", ["1d", "1wk", "1mo"])
#     interval = st.selectbox("Select Interval", ["1m", "5m", "15m", "30m", "1h", "1d"])
#     solver = st.selectbox("Select Solver", ["Simulated Bifurcation", "Quantum Annealing", "Gurobi Solver", "D-Wave Solver"])

### ------------------- Header ------------------- ###
with st.sidebar:
    st.title("Forex QUBO Solver")
    st.divider()
    st.subheader('Présentation')
    st.info("Projet IND8123 Fintech, 2025")
    st.info("Acquisition de données, modélisation et résolution de problèmes d'arbitrage sur le marché des changes en utilsant différents solveurs disponibles.")

    st.divider()
    st.subheader('Calcul de la complexité')
    st.write("Le problème d'arbitrage sur le marché des changes est un problème NP-complet, ce qui signifie que le temps de calcul augmente exponentiellement avec le nombre de devises.")
    d = st.number_input("Nombre de devise", 0, 10, 2)
    st.write(f"Nombre de pairs de devise : {d*(d-1)}")
    st.write(f"Nombre de possibilités de combinaison : {2**(d*(d-1)):,}")
    st.write()
### ------------------- Dataloader ------------------- ###
# st.divider()
st.write("### Acquisition des données")
# st.write("On fait l'acquisition des données de prix des devises sur le marché des changes à partir de Yahoo Finance.")
with st.expander("Configurations utilisé pour l'acquisition des données"):
    with open("data/dataloader/config.json", "r") as f:
        config = json.load(f)
    st.write(config)


date_list = prices_df.index
# with st.sidebar:
#     st.divider()
#     st.subheader("Paramètres")
#     date_selection = st.selectbox('Choix de la date pour la formulation', date_list, index=len(date_list)-1)

col1, col2 = st.columns(2)
with col1:
    event = st.dataframe(prices_df, on_select="rerun", selection_mode="single-row")
    if event['selection']['rows'] == []:
        date_selection = prices_df.index[-1]
    else:
        date_selection = prices_df.index[event['selection']['rows'][0]]
    # print(date_selection)
    st.caption('Remarque : Les données sont disponibles toutes les 6 minutes, on peut expliquer ces trous parce qu\'on exclu les données manquantes.')
    st.caption('Remarque : Cliquer sur la colonne à gauche pour changer la date.')
# Render the component
with col2:
    with open(f"data/figure/graph_{date_selection}.json", "r") as f:
        elements = json.load(f)
    st_link_analysis(elements, "cose", NODE_STYLE, EDGE_STYLE)
### ------------------- Problem formulation ------------------- ###

st.divider()
st.write("### Formulation du problème")
# menu déroulant 

st.write("Le problème d'arbitrage sur le marché des changes peut être formulé comme un problème d'optimisation Quadratic Unconstrained Binary Optimisation (QUBO).")
with st.expander("Voir explications"):
    st.write("La formulation QUBO est donnée par la fonction objective et les contraintes suivantes :")
    st.write("1. **Variables binaires** ")
    st.write("   - Chaque paire de devise est représentée par une variable binaire")
    st.write("   - Si la variable est égale à 1, la paire de devise est sélectionnée pour l'arbitrage")
    st.write("   - Si la variable est égale à 0, la paire de devise n'est pas sélectionnée pour l'arbitrage")
    st.latex(r'''
            \textbf{b} \in \{0,1\} ^{D(D-1)}
                ''')
    st.write("2. **Fonction objective** ")
    st.write("   - Minimiser le coût d'arbitrage, utilisation de la fonction log pour minimiser le produit des taux de change")
    st.latex(r'''
            \argmin_{\textbf{b} \in \{0,1\} ^{D(D-1)}} - \textbf{b}^T \log(\textbf{R}) \textbf{b}
                ''')
    st.write("3. **Contraintes** ")
    st.caption("   Pour chaque paire de devise, on définit la source et la destination tel que la source est la devise de départ et la destination est la devise d'arrivée")
    st.write("   - On pénalise les solutions ayant sélectionné le plus de paires de devises")
    st.latex(r'''
            \argmin_{\textbf{b} \in \{0,1\} ^{D(D-1)}} m \times \textbf{b}^T I_{D(D-1)} \textbf{b}
            ''')
    st.write("   - Pour une paire de devise choisie, on pénalise les paires de devises ayant la même source et favorise les paires de devises dont la destination est la source")
    st.latex(r'''
            \argmin_{\textbf{b} \in \{0,1\} ^{D(D-1)}} m_1 \times \textbf{b}^T \textbf{M}_1\textbf{b} 
            ''')
    st.write("   - Pour une paire de devise choisie, on pénalise les paires de devises ayant la même destination et favorise les paires de devises dont la destination est la destination")

    st.latex(r'''
            \argmin_{\textbf{b} \in \{0,1\} ^{D(D-1)}} m_2 \times \textbf{b}^T \textbf{M}_2 \textbf{b} 
            ''')
    
    
st.write("**Formulation finale**")
st.latex(r'''
        \argmin_{\textbf{b} \in \{0,1\} ^{D(D-1)}}
            \textbf{b}^T 
            (
            \log(\textbf{R}) 
            + m \times I_{D(D-1)}
            + m_1 \times \textbf{M}_1
            + m_2 \times \textbf{M}_2
            )
            \textbf{b} 
        ''')
    # st.markdown("b : vecteur de variables binaires")
    # st.markdown("m : vecteur de poids des devises")
    # st.markdown("Q : matrice de coût")
    # st.markdown("x : vecteur de variables binaires")
    # st.markdown("QUBO : Quadratic Unconstrained Binary Optimization")
    # st.markdown("D : nombre de devises")
    # st.markdown("R : matrice des taux de change, diagonale")
    # st.markdown("M1 : matrice de contrainte des sources, stochastique et symétrique")
    # st.markdown("M2 : matrice de contrainte des cibles, stochastique et symétrique")

col1, col2, col3 = st.columns(3)
with col1:
    constraint_diag = st.slider("Constrainte diagonale", min_value=0., max_value=10., step=0.1, value=5.)
with col2:
    constraint_M1 = st.slider("Contrainte M1", min_value=0., max_value=1., step=0.1)
with col3:
    constraint_M2 = st.slider("Contrainte M2", min_value=0., max_value=1., step=0.1)

import src.problem as problem
qubo = problem.QUBOProblem()
qubo.get_Q(prices_df.loc[date_selection], constraint_M1=constraint_M1, constraint_M2=constraint_M2, constraint_diag=constraint_diag)
st.dataframe(qubo.Q)

# import plotly.graph_objects as go

# fig = go.Figure()

# fig.add_trace(
#     go.Heatmap(
#         z=qubo.Q.values,
#         x=qubo.Q.columns,
#         y=qubo.Q.index,
#         colorscale="Viridis",
#         text=qubo.Q.values,
#         hovertemplate="<b>%{x}</b> <br> %{y} <br> Coefficient: %{z:.2f}<extra></extra>",
#     )
# )

# fig.update_layout(
#     height=600,
# )

# st.plotly_chart(fig)
# st.markdown("Exemple de formulation matricielle")
# st.dataframe(q_df)
### ------------------- Display Solution ------------------- ###

st.divider()
st.write("### Solution")

tab1, tab2, tab3 = st.tabs(["Simulated Bifurcation (local)", "Gurobi Solver", "D-Wave Solver"])
with tab1:
    date_list = [date[3:-4] for date in os.listdir('data/solver/')]
    # sol_date = st.selectbox('Select Date', date_list, index=0)
    sol = pd.read_csv(f"data/solver/sb_{date_selection}.csv", index_col=0, header=0)
    sol.sort_values(by="coef", ascending=False, inplace=True)
    event = st.dataframe(sol, on_select="rerun", selection_mode="single-row")
    if event['selection']['rows'] == []:
        # paths = sol.loc[sol.index[0], "paths"]
        paths = sol["paths"].iloc[0].\
                    removeprefix("[").removesuffix("]")\
                    .replace("'", "").replace('"', "").replace(' ', "")\
                    .split(",") # remove the brackets
    else:
        paths = sol["paths"].iloc[event['selection']['rows'][0]].\
                    removeprefix("[").removesuffix("]")\
                    .replace("'", "").replace('"', "").replace(' ', "")\
                    .split(",") # remove the brackets
    
    print("PATHS", paths, "\n")

    nodes_ = set([path[:3] for path in paths])
    print("NODES_", nodes_, "\n")

    elements_ = {}
    # print("NODES", elements["nodes"], "\n")
    # print("EDGES", elements["edges"], "\n")

    elements_["nodes"] = [node for node in elements["nodes"] if node["data"]["id"] in nodes_]
    elements_["edges"] = [edge for edge in elements["edges"] if edge["data"]["id"] in paths]

    # print("NODES", elements_["nodes"], "\n")
    # print("EDGES", elements_["edges"], "\n")

    st_link_analysis(elements_, "cose", NODE_STYLE, EDGE_STYLE, key="sb")

with tab2:
    st.write("Not implemented yet")
with tab3:
    st.write("Not implemented yet")



