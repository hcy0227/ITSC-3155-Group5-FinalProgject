import pandas as pd
import numpy as np
import typing as t
from utils.cleaners import clean_symbol, clean_stock_name


# class to hold stock information
class Ticker:
    # initialize with descriptive attributes
    def __init__(self, symbol: str, name: str, sector: str, industry: str):
        self.symbol = symbol
        self.name = name
        self.sector = sector
        self.industry = industry

    # generate link to yahoo finance for this stock
    def yahoo_finance_url(self):
        # based on Charlotte's research in using yahoo finance and looking at the pattern of the url
        return f"https://finance.yahoo.com/quote/{self.symbol}"

    # convenience function to make debug statements more readable
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
        # don't like nan in the dataframe, so use None because it's cleaner for the code
        df = df.replace({np.nan: None})
        # map rows of file to cleaner Ticker class
        for r in df.itertuples():
            x = Ticker(clean_symbol(r.Symbol), clean_stock_name(r.Name), r.Sector, r.Industry)
            # only return tickers with at least 3 letters in symbol, so searching is more accurate
            if len(x.symbol) >= 3:
                tickers.append(x)
    return tickers
