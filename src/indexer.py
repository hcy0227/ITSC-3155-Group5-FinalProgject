import typing as t
import pandas as pd
from utils.load import load_messages
from utils.tickers import Ticker, load_tickers


# run indexing process to count occurrences of every stock in all messages
def create_index(name: str, ts: t.List[Ticker], minimum_occurrences: int = 10):
    # load all messages from reddit dataset
    df = load_messages()

    # access file to output compiled index of symbol occurrences
    with open(f"../data/{name}.csv", "w") as i_file:
        # write header
        i_file.write("symbol,date,occurrences\n")

        # index each ticker
        for i, ticker in enumerate(ts):
            # find number of occurrences
            occurrences = df.body.str.count(f" {ticker.symbol} ").rename("occurrences")
            occurrences = occurrences[occurrences > 0]
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
            partial_index = partial_index.groupby(partial_index.date).sum().reset_index()
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
    tickers = load_tickers("NYSE", "NASDAQ")
    create_index("compiled_index_min100", tickers, minimum_occurrences=100)
    create_index("compiled_index_min10", tickers, minimum_occurrences=10)
