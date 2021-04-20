import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objects as go
from utils.tickers import load_tickers
from utils.load import load_index
import typing as t
from utils.filters import StockSelection, TimeSelection


# =========
# DATA LOAD
# =========


tickers = load_tickers("NYSE", "NASDAQ")
keyed_tickers = {x.symbol: x for x in tickers}
index = load_index("compiled_index_min10")


# =======
# FILTERS
# =======


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
        # apply filter
        results = results[results.symbol.isin(x.symbol for x in f)]
    return results


def apply_time_filter(results: pd.DataFrame, time_selection: str):
    selection = TimeSelection.from_value(time_selection)
    if selection.min_date is not None:
        results = results[results.date >= pd.to_datetime(selection.min_date)]
    return results


# ===============
# BASE COMPONENTS
# ===============


def make_stock_dropdown():
    options = []
    # add top options
    for n in [1, 2, 5, 10, 20]:
        options.append(dict(
            label=f"the top {n} stocks",
            value=StockSelection(top=n).value(),
        ))
    # add symbol options
    for ticker in tickers:
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


def make_category_dropdown():
    # find unique categories given all tickers
    unique_sectors = set(ticker.sector for ticker in tickers)
    options = [
        dict(label="All Industries", value="all"),
    ]
    # add each unique category
    for x in unique_sectors:
        if x is not None:
            options.append(dict(label=x, value=f"{x}"))
    return dcc.Dropdown(
        id="category_selection",
        options=options,
        value="all",
        placeholder="Select industry",
        clearable=False,
    )


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

    # graphs
    html.Div(className="graphs", children=[
        dcc.Graph(id="trend_graph"),
        dcc.Graph(id="relative_trend_graph"),
        dcc.Graph(id="ranking_graph"),
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


@app.callback(
    Output(component_id="category_container", component_property="style"),
    Input(component_id="stock_selection", component_property="value"),
)
def handle_category_visiblity(selected_stock):
    stock = StockSelection.from_value(selected_stock)
    if stock.is_top_n():
        # show for selecting top n stocks
        return dict(display="contents")
    else:
        # hide for selecting single stocks
        return dict(display="none")


@app.callback(
    Output(component_id="trend_graph", component_property="figure"),
    Output(component_id="relative_trend_graph", component_property="figure"),
    Output(component_id="ranking_graph", component_property="figure"),
    Input(component_id="stock_selection", component_property="value"),
    Input(component_id="time_selection", component_property="value"),
    Input(component_id="category_selection", component_property="value"),
)
def handle_visible_data(selected_stock, selected_time, selected_category):
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
        title="Stock Symbol Frequency",
        xaxis_title="Time",
        yaxis_title="Number of Occurrences",
        legend=dict(
            traceorder="reversed",
        ),
    )

    # create relative trend graph
    rel_trend_fig = go.Figure()
    rel_trend_fig.update_layout(
        title="Relative Stock Symbol Frequency",
        xaxis_title="Time",
        yaxis_title="Percentage of Messages",
    )

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
            mode="lines+markers",
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
        title="Stock Rankings",
        xaxis_title="Total Number of Occurrences",
        yaxis_title="Stock",
    )
    rank_fig.add_trace(go.Bar(
        y=[f"({x.symbol}) {x.name}" for x in result_tickers],
        x=totals,
        orientation="h",
    ))

    return trend_fig, rel_trend_fig, rank_fig


if __name__ == "__main__":
    app.run_server(debug=True, dev_tools_hot_reload=True)
