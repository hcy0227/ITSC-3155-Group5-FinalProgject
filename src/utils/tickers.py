import pandas as pd
import numpy as np
import typing as t
from utils.cleaners import clean_symbol, clean_stock_name


# ignore these symbols
IGNORE_SYMBOLS = {
    "A",        # capital A is a common word at beginning of sentence so don't count it as a stock
    "GDP",      # gross domestic product
}


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
        if self.symbol is None or len(self.symbol) == 0:
            return None
        return f"https://finance.yahoo.com/quote/{self.symbol}"

    # convenience function to make debug statements more readable
    def __str__(self):
        return f"Ticker(symbol='{self.symbol}', name='{self.name}', sector='{self.sector}', industry='{self.industry}')"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if isinstance(other, Ticker):
            return (
                self.symbol == other.symbol and
                self.name == other.name and
                self.sector == other.sector and
                self.industry == other.industry
            )


# get a combined list of tickers from multiple exchanges
def load_tickers(*paths: str) -> t.List[Ticker]:
    tickers: t.List[Ticker] = []
    for p in paths:
        # load necessary columns from csv
        df = pd.read_csv(
            p,
            usecols=["Symbol", "Name", "Sector", "Industry"]
        )
        # don't like nan in the dataframe, so use None because it's cleaner for the code
        df = df.replace({np.nan: None})
        # map rows of file to cleaner Ticker class
        for r in df.itertuples():
            x = Ticker(clean_symbol(r.Symbol), clean_stock_name(r.Name), r.Sector, r.Industry)
            # ignore tickers that don't match the cleaned symbol
            if x.symbol != r.Symbol:
                continue
            # ignore tickers without a sector
            if x.sector is None:
                continue
            # only return tickers not in the ignore list
            if x.symbol not in IGNORE_SYMBOLS:
                tickers.append(x)
    return tickers
