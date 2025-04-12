import sys
import os
import json
import argparse
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.solver import SimulatedBifurcationSolver
import pandas as pd 

if __name__ == "__main__":

    # 0. Parsing des arguments 
    parser = argparse.ArgumentParser(description="DataLoader for currency data")
    parser.add_argument("-n", type=str, nargs="+", help="List of currencies to download", default=4)
    n_currency = int(parser.parse_args().n[0])

    # Get terminal width
    columns, _ = os.get_terminal_size()

    # Print header
    print("=" * columns)
    print(" Running Solver")
    print("=" * columns)

    # Read prices_temporal 
    price_df = pd.read_csv(f"data/n_currency_{n_currency}/dataloader/prices_temporal.csv", index_col=0, header=0)

    Q_paths = os.listdir(f"data/n_currency_{n_currency}/problem")
    Q_paths = [path for path in Q_paths if path.startswith("Q_")]
    
    for path in Q_paths:

        print(f"Reading {path}...")
        # Read the QUBO formulation
        Q_df = pd.read_csv(f"data/n_currency_{n_currency}/problem/{path}", index_col=0, header=0)

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
        if not os.path.exists(f"data/n_currency_{n_currency}/solver"):
            os.makedirs(f"data/n_currency_{n_currency}/solver")
        results.to_csv(f"data/n_currency_{n_currency}/solver/sb_{timestamp}.csv", index=True, header=True)