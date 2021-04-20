import pandas as pd
import typing as t
from utils.cleaners import clean_symbol


class Ticker:
    # initialize with descriptive attributes
    def __init__(self, symbol: str, name: str, sector: str, industry: str):
        self.symbol = symbol
        self.name = name
        self.sector = sector
        self.industry = industry

    # convenience for debug
    def __str__(self):
        return f"Ticker(symbol='{self.symbol}', name='{self.name}')"

    def __repr__(self):
        return str(self)


# get a combined list of tickers from multiple exchanges
def load_tickers(*args: str) -> t.List[Ticker]:
    tickers: t.List[Ticker] = []
    for e in args:
        # load necessary columns from csv
        df = pd.read_csv(
            f"../data/{e}_stock_tickers.csv",
            usecols=["Symbol", "Name", "Sector", "Industry"]
        )
        # map rows of file to cleaner Ticker class
        for r in df.itertuples():
            x = Ticker(clean_symbol(r.Symbol), r.Name, r.Sector, r.Industry)
            # only return tickers with at least 3 letters in symbol, so searching is more accurate
            if len(x.symbol) >= 3:
                tickers.append(x)
    return tickers
