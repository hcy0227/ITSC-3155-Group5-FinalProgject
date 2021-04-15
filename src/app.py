import dash
import dash_html_components as html
import dash_core_components as dcc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import numpy as np


def load_data(path: Path):
    df = pd.read_csv(path, parse_dates=["timestamp"])
    df.sort_values("timestamp", inplace=True)
    df.body = df.body.str.upper().str.replace("[^a-zA-Z\s]", "", regex=True)
    df["occurances_gme"] = df.body.str.count(" AMC ")
    # df.groupby(df.timestamp.dt.date)

    df = df.groupby(df.timestamp.dt.date).sum()
    all_dates = pd.date_range(df.index.min(), df.index.max())
    df = df.reindex(all_dates, fill_value=0)
    print(df)
    fig = px.line(x=df.index, y=df.occurances_gme, title="GME over time")
    # fig.show()


def make_stock_dropdown_option(company, ticker):
    return dict(
        label=f"{company} ({ticker})",
        value=f"single|{ticker}",
    )



def make_fake_trend_fig():
    fig = go.Figure()
    fig.update_layout(
        title="Message Frequency",
        xaxis_title="Time",
        yaxis_title="Number of Messages",
    )
    x = np.linspace(0, 1000, 1000)
    fig.add_trace(go.Scatter(x=x, y=x * 0.5 + 10, mode="lines", name="A"))
    fig.add_trace(go.Scatter(x=x, y=x * 0.8 - 100, mode="lines", name="B"))
    fig.add_trace(go.Scatter(x=x, y=(x / 100) ** 0.5 * 300, mode="lines", name="C"))
    return fig

def make_fake_ranking_fig():
    fig = go.Figure()
    fig.update_layout(
        title="Stock Rankings",
        xaxis_title="Stock",
        yaxis_title="Total Number of Messages",
    )
    stocks = ["GameStop (GME)", "Amazon (AMZN)", "Apple (APPL)", "AMC Theaters (AMC)"]

    fig.add_trace(go.Bar(
        y=stocks,
        x=sorted([6500, 400, 500, 2000]),
        orientation="h",
    ))

    # x = np.linspace(0, 1000, 1000)
    # fig.add_trace(go.Scatter(x=x, y=x * 0.5 + 10, mode="lines", name="A"))
    # fig.add_trace(go.Scatter(x=x, y=x * 0.8 - 100, mode="lines", name="B"))
    # fig.add_trace(go.Scatter(x=x, y=(x / 100) ** 0.5 * 300, mode="lines", name="C"))
    return fig



app = dash.Dash("WallStreetBets Tracker")

app.layout = html.Div([
    # header
    html.Div(className="header", children=[
        html.H1("WallStreetBets Tracker"),
    ]),

    # controls
    html.Div(className="controls", children=[
        html.Span("Show me"),
        dcc.Dropdown(
            id="stock_selection",
            options=[
                dict(label="the top 1 stocks", value="top|1"),
                dict(label="the top 2 stocks", value="top|2"),
                dict(label="the top 5 stocks", value="top|5"),
                dict(label="the top 10 stocks", value="top|10"),
                dict(label="the top 20 stocks", value="top|20"),
                make_stock_dropdown_option("GameStop", "GME"),
                make_stock_dropdown_option("Amazon", "AMZN"),
                make_stock_dropdown_option("Apple", "AAPL"),
            ],
            value="top|5",
            placeholder="Select stocks",
        ),
        html.Span("for"),
        dcc.Dropdown(
            id="time_selection",
            options=[
                dict(label="this week", value="week"),
                dict(label="this month", value="month"),
                dict(label="this year", value="year"),
                dict(label="all time", value="all"),
            ],
            value="week",
            placeholder="Select time frame",
        ),
        html.Span("in"),
        dcc.Dropdown(
            id="category_selection",
            options=[
                dict(label="All Industries", value="all"),
                dict(label="Technology", value="technology"),
                dict(label="Transportation", value="transportation"),
                dict(label="Retail", value="retail"),
            ],
            value="all",
            placeholder="Select industry",
        ),
    ]),

    # graphs
    html.Div(className="graphs", children=[
        dcc.Graph(id="trend_graph", figure=make_fake_trend_fig()),
        dcc.Graph(id="ranking_graph", figure=make_fake_ranking_fig()),
    ]),


    # disclaimer
    html.Div(className="footer", children=[
        html.H2("Disclaimer"),
        html.P(className="legal-text", children="We do not provide personal investment advice and We are not a qualified licensed investment advisor. We will not and cannot be held liable for any actions you take as a result of anything you read in the WSB Trackers."),
        html.P(className="legal-text", children="All information found here, including any ideas, opinions, views, predictions, forecasts, commentaries, suggestions, or stock picks, expressed or implied herein, are for informational, entertainment or educational purposes only and should not be construed as personal investment advice. While the information provided is believed to be accurate, it may include errors or inaccuracies."),
        html.P(className="legal-text", children="Conduct your own due diligence, or consult a licensed financial advisor or broker before making any and all investment decisions. Any investments, trades, speculations, or decisions made on the basis of any information found on this site, expressed or implied herein, are committed at your own risk, financial or otherwise."),
    ]),
])



# def main():
    # print("main()")
    # load_data("../data/reddit_wsb.csv")

if __name__ == "__main__":
    # main()
    app.run_server(debug=True, dev_tools_hot_reload=True)