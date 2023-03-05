from pathlib import Path
from plotly import graph_objects as go
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import numpy as np
from collections import defaultdict
from plotly.subplots import make_subplots

from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc

DATA_DIR = '../DATA/'

class ResearchTool():
    def __init__(self, symbols):
        self.symbols = symbols
        self.dfs = defaultdict(dict)
        

    def load_symbol_data(self, symbol):
        data_dir = Path(DATA_DIR  + symbol)
        df = pd.concat(
            pd.read_parquet(parquet_file, engine='fastparquet')
            for parquet_file in data_dir.glob('*.parquet')
        )
        df.dropna(inplace=True)
        df['date'] = pd.to_datetime(df.index)
        df.set_index("date", inplace=True)
        #df = df.iloc[10:190]
      
        self.dfs[symbol]["1MIN"] = df
        self.dfs[symbol]["15MIN"] = df.resample("15min").agg(ta.CANGLE_AGG)
        self.dfs[symbol]["1H"] = df.resample("1h").agg(ta.CANGLE_AGG)
        self.dfs[symbol]["1D"] = df.resample("1d").agg(ta.CANGLE_AGG)
        self.dfs[symbol]["1M"] = df.resample("1m").agg(ta.CANGLE_AGG)
        
    
    
    def load_all_data(self):
        for symbol in self.symbols:
            df = self.load_symbol_data(symbol)
    
        
    def plot_chart(self, symbol, granularity, smas):
        df = self.dfs[symbol][granularity]
        
        
        
        palette = {"bg_color":"#ffffff", "plot_bg_color": "#ffffff", "grid_color":"#e6e6e6",
                        "text_color":"#2e2e2e","dark_candle":"#4d98c4","light_candle":"#b1b7ba", 
                        "volume_color":"#c74e96","border_color":"#2e2e2e",
                        "color_1":"#5c285b","color_2":"#802c62","color_3":"#a33262","color_4":"#c43d5c",
                        "color_5":"#de4f51", "color_6":"#f26841", "color_7":"#fd862b",
                        "color_8":"#ffa600", "color_9":"#3366d6"}
        
        #  Create sub plots
        fig = make_subplots(rows=4, cols=1, subplot_titles=[f"{symbol} Chart", '', '', 'Volume'], \
                            specs=[[{"rowspan": 3, "secondary_y": True}], [{"secondary_y": True}], [{"secondary_y": True}],
                                [{"secondary_y": True}]], \
                            vertical_spacing=0.04, shared_xaxes=True)
        #  Plot close price
        
        
        fig.add_trace(go.Candlestick(x=df.index,
                                    open=df['open'],
                                    close=df['close'],
                                    low=df['low'],
                                    high=df['high'],
                                    increasing_line_color=palette['light_candle'], 
                                    decreasing_line_color=palette['dark_candle'], 
                                    name='Price')
                        , row=1, col=1)
        
        for i in range(len(smas)):
            sma = smas[i]
            if sma != 0:
                sma_col = "sma_{}".format(sma)
                if sma_col not in df.columns:
                    df[sma_col] = ta.sma(df['close'], length=sma)
                color = "color_{}".format(i + 1)
                fig.add_trace(go.Scatter(x=df.index, y=df[sma_col], line=dict(color=palette[color], width=1), name=sma_col),
                        row=1, col=1)
      
        
        #  Volume Histogram
        fig.add_trace(go.Bar(
            name='Volume',
            x=df.index, y=df['volume'], marker_color=palette['volume_color']), row=4,col=1)
        fig.update_layout(
                title={'text': '', 'x': 0.5},
                font=dict(family="Verdana", size=12, color=palette["text_color"]),
                autosize=True,
                width=1280, height=1000,
                xaxis={
                        'rangeslider': {'visible':True}
                    },
                plot_bgcolor=palette["plot_bg_color"],
                paper_bgcolor=palette["bg_color"])
        fig.update_yaxes(visible=False, secondary_y=True, autorange=True)
        #  Change grid color
        fig.update_xaxes(showline=True, linewidth=1, linecolor=palette["grid_color"],gridcolor=palette["grid_color"])
        fig.update_yaxes(showline=True, linewidth=1, linecolor=palette["grid_color"],gridcolor=palette["grid_color"],fixedrange=False)
        #  Create output file
        #file_name = f"{symbol}_chart.png"
        #fig.write_image(file_name, format="png")
        return fig


if __name__ == '__main__':
    #symbols = ["btcusdt"]
    symbols = ["btcusdt", "dogeusdt", "ethusdt", "solusdt"]
    rt = ResearchTool(symbols)
    rt.load_all_data()
    #  Run Dash server
    app = Dash(__name__)
    app.layout = html.Div([
        html.H2('Monoceros'),
        html.P("Select symbol:"),
        dcc.Dropdown(
            id="symbol",
            options=symbols,
            value="btcusdt",
            clearable=False,
        ),
        html.P("Select Granularity:"),
        dcc.Dropdown(
            id="granularity",
            options=["1MIN", "15MIN", "1H", "1D", "1M"],
            value="1D",
            clearable=False,
        ),
        html.P("Add SMAs:"),
        
        html.Span([
            dbc.Checklist(
            options=[
                {"label": "SMA1", "value": 1},
            ],
            value=[],
            id="sma1_switch",
            switch=True,
            inline=True,
            style = {'display':'inline-block', "width":'7%'}
            ),
            dcc.Input(
                id="sma_1", type="number",
                debounce=True, placeholder="20",
                min=2,
                style = {'display':'inline-block', 'margin-right':'20px','margin-left':'10px', "width":'10%'}
            ),
        ]),
        html.Span([
            dbc.Checklist(
            options=[
                {"label": "SMA2", "value": 1},
            ],
            value=[],
            id="sma2_switch",
            switch=True,
            inline=True,
            style = {'display':'inline-block', "width":'7%'}
            ),
            dcc.Input(
                id="sma_2", type="number",
                debounce=True, placeholder="20",
                min=2,
                style = {'display':'inline-block', 'margin-right':'20px','margin-left':'10px', "width":'10%'}
            ),
        ]),
        dcc.Graph(id="graph"),
    ],)
    
    @app.callback(
        Output("graph", "figure"),
        Input("symbol", "value"),
        Input("granularity", "value"),
        [
            Input("sma1_switch", "value"),
            Input("sma2_switch", "value"),
        ],
        [
            Input("sma_1", "value"),
            Input("sma_2", "value"),
        ],
       )
    def display_graph(symbol, granularity, sma1_switch, sma2_switch, sma_1, sma_2):
        smas = [0] * 2
       
        if sma1_switch and sma_1 is not None and sma_1>=2:
            smas[0] = sma_1
        if sma2_switch and sma_2 is not None and sma_2>=2:
            smas[1] = sma_2
            
        fig = rt.plot_chart(symbol, granularity, smas)
        return fig
    app.run_server(debug=True)
