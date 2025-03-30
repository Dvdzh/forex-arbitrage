import itertools
import yfinance as yf
from typing import List
import pandas as pd 
import networkx as nx

import plotly.graph_objects as go
import json 

import os

class DataLoader():

    def __init__(self):
        self.list_currency = None
        self.tickers = None
        self.data = None
        self.period = None
        self.interval = None
        self.rate_df = None

    def download_data(self, list_currency:List[str], period:str, interval:str) -> pd.DataFrame:
        """
        Télécharge les données des paires de devises depuis Yahoo Finance.
        
        Args:
            list_currency (List[str]): Liste des devises à télécharger
            period (str): Période de temps à télécharger
            interval (str): Intervalle de temps à télécharger

        Returns:
            pandas.DataFrame: DataFrame contenant les données historiques des paires de devises
            
        Raises:
            ConnectionError: Si la connexion à Yahoo Finance échoue
            
        Examples:
            >>> loader = DataLoader()
            >>> data = loader.download_data("2021-01-01", "2021-12-31")
        """
        # Keep on objet attributes at each download
        self.period = period
        self.interval = interval

        # Downloading data 
        self.list_currency = sorted(list_currency)
        self.tickers = [f"{a}{b}=X" for a, b in itertools.permutations(self.list_currency, 2)]
        self.data = yf.download(self.tickers, period=period, interval=interval)

        return self.data
    
    def get_last_price(self):
        return self.data.dropna(axis=0)["Close"].iloc[-1]

    def get_prices(self):
        return self.data.dropna(axis=0)["Close"]
    
    def series_to_df(self, series):
        df = pd.DataFrame(index=self.list_currency, columns=self.list_currency)
        for a, b in itertools.permutations(self.list_currency, 2):
            df.loc[a, b] = series[f"{a}{b}=X"]
        for a in self.list_currency:
            df.loc[a, a] = 1

        self.rate_df = df
        return self.rate_df
    
    def _create_graph(self, rate_df):
        # Create a directed graph
        G = nx.DiGraph()

        # Add nodes
        for currency in rate_df.columns:
            G.add_node(currency)
        
        # Add edges
        for i, row in rate_df.iterrows():
            for j, rate in row.items():
                if i != j:
                    G.add_edge(i, j, weight=rate)
        
        return G
    
    def plot_graph(self, rate_df:pd.DataFrame, show:bool=False):
        
        G = self._create_graph(rate_df)
        pos = nx.circular_layout(G)

        # Draw nodes
        node_trace = go.Scatter(
            x=[pos[k][0] for k in G.nodes()],
            y=[pos[k][1] for k in G.nodes()],
            mode='markers',
            marker=dict(
                size=50,
                color='lightblue',
                line=dict(width=2, color='darkblue')
            ),
            text=[k for k in G.nodes()],
            hoverinfo='text',
            hovertemplate='<b>%{text}</b><br>'
        )

        # Draw edges
        edge_traces = []
        for u, v, data in G.edges(data=True):
            weight = min(1.5 * data['weight'], 3)
            edge_trace = go.Scatter(
                x=[pos[u][0], pos[v][0]],
                y=[pos[u][1], pos[v][1]],
                mode='lines',
                line=dict(width=weight, color='black'),
                hoverinfo='none'
            )
            edge_traces.append(edge_trace)

        # Create figure
        fig = go.Figure()
        
        # Add all edge traces individually
        for edge_trace in edge_traces:
            fig.add_trace(edge_trace)
            
        # Add node trace
        fig.add_trace(node_trace)
        
        # Update layout
        fig.update_layout(
            showlegend=False,
            hovermode='closest',
            margin=dict(b=0, l=0, r=0, t=0),
            height=400
        )
        
        if show:
            fig.show()

        return fig

if __name__ == "__main__":

    # Get terminal width
    columns, _ = os.get_terminal_size()

    # Print header
    print("=" * columns)
    print(" Running DataLoader")
    print("=" * columns)

    # 0. Create DataLoader object
    loader = DataLoader()

    # 1. Download data
    config = {
        "list_currency": ["USD", "EUR", "JPY", "CHF"],
        "period": "1d",
        "interval": "1m",
        "source": "yahooFinance",
    }
    print("\nDownloading data...")
    print("- Configuration :")
    for key, value in config.items():
        print(f"  - {key} : {value}")
    print("\n") 
    loader.download_data(config["list_currency"], config["period"], config["interval"])

    # # 2. Get last price
    # price_series = loader.get_last_price()
    # print("\nGetting last price...")
    # print("\n")

    # 2.1 Get all prices
    price_temporal_df = loader.get_prices()
    print("\nGetting all prices...")
    print("- Shape : ", price_temporal_df.shape)
    print("- Head : ")
    print(price_temporal_df.head())
    print("- Tail : ")
    print(price_temporal_df.tail())

    # # 3. Convert series to DataFrame
    # price_last_df = loader.series_to_df(price_series)

    # # 4. Plot graph
    # fig = loader.plot_graph(price_last_df, show=True)

    # 5. Saving    
    with open("data/dataloader/list_currency.json", "w") as f:
        json.dump(loader.list_currency, f, indent=4)
    with open("data/dataloader/tickers.json", "w") as f:
        json.dump(loader.tickers, f, indent=4)
    with open("data/dataloader/config.json", "w") as f:
        json.dump(config, f, indent=4)
    price_temporal_df.iloc[:10].to_csv("data/dataloader/prices_temporal.csv", index=True, header=True)
    # price_series.to_csv("data/dataloader/prices_series.csv", index=True, header=True)
    