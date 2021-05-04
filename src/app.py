import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objects as go
from utils.tickers import Ticker, load_tickers
from utils.load import load_index
import typing as t
from utils.filters import StockSelection, TimeSelection


# =========
# DATA LOAD
# =========


tickers = load_tickers(
    "../data/NYSE_stock_tickers.csv",
    "../data/NASDAQ_stock_tickers.csv",
)
keyed_tickers = {x.symbol: x for x in tickers}
index = load_index("../data/compiled_index_min10_keepcase.csv")


# =======
# FILTERS
# =======


# filter results dataframe to specific stock(s) based on current user selections
def apply_ticker_filter(results: pd.DataFrame, stock: StockSelection, sector: str):
    f = None
    if stock.is_top_n():
        if sector != "all":
            # filter by matching sector if showing top n stocks
            f = [x for x in tickers if x.sector == sector]
    else:
        # filter to only selected ticker
        f = [keyed_tickers[stock.symbol]]

    if f is not None:
        # apply filter by matching symbols
        results = results[results.symbol.isin(x.symbol for x in f)]
    return results


# filter results dataframe to specific date range based on current user selection
def apply_time_filter(results: pd.DataFrame, time_selection: str):
    # parse selection value
    selection = TimeSelection.from_value(time_selection)
    # filter to minimum date based on user selection
    if selection.min_date is not None:
        results = results[results.date >= pd.to_datetime(selection.min_date)]
    return results


# ===============
# BASE COMPONENTS
# ===============


# base section heading component for UI
def make_section_heading(title: str, info: str = None):
    return html.Div(className="section-header", children=[
        html.H2(children=title),
        html.P(children=info),
    ])


# create the stock selection dropdown with all options
def make_stock_dropdown():
    options = []
    # add top n options
    for n in [1, 2, 5, 10, 20]:
        options.append(dict(
            label=f"the top {n} stocks",
            value=StockSelection(top=n).value(),
        ))

    # get unique set of symbols present in the index
    indexed_symbols = sorted(set(index.symbol))
    # add symbol options
    for s in indexed_symbols:
        ticker = keyed_tickers.get(s)
        if ticker is not None:
            options.append(dict(
                label=f"({ticker.symbol}) {ticker.name}",
                value=StockSelection(symbol=ticker.symbol).value(),
            ))

    # make component
    return dcc.Dropdown(
        id="stock_selection",
        options=options,
        value=StockSelection(top=5).value(),
        placeholder="Select stocks",
        clearable=False,
    )


# create the time range selection dropdown with specific options
def make_time_dropdown():
    return dcc.Dropdown(
        id="time_selection",
        options=[
            dict(label="this week", value="week"),
            dict(label="the past 30 days", value="month"),
            dict(label="the past 90 days", value="3month"),
            dict(label="this year", value="year"),
            dict(label="all time", value="all"),
        ],
        value="month",
        placeholder="Select time frame",
        clearable=False,
    )


# create the industry selection dropdown based on the tickers loaded
def make_category_dropdown():
    # make base option
    options = [
        dict(label="All Industries", value="all"),
    ]
    # find unique categories given the indexed tickers
    indexed_tickers = (keyed_tickers.get(x) for x in set(index.symbol) if keyed_tickers.get(x) is not None)
    unique_sectors = sorted(set(ticker.sector for ticker in indexed_tickers if ticker.sector is not None))
    # add each unique category
    for x in unique_sectors:
        options.append(dict(label=x, value=x))
    # create component
    return dcc.Dropdown(
        id="category_selection",
        options=options,
        value="all",
        placeholder="Select industry",
        clearable=False,
    )


# create a stock link cell to Yahoo Finance for the financial information section
def make_stock_link_cell(i: int, ticker: Ticker):
    # nest visible cell inside clickable container so easier to navigate and use
    return html.A(href=ticker.yahoo_finance_url(), target="_blank", children=[
        html.Div(
            className="cell",
            children=[
                # basic component that shows the ranking, symbol, and name of a ticker
                html.Span(className="column index", children=i),
                html.Span(className="column symbol", children=ticker.symbol),
                html.Span(className="column name", children=ticker.name),
                # purple indicator just to signify it's connected to Yahoo Finance
                html.Span(className="indicator"),
            ],
        ),
    ])


# ========
# MAIN APP
# ========


app = dash.Dash("WallStreetBets Tracker")
app.layout = html.Div([
    # header
    html.Div(className="header", children=[
        html.H1("WallStreetBets Tracker"),
    ]),

    # controls
    html.Div(className="controls", children=[
        html.Span(className="control-word", children="Show me"),
        make_stock_dropdown(),
        html.Span(className="control-word", children="for"),
        make_time_dropdown(),
        html.Div(id="category_container", children=[
            html.Span(className="control-word", children="in"),
            make_category_dropdown(),
        ]),
    ]),

    html.Div(className="central-content", children=[
        # explanation
        make_section_heading("Introduction", info=[
            html.P(
                "Welcome to WallStreetBets Tracker! WallStreetBets Tracker is designed to allow you to "
                "see how often stocks are mentioned in the Reddit/WallStreetBets forum. This way you can "
                "see if a stock is becoming more popular!"
            ),
            html.P(
                "Investing is often intimidating and can be risky if you feel like you have made a bad "
                "decision. While we are not recommending what stocks you are investing in, we are here to provide "
                "you with stocks that may be trending like GameStop was in January 2021."),
            html.P(
                "You can view the popularity of various stocks over time using the graphs below, and once you find a "
                "stock you want to know more about, go to the bottom of the page and click the one you are interested "
                "in. It will take you to the stock’s Yahoo Finance page where you can find the financial information "
                "about the stock before you invest. Happy Investing!"
            ),
        ]),
        # graphs
        make_section_heading("Stock Rankings", info="Compare stocks based on their overall popularity"),
        dcc.Graph(id="ranking_graph"),
        make_section_heading("Stock Symbol Frequency", info="Understand the trends in people mentioning specific stocks over time"),
        dcc.Graph(id="trend_graph"),
        make_section_heading("Relative Stock Symbol Frequency", info="See how stocks compare to others mentioned on the same day"),
        dcc.Graph(id="relative_trend_graph"),


        # links
        make_section_heading("Financial Information", info="View each stock's price trend on Yahoo Finance"),
        html.Div(id="links_container", className="links-container"),

    ]),


    # disclaimer
    html.Div(className="footer", children=[
        html.H2("Disclaimer"),
        html.P(className="legal-text",
               children="We do not provide personal investment advice and We are not a qualified licensed investment "
                        "adviser. We will not and cannot be held liable for any actions you take as a result of "
                        "anything you read in the WSB Trackers."),
        html.P(className="legal-text",
               children="All information found here, including any ideas, opinions, views, predictions, forecasts, "
                        "commentaries, suggestions, or stock picks, expressed or implied herein, "
                        "are for informational, entertainment or educational purposes only and should not be "
                        "construed as personal investment advice. While the information provided is believed to be "
                        "accurate, it may include errors or inaccuracies."),
        html.P(className="legal-text",
               children="Conduct your own due diligence, or consult a licensed financial adviser or broker before "
                        "making any and all investment decisions. Any investments, trades, speculations, or decisions "
                        "made on the basis of any information found on this site, expressed or implied herein, "
                        "are committed at your own risk, financial or otherwise."),
    ]),
])


# control whether or not the industry selector will show based on the current option selected for stocks
@app.callback(
    Output(component_id="category_container", component_property="style"),
    Input(component_id="stock_selection", component_property="value"),
)
def handle_category_visiblity(selected_stock):
    # parse stock selection
    stock = StockSelection.from_value(selected_stock)
    if stock.is_top_n():
        # show industries when selecting top n stocks
        return dict(display="contents")
    else:
        # hide industries when selecting a single stock
        return dict(display="none")


# control primary function of app by reading current user selections and controlling figures
@app.callback(
    Output(component_id="trend_graph", component_property="figure"),
    Output(component_id="relative_trend_graph", component_property="figure"),
    Output(component_id="ranking_graph", component_property="figure"),
    Output(component_id="links_container", component_property="children"),
    Input(component_id="stock_selection", component_property="value"),
    Input(component_id="time_selection", component_property="value"),
    Input(component_id="category_selection", component_property="value"),
)
def handle_visible_data(selected_stock, selected_time, selected_category):
    # parse user stock selection
    stock = StockSelection.from_value(selected_stock)

    # reduce data to only selected stocks and time range
    results = index
    results = apply_ticker_filter(results, stock, selected_category)
    results = apply_time_filter(results, selected_time)

    # calculate total occurrences of resulting stock
    totals = results.groupby(results.symbol).occurrences.sum().sort_values(ascending=True)
    # reduce to desired amount if necessary
    if stock.is_top_n():
        totals = totals[-stock.top:]
    # get tickers from results
    result_tickers = [keyed_tickers[x] for x in totals.index]

    # create trend figure
    trend_fig = go.Figure()
    trend_fig.update_layout(
        xaxis_title="Time",
        yaxis_title="Number of Occurrences",
        legend=dict(
            traceorder="reversed",
            y=0.9,
        ),
        margin=dict(t=0),
    )

    # create relative trend graph
    rel_trend_fig = go.Figure()
    rel_trend_fig.update_layout(
        xaxis_title="Time",
        yaxis_title="Percentage of Occurrences",
        margin=dict(t=0),
        legend=dict(
            y=0.9,
        ),
    )

    # only show markers on trend graph when not too much data
    show_trend_markers = selected_time not in {"3month", "year", "all"}

    # add each ticker to the trend graphs
    for ticker in result_tickers:
        # filter to only this ticker
        trend = results[results.symbol == ticker.symbol]
        # reduce to a single series of occurrences indexed by date
        trend = trend.set_index(trend.date).occurrences
        # reindex the series so missing dates are filled with 0
        filled_dates = pd.date_range(results.date.min(), results.date.max(), freq="D")
        trend = trend.reindex(filled_dates, fill_value=0)
        # make line component and add to absolute graph
        trend_fig.add_trace(go.Scatter(
            x=trend.index,
            y=trend,
            mode="lines+markers" if show_trend_markers else "lines",
            line_shape="spline",
            name=ticker.symbol,
        ))
        # make line component and add to relative graph
        rel_trend_fig.add_trace(go.Scatter(
            x=trend.index,
            y=trend,
            mode="lines+markers",
            line_shape="spline",
            stackgroup="one",
            groupnorm="percent",
            name=ticker.symbol
        ))

    # create rank figure
    rank_fig = go.Figure()
    rank_fig.update_layout(
        xaxis_title="Total Number of Occurrences",
        yaxis_title="Stock",
        margin=dict(t=0),
    )
    rank_fig.add_trace(go.Bar(
        y=[f"({x.symbol}) {x.name}" for x in result_tickers],
        x=totals,
        orientation="h",
    ))

    # make link cells
    link_cells = [make_stock_link_cell(i + 1, x) for i, x in enumerate(result_tickers[::-1])]

    return trend_fig, rel_trend_fig, rank_fig, link_cells


if __name__ == "__main__":
    app.run_server(debug=True, dev_tools_hot_reload=True)
