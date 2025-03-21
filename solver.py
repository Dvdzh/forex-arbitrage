import networkx as nx
import plotly.graph_objects as go
import pandas as pd 
import numpy as np 
from dataloader_yf import DataLoader
import simulated_bifurcation as sb 

# itertools
import itertools
import yfinance as yf 
class Solver():

    def __init__(self):
        self.Q = None

    def to_qubo(self, price_series:pd.DataFrame, constraint:float):
    
        r = - np.log(price_series) 
        R = pd.DataFrame(np.diag(r), columns=price_series.index, index=price_series.index)
        M1 = self._get_M1(len(price_series))
        M2 = self._get_M2(len(price_series))

        self.Q = R + constraint * (M1 + M2)
        return self.Q
    
    def _get_M1(self, size:int):
        M1 = np.zeros((size, size))
        for i in range(size):
            for j in range(size):
                for j2 in range(size):
                    if j2 != j:
                        M1[i, j] = 1
        return M1
    
    def _get_M2(self, size:int):
        M2 = np.zeros((size, size))
        for j in range(size):
            for i in range(size):
                for i2 in range(size):
                    if i2 != i:
                        M2[i, j] = 1
        return M2
    
    def check_solution(self, tickers, vector):
        paths = self._vector_to_paths(tickers, vector)
        if len(paths) == 0:
            return False
        return self._check_solution(paths)

    def _vector_to_paths(self, tickers, vector):
        return [ticker for ticker, value in zip(tickers, vector) if value == 1]
    
    def _check_solution(self, paths):
        sources, destinations = [], []
        for path in paths:
            sources.append(path[:3])
            destinations.append(path[3:])
        return len(set(sources)) == len(sources) and len(set(destinations)) == len(destinations)

class BellmanFord(Solver):
    def __init__(self):
        super().__init__()
        self.currency_graph = nx.DiGraph()

    def solve(self, source):
        dist = {node: float('inf') for node in self.currency_graph.nodes()}
        dist[source] = 0
        for _ in range(len(self.currency_graph.nodes()) - 1):
            for u, v in self.currency_graph.edges():
                if dist[u] + self.currency_graph[u][v]['weight'] < dist[v]:
                    dist[v] = dist[u] + self.currency_graph[u][v]['weight']
        return dist
    
    def plot(self, source):
        pass

class DwaveQuantumSolver(Solver):

    def __init__(self):
        super().__init__()
    
    def solve(self):
        pass

    def plot(self):
        pass

class GurobiSolver(Solver):
    
    def __init__(self):
        super().__init__()
    
    def solve(self):
        pass

    def plot(self):
        pass

class QiskitQuantumSolver(Solver):

    def __init__(self):
        super().__init__()
    
    def solve(self):
        pass

    def plot(self):
        pass

class SimulatedBifurcation(Solver):

    def __init__(self):
        super().__init__()
    
    def solve(self):
        pass

    def plot(self):
        pass

import torch 

if __name__ == "__main__":

    # 0. DataLoader
    loader = DataLoader()
    loader.download_data(list_currency=["USD", "EUR", "JPY", "GBP", "CHF", "AUD", "CAD"], # "CNY", 
                         period="1d",
                         interval="1m")
    series = loader.get_last_price()
    tickers = loader.tickers

    prices_series = loader.get_prices()

    for i in range(5):
        series = prices_series.iloc[-i]
        print("\n", series.name)
        for constraint in np.linspace(0.1, 1, 10):
            solver = Solver()
            Q = solver.to_qubo(series, constraint)
            Q_tensor = torch.tensor(Q.values).float()
            vector, value = sb.minimize(Q_tensor, domain='binary')
            print(f"Result : {solver.check_solution(tickers, vector.numpy())}")
