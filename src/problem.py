import numpy as np
import pandas as pd 
from typing import List
import os 

class QUBOProblem():

    def __init__(self):
        self.Q = None

    def get_Q(self, price_series:pd.DataFrame, constraint_M1:float, constraint_M2:float, constraint_diag:float, list_currency:List[str]=None):

        if list_currency is None:
            list_currency = set([ticker[:3] for ticker in price_series.index])
        self.list_currency = list_currency  

        r = - np.log(price_series) + constraint_diag
        R = pd.DataFrame(np.diagflat(r), columns=price_series.index, index=price_series.index)
        M1 = self._get_M1(price_series.index)
        M2 = self._get_M2(price_series.index)
        self.Q = R + constraint_M1 * M1 + constraint_M2 * M2

        self.R = R
        self.M1 = M1
        self.M2 = M2

        return self.Q
    
    def _get_M1(self, columns:List[str]):
        M1 = pd.DataFrame(0, columns=columns, index=columns)
        for source_destination in M1.index:
            source = source_destination[:3]
            destination = source_destination[3:6]
            destination_list = [dest for dest in self.list_currency if dest != destination and dest != source]
            for dest in destination_list:
                M1.loc[source_destination, source+dest+"=X"] = 1
                M1.loc[source_destination, destination+dest+"=X"] = -2

        return M1
    
    def _get_M2(self, columns:List[str]):
        M2 = pd.DataFrame(0, columns=columns, index=columns)
        for source_destination in M2.index:
            source = source_destination[:3]
            destination = source_destination[3:6]
            source_list = [src for src in self.list_currency if src != destination and src != source]
            for src in source_list:
                M2.loc[source_destination, src+destination+"=X"] = 1
                M2.loc[source_destination, src+source+"=X"] = -2

        return M2
    
if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser(description="DataLoader for currency data")
    parser.add_argument("--n_currency", type=str, nargs="+", help="List of currencies to download", default=4)
    n_currency = int(parser.parse_args().n_currency[0])
    
    # Get terminal width
    columns, _ = os.get_terminal_size()

    # Print header
    print("=" * columns)
    print(" Running Problem")
    print("=" * columns)

    # 0. Read data 
    # price_series = pd.read_csv("data/dataloader/prices_series.csv", index_col=0, header=0)
    price_df = pd.read_csv("data/dataloader/prices_temporal.csv", index_col=0, header=0)

    qubo = QUBOProblem()
    constraint_diag = 5
    constraint_M1 = 1
    constraint_M2 = 1

    for date in price_df.index:
        print(f"\n- Date: {date}")

        # 1. Formulate QUBO
        price_series = price_df.loc[date]
        Q = qubo.get_Q(price_series, constraint_M1=constraint_M1, constraint_M2=constraint_M2, constraint_diag=constraint_diag)

        # 2. Save results
        Q.to_csv(f"data/problem/Q_{date}.csv", header=True, index=True)
        # qubo.R.to_csv(f"data/problem/R_{date}.csv", header=True, index=True)
        # qubo.M1.to_csv(f"data/problem/M1_{date}.csv", header= True, index=True)
        # qubo.M2.to_csv(f"data/problem/M2_{date}.csv", header= True, index=True)
        print("- Formulation shape:")
        print(f"  - Q : {Q.shape}")
        print(f"  - R : {qubo.R.shape}")
        print(f"  - M1 : {qubo.M1.shape}")  
        print(f"  - M2 : {qubo.M2.shape}\n")

    # # 1. Formulate QUBO
    # print("\nFormulating QUBO...")
    # qubo = QUBOProblem()
    # constraint = 1
    # Q = qubo.get_Q(price_series, constraint=constraint)

    # # 2. Save results
    # Q.to_csv(f"data/problem/Q_{constraint}.csv")
    # qubo.R.to_csv(f"data/problem/R_{constraint}.csv")
    # qubo.M1.to_csv(f"data/problem/M1_{constraint}.csv")
    # qubo.M2.to_csv(f"data/problem/M2_{constraint}2.csv")

    # print("\n- Formulation shape:")
    # print(f"  - Q : {Q.shape}")
    # print(f"  - R : {qubo.R.shape}")
    # print(f"  - M1 : {qubo.M1.shape}")
    # print(f"  - M2 : {qubo.M2.shape}\n")