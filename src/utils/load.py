import pandas as pd


# load and cleanup all messages from the reddit dataset
def load_messages(path: str) -> pd.DataFrame:
    # read only necessary columns from dataset
    df = pd.read_csv(path, parse_dates=["timestamp"], usecols=["body", "timestamp"])
    # filter to only rows with non-null body
    df = df[~df.body.isnull()]
    # remap the timestamps to only the date
    df["date"] = df.timestamp.dt.date
    # remove old timestamp column
    df.drop(columns=["timestamp"], inplace=True)
    # clean body of all messages to only letters and whitespace
    df.body = df.body.str.upper().str.replace(r"[^a-zA-Z\s]", " ", regex=True)
    # sort by timestamp
    df.sort_values("date", inplace=True)
    return df


# load pre-calculated index into a DataFrame
def load_index(path: str) -> pd.DataFrame:
    # load necessary columns from csv
    df = pd.read_csv(
        path,
        usecols=["symbol", "date", "occurrences"],
        parse_dates=["date"],
    )
    return df
