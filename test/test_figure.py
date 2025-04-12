import json 
import pandas as pd 
import argparse
import os

if __name__ == "__main__":
  
    # 0. Parsing des arguments 
    parser = argparse.ArgumentParser(description="DataLoader for currency data")
    parser.add_argument("-n", type=str, nargs="+", help="List of currencies to download", default=4)
    n_currency = int(parser.parse_args().n[0])


    series = pd.read_csv(f"data/n_currency_{n_currency}/dataloader/prices_series.csv", index_col=0, header=0)

    pairs = series.index
    list_currency = set([ticker[:3] for ticker in pairs.tolist()])

    nodes = [{"data": {"id":ticker, 
                    "label": "CURRENCY",
                    "name": ticker}}  for ticker in list_currency]
    edges = [{"data": {"id":pair,
                    "label": "PAIR_DIRECT" if series.loc[pair][0] > 1 else "PAIR_INVERSE",
                    "source": pair[:3],
                    "target": pair[3:6], 
                    "rate":series.loc[pair][0]}} for pair in pairs]
    with open(f"data/n_currency_{n_currency}/dataloader/graph.json", "w") as f:
        json.dump({"nodes": nodes, "edges": edges}, f, indent=4)