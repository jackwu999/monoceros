from pathlib import Path
from plotly import graph_objects as go
import pandas as pd
import pandas_ta as ta
from collections import defaultdict
from plotly.subplots import make_subplots

from dash import Dash, Input, Output, State, dash_table
from layout import LAYOUT

DATA_DIR = "../DATA/"
PALETTE = {
    "bg_color": "#ffffff",
    "plot_bg_color": "#ffffff",
    "grid_color": "#e6e6e6",
    "text_color": "#2e2e2e",
    "dark_candle": "#84dc58",
    "light_candle": "#ec3a11",
    "volume_color": "#d32e48",
    "border_color": "#2e2e2e",
    "color_1": "#3eb863",
    "color_2": "#bf3fd8",
    "color_3": "#ffc900",
    "color_4": "#6401d1",
    "color_5": "#ff7f50",
    "color_6": "#f26841",
    "color_7": "#fd862b",
    "color_8": "#ffa600",
    "color_9": "#3366d6",
}


class ResearchTool:
    def __init__(self, symbols):
        self.symbols = symbols
        self.dfs = defaultdict(dict)

    def load_symbol_data(self, symbol):
        data_dir = Path(DATA_DIR + symbol)
        df = pd.concat(
            pd.read_parquet(parquet_file, engine="fastparquet")
            for parquet_file in data_dir.glob("*.parquet")
        )
        df.dropna(inplace=True)
        df["date"] = pd.to_datetime(df.index)
        df.set_index("date", inplace=True)

        self.dfs[symbol]["1MIN"] = df
        self.dfs[symbol]["15MIN"] = df.resample("15min").agg(ta.CANGLE_AGG).copy()
        self.dfs[symbol]["1H"] = df.resample("1h").agg(ta.CANGLE_AGG).copy()
        self.dfs[symbol]["1D"] = df.resample("1d").agg(ta.CANGLE_AGG).copy()
        self.dfs[symbol]["1M"] = df.resample("1m").agg(ta.CANGLE_AGG).copy()

        self.dfs[symbol]["15MIN"]["date"] = pd.to_datetime(
            self.dfs[symbol]["15MIN"].index
        )
        self.dfs[symbol]["1H"]["date"] = pd.to_datetime(self.dfs[symbol]["1H"].index)
        self.dfs[symbol]["1D"]["date"] = pd.to_datetime(self.dfs[symbol]["1D"].index)
        self.dfs[symbol]["1M"]["date"] = pd.to_datetime(self.dfs[symbol]["1M"].index)

    def load_all_data(self):
        for symbol in self.symbols:
            self.load_symbol_data(symbol)

    def plot_sma_signals(self, smas, fig, df):
        for i in range(len(smas)):
            sma = smas[i]
            if sma != 0:
                sma_col = "sma_{}".format(sma)
                if sma_col not in df.columns:
                    df[sma_col] = ta.sma(df["close"], length=sma)
                color = "color_{}".format(i + 1)
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df[sma_col],
                        line=dict(color=PALETTE[color], width=2),
                        name=sma_col,
                    ),
                    row=1,
                    col=1,
                )

    def plot_chart(self, symbol, granularity, smas):
        df = self.dfs[symbol][granularity]

        #  Create sub plots
        fig = make_subplots(
            rows=4,
            cols=1,
            subplot_titles=[f"{symbol}", "", "", "Volume"],
            specs=[
                [{"rowspan": 3, "secondary_y": True}],
                [{"secondary_y": True}],
                [{"secondary_y": True}],
                [{"secondary_y": True}],
            ],
            vertical_spacing=0.04,
            shared_xaxes=True,
        )
        #  Plot close price
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df["open"],
                close=df["close"],
                low=df["low"],
                high=df["high"],
                increasing_line_color=PALETTE["light_candle"],
                decreasing_line_color=PALETTE["dark_candle"],
                name="Price",
            ),
            row=1,
            col=1,
        )

        # Plot SMA signals
        self.plot_sma_signals(smas, fig, df)

        #  Volume Histogram
        fig.add_trace(
            go.Bar(
                name="Volume",
                x=df.index,
                y=df["volume"],
                marker_color=PALETTE["volume_color"],
            ),
            row=4,
            col=1,
        )

        fig.update_layout(
            title={"text": "", "x": 0.5},
            font=dict(family="Verdana", size=12, color=PALETTE["text_color"]),
            autosize=True,
            width=1280,
            height=1000,
            xaxis={"rangeslider": {"visible": False}},
            plot_bgcolor=PALETTE["plot_bg_color"],
            paper_bgcolor=PALETTE["bg_color"],
            uirevision=True,
        )
        fig.update_yaxes(visible=False, secondary_y=True, autorange=True)
        
        #  Change grid color
        fig.update_xaxes(
            showline=True,
            linewidth=1,
            linecolor=PALETTE["grid_color"],
            gridcolor=PALETTE["grid_color"],
        )
        fig.update_yaxes(
            showline=True,
            linewidth=1,
            linecolor=PALETTE["grid_color"],
            gridcolor=PALETTE["grid_color"],
            fixedrange=False,
        )

        return fig

    def query(
        self,
        symbols,
        granularity,
        equality,
        condition_1_type,
        condition_1_value,
        condition_2_type,
        condition_2_value,
    ):
        res = None
        for symbol in symbols:
            df = self.dfs[symbol][granularity]
            if condition_1_type == "SMA" and condition_2_type == "SMA":
                sma_1_col = "sma_{}".format(condition_1_value)
                sma_2_col = "sma_{}".format(condition_2_value)
                if sma_1_col not in df.columns:
                    df[sma_1_col] = ta.sma(df["close"], length=condition_1_value)
                if sma_2_col not in df.columns:
                    df[sma_2_col] = ta.sma(df["close"], length=condition_2_value)

                if equality == ">":
                    new_df = df.loc[df[sma_1_col] > df[sma_2_col]].copy()
                elif equality == "<":
                    new_df = df.loc[df[sma_1_col] < df[sma_2_col]].copy()
                else:
                    new_df = df.loc[df[sma_1_col] == df[sma_2_col]].copy()
                new_df["symbol"] = symbol
                new_df = new_df[
                    [
                        "date",
                        "symbol",
                        "open",
                        "high",
                        "low",
                        "close",
                        "volume",
                        sma_1_col,
                        sma_2_col,
                    ]
                ]
                if res is None:
                    res = new_df
                else:
                    res = pd.concat([res, new_df])
        return self.get_query_table(res)

    def get_query_table(self, df):
        fig = dash_table.DataTable(
            df.to_dict("records"), [{"name": i, "id": i} for i in df.columns]
        )
        return fig


if __name__ == "__main__":
    symbols = ["btcusdt", "dogeusdt", "ethusdt", "solusdt"]
    rt = ResearchTool(symbols)
    rt.load_all_data()
    #  Run Dash server
    app = Dash(__name__)
    app.layout = LAYOUT

    @app.callback(
        Output("graph", "figure"),
        Input("symbol", "value"),
        Input("granularity", "value"),
        Input("sma1_switch", "value"),
        Input("sma2_switch", "value"),
        Input("sma3_switch", "value"),
        Input("sma4_switch", "value"),
        Input("sma5_switch", "value"),
        Input("sma_1", "value"),
        Input("sma_2", "value"),
        Input("sma_3", "value"),
        Input("sma_4", "value"),
        Input("sma_5", "value"),
    )
    def display_graph(
        symbol,
        granularity,
        sma1_switch,
        sma2_switch,
        sma3_switch,
        sma4_switch,
        sma5_switch,
        sma_1,
        sma_2,
        sma_3,
        sma_4,
        sma_5,
    ):
        smas = [sma_1, sma_2, sma_3, sma_4, sma_5]
        smas_switches = [
            sma1_switch,
            sma2_switch,
            sma3_switch,
            sma4_switch,
            sma5_switch,
        ]
        print(smas)
        for i in range(len(smas)):
            if len(smas_switches[i]) == 0 or smas[i] is None or smas[i] < 2:
                smas[i] = 0
        fig = rt.plot_chart(symbol, granularity, smas)
        return fig

    @app.callback(
        Output("query_table", "children"),
        Input("query", "n_submit"),
        State("asset_1", "value"),
        State("asset_2", "value"),
        State("asset_3", "value"),
        State("asset_4", "value"),
        State("query_granularity", "value"),
        State("condition_1_type", "value"),
        State("condition_1_value", "value"),
        State("condition_equality", "value"),
        State("condition_2_type", "value"),
        State("condition_2_value", "value"),
        prevent_initial_call=True,
    )
    def handle_submit(
        n_submit,
        asset_1,
        asset_2,
        asset_3,
        asset_4,
        granularity,
        condition_1_type,
        condition_1_value,
        equality,
        condition_2_type,
        condition_2_value,
    ):
        symbols = []
        for option in [asset_1, asset_2, asset_3, asset_4]:
            symbols += option

        if (
            (condition_1_value is not None)
            and (condition_1_value is not None)
            and (2 <= int(condition_1_value))
            and (2 <= int(condition_2_value))
        ):
            fig = rt.query(
                symbols,
                granularity,
                equality,
                condition_1_type,
                int(condition_1_value),
                condition_2_type,
                int(condition_2_value),
            )
            return fig

    app.run_server(debug=True)
