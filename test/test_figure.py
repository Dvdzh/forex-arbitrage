import json 
import pandas as pd 
import argparse
import os

if __name__ == "__main__":
  
    # 0. Parsing des arguments 
    parser = argparse.ArgumentParser(description="DataLoader for currency data")
    parser.add_argument("-n", type=str, nargs="+", help="List of currencies to download", default=4)
    n_currency = int(parser.parse_args().n[0])


    # 0. Read data 
    # price_series = pd.read_csv("data/dataloader/prices_series.csv", index_col=0, header=0)
    price_df = pd.read_csv(f"data/n_currency_{n_currency}/dataloader/prices_temporal.csv", index_col=0, header=0)

    # TODO : refactorer le code pour ne avoir que a envoyer un price_df 
    # Et tout placer dans une fonction 

    if not os.path.exists(f"data/n_currency_{n_currency}/figure/"):
        os.makedirs(f"data/n_currency_{n_currency}/figure/")
        
    for date in price_df.index:
        print(f"\n- Date: {date}")

        series = price_df.loc[date]
        # series = pd.read_csv(f"data/n_currency_{n_currency}/dataloader/prices_series.csv", index_col=0, header=0)

        pairs = series.index
        list_currency = set([ticker[:3] for ticker in pairs.tolist()])

        nodes = [{"data": {"id":ticker, 
                        "label": "CURRENCY",
                        "name": ticker}}  for ticker in list_currency]
        edges = [{"data": {"id":pair,
                        "label": "PAIR_DIRECT" if series.loc[pair] > 1 else "PAIR_INVERSE",
                        "source": pair[:3],
                        "target": pair[3:6], 
                        "rate":series.loc[pair]}} for pair in pairs]
        
        with open(f"data/n_currency_{n_currency}/figure/graph_{date}.json", "w") as f:
            json.dump({"nodes": nodes, "edges": edges}, f, indent=4)