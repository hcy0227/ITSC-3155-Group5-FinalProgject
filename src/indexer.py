import typing as t
import pandas as pd
from utils.load import load_messages
from utils.tickers import Ticker, load_tickers


# run indexing process to count occurrences of every stock in all messages
def create_index(path: str, messages_path: str, ts: t.List[Ticker], minimum_occurrences: int = 10):
    # load all messages from reddit dataset
    df = load_messages(messages_path)

    # access file to output compiled index of symbol occurrences
    with open(path, "w") as i_file:
        # write header
        i_file.write("symbol,date,occurrences\n")

        # index each ticker
        for i, ticker in enumerate(ts):
            # find number of occurrences in messages
            occurrences = df.body.str.count(f" {ticker.symbol} ").rename("occurrences")
            # exclude days where no reference to this stock
            occurrences = occurrences[occurrences > 0]
            # count total
            total = occurrences.sum()
            # only include tickers mentioned a minimum amount
            if total < minimum_occurrences:
                continue

            print(f"[{i + 1}/{len(ts)}]", ticker, total)

            # create index of this symbol
            partial_index = pd.concat([
                df.date[occurrences.index],
                occurrences,
            ], axis=1)
            # aggregate count by date
            partial_index = partial_index.groupby(partial_index.date).sum().reset_index()
            # add this stock's symbol to the dataframe
            partial_index["symbol"] = pd.Series(ticker.symbol, index=partial_index.index)

            # append partial index to file
            partial_index.to_csv(
                i_file,
                columns=["symbol", "date", "occurrences"],
                index=False,
                header=False,
                line_terminator="\n"
            )
            i_file.flush()


if __name__ == "__main__":
    # pre-calculate indexes so refined data is available for higher performance
    tickers = load_tickers(
        "../data/NYSE_stock_tickers.csv",
        "../data/NASDAQ_stock_tickers.csv",
    )
    create_index("../data/compiled_index_min100.csv", "../data/reddit_web.csv", tickers, minimum_occurrences=100)
    create_index("../data/compiled_index_min10.csv", "../data/reddit_web.csv", tickers, minimum_occurrences=10)
