import pandas as pd 
import numpy as np 
import networkx as nx

# import bellmanford as bf  
import simulated_bifurcation as sb 
import torch 

from abc import ABC, abstractmethod
import os 

class Solver(ABC):

    def __init__(self, tickers):
        self.tickers = tickers
        pass

    @abstractmethod
    def solve(self):
        pass

    def _vector_to_paths(self, vector):
        return [ticker for ticker, value in zip(self.tickers, vector) if value == 1]
    
    def _check_solution(self, paths):
        sources, destinations = [], []
        for path in paths:
            sources.append(path[:3])
            destinations.append(path[3:6])
        cond = sorted(sources) == sorted(destinations)
        if cond:
            return True 
        return False


class BellFordSolver(Solver):
     
    def __init__(self):
        super().__init__()

    def solve(self, G:nx.DiGraph, source:str, target:str):
        length, nodes, negative_cycle = bf.bellmanford(G, source, target, weight='weight')
        return length, nodes, negative_cycle

class DwaveQuantumSolver(Solver):

    def __init__(self):
        super().__init__()
    
    def solve(self):
        pass

class GurobiSolver(Solver):
    
    def __init__(self):
        super().__init__()
    
    def solve(self):
        pass

class SimulatedBifurcationSolver(Solver):

    def __init__(self, tickers):
        super().__init__(tickers)
    
    def solve(self, Q_df:pd.DataFrame, price_series:pd.Series):

        # Solve the QUBO problem
        Q_tensor = torch.tensor(Q_df.values).float()
        vectors, values = sb.minimize(Q_tensor, domain='binary', max_steps=200_000, best_only=False, heated=True, agents=124)
        
        # Check each solution
        valid_paths, valid_values, valid_coefs = [], [], []
        for vector, value in zip(vectors, values):
            paths_list = self._vector_to_paths(vector.numpy())
            valid = self._check_solution(paths_list)
            if valid:
                coef = np.prod([price_series.loc[ticker] for ticker in paths_list])
                valid_paths.append(paths_list)
                valid_values.append(value)
                valid_coefs.append(coef)
                print(f"Valid: {valid}, paths: {paths_list}, value: {value}, coef: {coef}")
        return valid_paths, valid_values, valid_coefs
    
if __name__ == "__main__":

        # Get terminal width
    columns, _ = os.get_terminal_size()

    # Print header
    print("=" * columns)
    print(" Running Solver")
    print("=" * columns)

    # Read prices_temporal 
    price_df = pd.read_csv("data/dataloader/prices_temporal.csv", index_col=0, header=0)

    Q_paths = os.listdir("data/problem")
    Q_paths = [path for path in Q_paths if path.startswith("Q_")]
    
    for path in Q_paths:

        print(f"Reading {path}...")
        # Read the QUBO formulation
        Q_df = pd.read_csv(f"data/problem/{path}", index_col=0, header=0)

        # Read the price series
        timestamp = path[2:-4]
        price_series = price_df.loc[timestamp]

        # Using simulated bifurcation solver
        print("\nUsing simulated bifurcation...")
        solver = SimulatedBifurcationSolver(tickers=Q_df.columns)
        valid_paths, valid_values, valid_coefs = solver.solve(Q_df, price_series)
        results = pd.DataFrame()
        for paths, value, coef in zip(valid_paths, valid_values, valid_coefs):
            if coef > 1:
                print("=====================================")
                print("Arbitrage opportunity detected!")
                print("=====================================")
                print(f"Paths: {paths}, value: {value}, coef: {coef}")
            results = pd.concat([results, pd.DataFrame({"paths": [paths], "value": [value], "coef": [coef]})], ignore_index=True)
        
        # Save results
        results.to_csv(f"data/solver/sb_{timestamp}.csv", index=True, header=True)
        # # dump json 
        # # result = pd.DataFrame()
        # import json 
        # with open(f"data/solver/solutions_{timestamp}.json", "w") as f:

        #     json.dump({"paths": valid_paths, "coefs": valid_coefs}, f, indent=4)