import sys
import os
import json
import argparse
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.problem import QUBOProblem
import pandas as pd 

if __name__ == "__main__":

    # 0. Parsing des arguments 
    parser = argparse.ArgumentParser(description="DataLoader for currency data")
    parser.add_argument("-n", type=str, nargs="+", help="List of currencies to download", default=4)
    n_currency = int(parser.parse_args().n[0])
    
    config = dict(
        n4=dict(
            constraint_diag=5,
            constraint_M1=1,
            constraint_M2=1,
        ),
        n5=dict(
            constraint_diag=3.4,
            constraint_M1=1,
            constraint_M2=1,
        ),
        n6=dict(
            constraint_diag=5,
            constraint_M1=1,
            constraint_M2=1,
        ),
        n7=dict(
            constraint_diag=5,
            constraint_M1=1,
            constraint_M2=1,
        ),
    )
    # TODO : move this into an utils file
    # Get terminal width
    columns, _ = os.get_terminal_size()

    # Print header
    print("=" * columns)
    print(" Running Problem")
    print("=" * columns)

    # 0. Read data 
    # price_series = pd.read_csv("data/dataloader/prices_series.csv", index_col=0, header=0)
    price_df = pd.read_csv(f"data/n_currency_{n_currency}/dataloader/prices_temporal.csv", index_col=0, header=0)


    qubo = QUBOProblem()
    constraint_diag = config[f"n{n_currency}"]["constraint_diag"]
    constraint_M1 = config[f"n{n_currency}"]["constraint_M1"]
    constraint_M2 = config[f"n{n_currency}"]["constraint_M2"]

    # TODO : refactorer le code pour ne avoir que a envoyer un price_df 
    # Et tout placer dans une fonction 

    for date in price_df.index:
        print(f"\n- Date: {date}")

        price_series = price_df.loc[date]
        # 1. Formulate QUBO

        Q = qubo.get_Q(price_series, constraint_M1=constraint_M1, constraint_M2=constraint_M2, constraint_diag=constraint_diag)

        # 2. Save results
        # TODO : move the save function in the QUBOProblem class
        if not os.path.exists(f"data/n_currency_{n_currency}/problem"):
            os.makedirs(f"data/n_currency_{n_currency}/problem")
        Q.to_csv(f"data/n_currency_{n_currency}/problem/Q_{date}.csv", header=True, index=True)
        # TODO : move this into the QUBOProblem class, with a verbose option
        print("- Formulation shape:")
        print(f"  - Q : {Q.shape}")
        print(f"  - R : {qubo.R.shape}")
        print(f"  - M1 : {qubo.M1.shape}")  
        print(f"  - M2 : {qubo.M2.shape}\n")