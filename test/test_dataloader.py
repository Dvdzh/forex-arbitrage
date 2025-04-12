import sys
import os
import json
import argparse
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.dataloader import DataLoader


if __name__ == "__main__":

    # TODO : move this into an utils file 
    # Get terminal width
    columns, _ = os.get_terminal_size()

    # 0. Parsing des arguments 
    parser = argparse.ArgumentParser(description="DataLoader for currency data")
    parser.add_argument("-n", type=str, nargs="+", help="List of currencies to download", default=4)
    n_currency = int(parser.parse_args().n[0])
    
    # 1. Configuration values
    list_currency = ["USD", "EUR", "JPY", "CHF", "GBP", "AUD", "CAD", "NZD"]
    config = dict(
        list_currency=list_currency[:n_currency],
        period="1d",
        interval="1m",
        source="yahooFinance",
    )
    
    # Print header
    print("=" * columns)
    print(" Running DataLoader")
    print("=" * columns)

    # 1. Create DataLoader object
    loader = DataLoader()
    
    # Function 1 : Download data 
    print("\nDownloading data...")
    # TODO : move this in the DataLoader function download_data with a verbose option 
    print("- Configuration :")
    for key, value in config.items():
        print(f"  - {key} : {value}")
    print("\n") 
    loader.download_data(config["list_currency"], config["period"], config["interval"])

    # Function 2 : Get all prices in dataframe 
    # TODO : move this in the DataLoader function get_prices, with a verbose option 
    price_temporal_df = loader.get_prices()
    print("\nGetting all prices...")
    print("- Shape : ", price_temporal_df.shape)
    print("- Head : ")
    print(price_temporal_df.head())
    print("- Tail : ")
    print(price_temporal_df.tail())

    # TODO : move this in the DataLoader function get_last_price
    # Function 3 : Save data 
    # check if f"data/n_currency_{n_currency}" exists
    if not os.path.exists(f"data/n_currency_{n_currency}/dataloader"):
        print(f"Creating directory data/n_currency_{n_currency}/dataloader")
        os.makedirs(f"data/n_currency_{n_currency}/dataloader")

    with open(f"data/n_currency_{n_currency}/dataloader/list_currency.json", "w") as f:
        json.dump(loader.list_currency, f, indent=4)
    with open(f"data/n_currency_{n_currency}/dataloader/tickers.json", "w") as f:
        json.dump(loader.tickers, f, indent=4)
    with open(f"data/n_currency_{n_currency}/dataloader/config.json", "w") as f:
        json.dump(config, f, indent=4)
    price_temporal_df.iloc[:20].to_csv(f"data/n_currency_{n_currency}/dataloader/prices_temporal.csv", index=True, header=True)