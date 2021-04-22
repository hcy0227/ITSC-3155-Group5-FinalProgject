import pytest
import datetime as dt
from utils.filters import StockSelection, TimeSelection


def test_stock_selection():
    # error on no params
    with pytest.raises(ValueError):
        StockSelection()
    # error on both params
    with pytest.raises(ValueError):
        StockSelection(top=10, symbol="ASDF")

    # top n selection
    n = 5
    x = StockSelection(top=n)
    assert x.top == n
    assert x.symbol is None
    assert x.is_top_n()
    assert x.value() == f"top|{n}"

    # symbol selection
    s = "GME"
    x = StockSelection(symbol=s)
    assert x.top is None
    assert x.symbol == s
    assert not x.is_top_n()
    assert x.value() == f"symbol|{s}"

    # invalid format
    with pytest.raises(ValueError):
        StockSelection.from_value("asdf")

    # valid formats
    assert StockSelection.from_value("top|5") == StockSelection(top=5)
    assert StockSelection.from_value("symbol|ASDF") == StockSelection(symbol="ASDF")

    # invalid comparison
    with pytest.raises(Exception):
        test = StockSelection(top=4) == 5


def test_time_selection():
    # make sure init works
    TimeSelection()

    # all time option
    assert TimeSelection.from_value("all").min_date is None

    # test time ranges on sliding window to simulate each day of 10 years
    for i in range(365 * 10):
        offset = dt.timedelta(days=i)
        ref_date = dt.date(2021, 1, 1) + offset
        assert TimeSelection.from_value("week", today=ref_date).min_date == dt.date(2020, 12, 26) + offset
        assert TimeSelection.from_value("month", today=ref_date).min_date == dt.date(2020, 12, 3) + offset
        assert TimeSelection.from_value("3month", today=ref_date).min_date == dt.date(2020, 10, 4) + offset
        assert TimeSelection.from_value("year", today=ref_date).min_date == dt.date(2020, 1, 3) + offset

    # invalid option
    with pytest.raises(ValueError):
        assert TimeSelection.from_value("asdf")

    # invalid comparisons
    x = TimeSelection(min_date=ref_date)
    with pytest.raises(Exception):
        test = x == 10
    with pytest.raises(Exception):
        test = x == "asdf"
    with pytest.raises(Exception):
        test = x == 45.5
