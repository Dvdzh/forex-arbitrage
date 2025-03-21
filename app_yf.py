import streamlit as st 
from dataloader_yf import DataLoader

list_currency = ["USD", "EUR", "JPY", "GBP", "CHF", "AUD", "CAD"]

# Set page configuration
st.set_page_config(page_title="Forex Arbitrage Detector", layout="wide")

with st.sidebar:
    st.title("Configuration")
    st.write("### Paramètres")
    list_currency = st.multiselect("Select Currencies", list_currency, default=list_currency)
    period = st.selectbox("Select Period", ["1d", "1wk", "1mo"])
    interval = st.selectbox("Select Interval", ["1m", "5m", "15m", "30m", "1h", "1d"])

loader = DataLoader()
loader.download_data(list_currency, period, interval)
rate_series = loader.get_last_price()
rate_df = loader.series_to_df(rate_series)
fig = loader.plot_graph(rate_df)

# App header
st.title("Forex Arbitrage Opportunity Detector")
st.markdown("""
This application helps identify arbitrage opportunities in the forex market by analyzing exchange rates between multiple currencies.
""")


st.divider()

st.write("### Data Analysis")
col1, col2 = st.columns(2)
with col1:
    st.dataframe(rate_df)
with col2:
    st.plotly_chart(fig)

st.divider()
st.write("### QUBO Formulation")


""""
Dollar américain (USD)
La devise de réserve mondiale par excellence, au cœur des opérations de refinancement et de diversification des réserves internationales.
Euro (EUR)
Suivi de près par la Banque centrale européenne, avec des interventions pour stabiliser la zone euro et gérer les flux de capitaux.
Yen japonais (JPY)
La politique monétaire de la Banque du Japon influence fortement le yen, notamment dans un contexte de taux ultra-bas et d'assouplissement quantitatif.
Livre sterling (GBP)
Impactée par les décisions de la Banque d’Angleterre qui intervient pour assurer la stabilité face aux variations du marché.
Franc suisse (CHF)
Réputé comme valeur refuge, le CHF subit aussi les actions de la Banque nationale suisse pour moduler sa volatilité.
Yuan chinois (CNH/CNY)
Avec une stratégie active de la Banque populaire de Chine pour internationaliser sa monnaie et diversifier les réserves, le yuan est très suivi sur le plan des interventions.
Dollar australien (AUD)
Influencé par les politiques de la Reserve Bank of Australia et souvent impacté par les fluctuations des marchés de matières premières.
Dollar canadien (CAD)
Suivi par la Banque du Canada, dont la politique monétaire s’adapte aux évolutions des prix des matières premières et aux flux de capitaux internationaux.
"""
