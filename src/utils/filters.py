import datetime as dt


# class to handle stock selection options
class StockSelection:
    # represents either selecting the top n stocks, or a single stock by symbol
    def __init__(self, top: int = None, symbol: str = None):
        if top is not None and symbol is not None:
            # cannot represent both top n stocks and a single stock
            raise ValueError("Must represent either top or symbol, not both")
        self.top = top
        self.symbol = symbol

    # decode a stock selection value from the dropdown on the app
    @classmethod
    def from_value(cls, value):
        # value is in the following format
        # top|n >> select the top n stocks
        # symbol|X >> select a single symbol X
        a, b = value.split("|")
        if a == "top":
            return cls(top=int(b))
        elif a == "symbol":
            return cls(symbol=b)
        raise ValueError(f"Unknown stock selection value: {value}")

    # check if this selection represents selecting the top n stocks
    def is_top_n(self):
        return self.top is not None

    # check if this selection represents selecting a single stock
    def is_symbol(self):
        return self.symbol is not None

    # encode this stock selection into a value that can be used in UI components
    def value(self):
        if self.is_top_n():
            return f"top|{self.top}"
        else:
            return f"symbol|{self.symbol}"

    # convenience function so debug statements are more readable
    def __str__(self):
        if self.is_top_n():
            return f"StockSelection(top={self.top})"
        else:
            return f"StockSelection(symbol={self.symbol})"


# class to handle time filtering options
class TimeSelection:
    # represent filtering the data by a minimum date
    def __init__(self, min_date: dt.date = None):
        self.min_date = min_date

    # decode a time selection value from the dropdown on the app
    @classmethod
    def from_value(cls, value):
        # get reference to today because filters are based on the current time
        today = dt.datetime.now().date()
        if value == "all":
            # no limit
            return cls()
        elif value == "week":
            # >= past 7 days
            return cls(min_date=today - dt.timedelta(days=7 - 1))
        elif value == "month":
            # >= past 30 days
            return cls(min_date=today - dt.timedelta(days=30 - 1))
        elif value == "3month":
            # >= past 90 days
            return cls(min_date=today - dt.timedelta(days=90 - 1))
        elif value == "year":
            # >= past 365 days
            return cls(min_date=today - dt.timedelta(days=365 - 1))
        # safety for invalid values
        raise ValueError(f"Unknown time selection value: {value}")

    # convenience function so debug statements are more readable
    def __str__(self):
        min_date_str = "None" if self.min_date is None else self.min_date.isoformat()
        return f"TimeSelection(min_date={min_date_str})"
