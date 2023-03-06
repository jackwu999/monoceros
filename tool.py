from pathlib import Path
from plotly import graph_objects as go
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import numpy as np
from collections import defaultdict
from plotly.subplots import make_subplots

from dash import Dash, dcc, html, Input, Output, State, dash_table
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
        self.dfs[symbol]["15MIN"] = df.resample("15min").agg(ta.CANGLE_AGG).copy()
        self.dfs[symbol]["1H"] = df.resample("1h").agg(ta.CANGLE_AGG).copy()
        self.dfs[symbol]["1D"] = df.resample("1d").agg(ta.CANGLE_AGG).copy()
        self.dfs[symbol]["1M"] = df.resample("1m").agg(ta.CANGLE_AGG).copy()
        
        self.dfs[symbol]["15MIN"]['date'] = pd.to_datetime(self.dfs[symbol]["15MIN"].index)
        self.dfs[symbol]["1H"]['date'] = pd.to_datetime(self.dfs[symbol]["1H"].index)
        self.dfs[symbol]["1D"]['date'] = pd.to_datetime(self.dfs[symbol]["1D"].index)
        self.dfs[symbol]["1M"]['date'] = pd.to_datetime(self.dfs[symbol]["1M"].index)
        
    
    
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
                paper_bgcolor=palette["bg_color"],
                uirevision=True)
        fig.update_yaxes(visible=False, secondary_y=True, autorange=True)
        #  Change grid color
        fig.update_xaxes(showline=True, linewidth=1, linecolor=palette["grid_color"],gridcolor=palette["grid_color"])
        fig.update_yaxes(showline=True, linewidth=1, linecolor=palette["grid_color"],gridcolor=palette["grid_color"],fixedrange=False)
        #  Create output file
        #file_name = f"{symbol}_chart.png"
        #fig.write_image(file_name, format="png")
        return fig
    
    def query(self, symbols, granularity, equality, condition_1_type, condition_1_value, condition_2_type, condition_2_value):
        res = None
        for symbol in symbols:
            df = self.dfs[symbol][granularity]
            if condition_1_type == "SMA" and condition_2_type == "SMA":
                sma_1_col = "sma_{}".format(condition_1_value)
                sma_2_col = "sma_{}".format(condition_2_value)
                if sma_1_col not in df.columns:
                    df[sma_1_col] = ta.sma(df['close'], length=condition_1_value)
                if sma_2_col not in df.columns:
                    df[sma_2_col] = ta.sma(df['close'], length=condition_2_value)
                
                if equality == ">":
                    new_df = df.loc[df[sma_1_col] > df[sma_2_col]].copy()
                elif equality == "<":
                    new_df = df.loc[df[sma_1_col] < df[sma_2_col]].copy()
                else:
                    new_df = df.loc[df[sma_1_col] == df[sma_2_col]].copy()
                new_df["symbol"] = symbol
                new_df = new_df[["date", "symbol", 'open', 'high', 'low', 'close','volume', sma_1_col, sma_2_col]]
                if res is None:
                    res = new_df
                else:
                    res = pd.concat([res, new_df])
        return self.get_query_table(res)

    def get_query_table(self, df):
        fig = dash_table.DataTable(df.to_dict('records'), [{"name": i, "id": i} for i in df.columns])
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
            style = {'display':'inline-block', "width":'80px'}
            ),
            dcc.Input(
                id="sma_1", type="number",
                debounce=True, placeholder="value",
                min=2,
                style = {'display':'inline-block', 'margin-right':'20px','margin-left':'10px', "width":'80px'}
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
            style = {'display':'inline-block', "width":'80px'}
            ),
            dcc.Input(
                id="sma_2", type="number",
                debounce=True, placeholder="value",
                min=2,
                style = {'display':'inline-block', 'margin-right':'20px','margin-left':'10px', "width":'80px'}
            ),
        ]),
        html.Span([
            dbc.Checklist(
            options=[
                {"label": "SMA3", "value": 1},
            ],
            value=[],
            id="sma3_switch",
            switch=True,
            inline=True,
            style = {'display':'inline-block', "width":'80px'}
            ),
            dcc.Input(
                id="sma_3", type="number",
                debounce=True, placeholder="value",
                min=2,
                style = {'display':'inline-block', 'margin-right':'20px','margin-left':'10px', "width":'80px'}
            ),
        ]),
        
        html.Span([
            dbc.Checklist(
            options=[
                {"label": "SMA4", "value": 1},
            ],
            value=[],
            id="sma4_switch",
            switch=True,
            inline=True,
            style = {'display':'inline-block', "width":'80px'}
            ),
            dcc.Input(
                id="sma_4", type="number",
                debounce=True, placeholder="value",
                min=2,
                style = {'display':'inline-block', 'margin-right':'20px','margin-left':'10px', "width":'80px'}
            ),
        ]),
        
        html.Span([
            dbc.Checklist(
            options=[
                {"label": "SMA5", "value": 1},
            ],
            value=[],
            id="sma5_switch",
            switch=True,
            inline=True,
            style = {'display':'inline-block', "width":'80px'}
            ),
            dcc.Input(
                id="sma_5", type="number",
                debounce=True, placeholder="value",
                min=2,
                style = {'display':'inline-block', 'margin-right':'20px','margin-left':'10px', "width":'80px'}
            ),
        ]),
        
        
        dcc.Graph(id="graph"),
        
        html.H2('Query'),
       
        dbc.Form(
            id="query",
            children =[
                dbc.Row([
                    dbc.Label("Assets:  "),
                    dbc.Checklist(
                        options=[
                            {"label": "BTC", "value": "btcusdt"},   
                                      
                        ],
                        value=["btcusdt"],
                        id="asset_1",
                        inline=True,
                        style = {'display':'inline-block', "width":'100px'}
                    ),
                    dbc.Checklist(
                        options=[
                            {"label": "DOGE", "value": "dogeusdt"},              
                        ],
                        value=[],
                        id="asset_2",
                        inline=True,
                        style = {'display':'inline-block', "width":'140px'}
                    ),
                    dbc.Checklist(
                        options=[
                            {"label": "ETH", "value": "ethusdt"},              
                        ],
                        value=[],
                        id="asset_3",
                        inline=True,
                        style = {'display':'inline-block', "width":'100px'}
                    ),
                    dbc.Checklist(
                        options=[
                            {"label": "SOL", "value": "solusdt"},              
                        ],
                        value=[],
                        id="asset_4",
                        inline=True,
                        style = {'display':'inline-block', "width":'100px'}
                    ),
                ]),
                dbc.Row([
                    dbc.Label("Granularity:  ", style = {"vertical-align": "middle"}),
                    dcc.Dropdown(
                        id="query_granularity",
                        options=["1MIN", "15MIN", "1H", "1D", "1M"],
                        value="1D",
                        clearable=False,
                        style = {'display':'inline-block', "width":'80px', "vertical-align": "middle"}
                    ),
                ])
                ,
                dbc.Row([
                    dbc.Label("Condition:  ", style = {"vertical-align": "middle"}),
                    dcc.Dropdown(
                        id="condition_1_type",
                        options=["SMA"],
                        value="SMA",
                        clearable=False,
                        style = {'display':'inline-block', "width":'80px', "vertical-align": "middle", "height":"30px"}
                    ),
                    dcc.Input(
                        id="condition_1_value", type="number",
                        debounce=True, placeholder="value",
                        min=2,
                        style = {'display':'inline-block', 'margin-right':'0px','margin-left':'0px', "width":'60px', "height":"22px"}
                    ),
                    dcc.Dropdown(
                        id="condition_equality",
                        options=[">", "=", "<"],
                        value=">",
                        clearable=False,
                        style = {'display':'inline-block', "width":'50px', "vertical-align": "middle", "height":"30px",  'margin-left':'10px', 'margin-right':'10px'}
                    ),
                    dcc.Dropdown(
                        id="condition_2_type",
                        options=["SMA"],
                        value="SMA",
                        clearable=False,
                        style = {'display':'inline-block', "width":'80px',  'margin-left':'10px', "vertical-align": "middle", "height":"30px"}
                    ),
                    dcc.Input(
                        id="condition_2_value", type="number",
                        debounce=True, placeholder="value",
                        min=2,
                        style = {'display':'inline-block','margin-left':'10px', "width":'60px', "height":"21px"}
                    ),
                ]),
                dbc.Button("Submit", color="primary"),
            ]
            
        ),
        html.Div(id="query_table")
    ])
    
    @app.callback(
        Output("graph", "figure"),
        Input("symbol", "value"),
        Input("granularity", "value"),
        [
            Input("sma1_switch", "value"),
            Input("sma2_switch", "value"),
            Input("sma3_switch", "value"),
            Input("sma4_switch", "value"),
            Input("sma5_switch", "value"),
        ],
        [
            Input("sma_1", "value"),
            Input("sma_2", "value"),
            Input("sma_3", "value"),
            Input("sma_4", "value"),
            Input("sma_5", "value"),
        ],
        
       )
    def display_graph(symbol, granularity, sma1_switch, sma2_switch, sma3_switch, sma4_switch, sma5_switch,
                      sma_1, sma_2, sma_3, sma_4, sma_5):
        smas = [0] * 5
        
        if sma1_switch and sma_1 is not None and sma_1>=2:
            smas[0] = sma_1
        if sma2_switch and sma_2 is not None and sma_2>=2:
            smas[1] = sma_2
        if sma3_switch and sma_3 is not None and sma_3>=2:
            smas[2] = sma_3
        if sma4_switch and sma_4 is not None and sma_4>=2:
            smas[3] = sma_4
        if sma5_switch and sma_5 is not None and sma_5>=2:
            smas[4] = sma_5
        
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
    State("condition_equality","value"),
    State("condition_2_type", "value"),
    State("condition_2_value", "value"),
    prevent_initial_call=True
    )
    def handle_submit(n_submit, asset_1, asset_2, asset_3, asset_4, granularity, 
                      condition_1_type, condition_1_value,equality, condition_2_type, condition_2_value):

        symbols = []
        for option in [asset_1, asset_2, asset_3, asset_4]:
            symbols += option
        print(symbols)
        if ((condition_1_value is not None) and ( condition_1_value is not None) and
            (2 <= int(condition_1_value)) and (2 <= int(condition_2_value))):
            fig = rt.query( symbols, granularity, equality, condition_1_type, int(condition_1_value), condition_2_type, int(condition_2_value))
            return fig
    
    app.run_server(debug=True)

