import pytest
from utils.tickers import Ticker, load_tickers


def test_ticker():
    # make sure init works
    x = Ticker("", "", "", "")

    # must include all params
    with pytest.raises(Exception):
        x = Ticker()

    # check yahoo finance urls
    assert Ticker("TSLA", "", "", "").yahoo_finance_url() == "https://finance.yahoo.com/quote/TSLA"
    assert Ticker("A", "", "", "").yahoo_finance_url() == "https://finance.yahoo.com/quote/A"
    assert Ticker("", "", "", "").yahoo_finance_url() is None
    assert Ticker(None, "", "", "").yahoo_finance_url() is None


def test_load_tickers():
    # throw exception for missing files
    with pytest.raises(FileNotFoundError):
        load_tickers("data/MISSINGFILE.csv")

    # ensure loads tickers correctly
    assert load_tickers("tests/data/FAKE_stock_tickers.csv") == [
        Ticker("TESTA", "Test A Company", "Testing", "Testing"),
    ]
