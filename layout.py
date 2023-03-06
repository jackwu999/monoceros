from dash import dcc, html
import dash_bootstrap_components as dbc


LAYOUT = html.Div(
        [
            html.H2("Monoceros"),
            html.P("Select symbol:"),
            dcc.Dropdown(
                id="symbol",
                options=["btcusdt", "dogeusdt", "ethusdt", "solusdt"],
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
            html.Span(
                [
                    dbc.Checklist(
                        options=[
                            {"label": "SMA1", "value": 1},
                        ],
                        value=[],
                        id="sma1_switch",
                        switch=True,
                        inline=True,
                        style={"display": "inline-block", "width": "80px"},
                    ),
                    dcc.Input(
                        id="sma_1",
                        type="number",
                        debounce=True,
                        placeholder="value",
                        min=2,
                        style={
                            "display": "inline-block",
                            "margin-right": "20px",
                            "margin-left": "10px",
                            "width": "80px",
                        },
                    ),
                ]
            ),
            html.Span(
                [
                    dbc.Checklist(
                        options=[
                            {"label": "SMA2", "value": 1},
                        ],
                        value=[],
                        id="sma2_switch",
                        switch=True,
                        inline=True,
                        style={"display": "inline-block", "width": "80px"},
                    ),
                    dcc.Input(
                        id="sma_2",
                        type="number",
                        debounce=True,
                        placeholder="value",
                        min=2,
                        style={
                            "display": "inline-block",
                            "margin-right": "20px",
                            "margin-left": "10px",
                            "width": "80px",
                        },
                    ),
                ]
            ),
            html.Span(
                [
                    dbc.Checklist(
                        options=[
                            {"label": "SMA3", "value": 1},
                        ],
                        value=[],
                        id="sma3_switch",
                        switch=True,
                        inline=True,
                        style={"display": "inline-block", "width": "80px"},
                    ),
                    dcc.Input(
                        id="sma_3",
                        type="number",
                        debounce=True,
                        placeholder="value",
                        min=2,
                        style={
                            "display": "inline-block",
                            "margin-right": "20px",
                            "margin-left": "10px",
                            "width": "80px",
                        },
                    ),
                ]
            ),
            html.Span(
                [
                    dbc.Checklist(
                        options=[
                            {"label": "SMA4", "value": 1},
                        ],
                        value=[],
                        id="sma4_switch",
                        switch=True,
                        inline=True,
                        style={"display": "inline-block", "width": "80px"},
                    ),
                    dcc.Input(
                        id="sma_4",
                        type="number",
                        debounce=True,
                        placeholder="value",
                        min=2,
                        style={
                            "display": "inline-block",
                            "margin-right": "20px",
                            "margin-left": "10px",
                            "width": "80px",
                        },
                    ),
                ]
            ),
            html.Span(
                [
                    dbc.Checklist(
                        options=[
                            {"label": "SMA5", "value": 1},
                        ],
                        value=[],
                        id="sma5_switch",
                        switch=True,
                        inline=True,
                        style={"display": "inline-block", "width": "80px"},
                    ),
                    dcc.Input(
                        id="sma_5",
                        type="number",
                        debounce=True,
                        placeholder="value",
                        min=2,
                        style={
                            "display": "inline-block",
                            "margin-right": "20px",
                            "margin-left": "10px",
                            "width": "80px",
                        },
                    ),
                ]
            ),
            dcc.Graph(id="graph"),
            html.H2("Query"),
            dbc.Form(
                id="query",
                children=[
                    dbc.Row(
                        [
                            dbc.Label("Assets:  "),
                            dbc.Checklist(
                                options=[
                                    {"label": "BTC", "value": "btcusdt"},
                                ],
                                value=["btcusdt"],
                                id="asset_1",
                                inline=True,
                                style={"display": "inline-block", "width": "100px"},
                            ),
                            dbc.Checklist(
                                options=[
                                    {"label": "DOGE", "value": "dogeusdt"},
                                ],
                                value=[],
                                id="asset_2",
                                inline=True,
                                style={"display": "inline-block", "width": "140px"},
                            ),
                            dbc.Checklist(
                                options=[
                                    {"label": "ETH", "value": "ethusdt"},
                                ],
                                value=[],
                                id="asset_3",
                                inline=True,
                                style={"display": "inline-block", "width": "100px"},
                            ),
                            dbc.Checklist(
                                options=[
                                    {"label": "SOL", "value": "solusdt"},
                                ],
                                value=[],
                                id="asset_4",
                                inline=True,
                                style={"display": "inline-block", "width": "100px"},
                            ),
                        ]
                    ),
                    dbc.Row(
                        [
                            dbc.Label(
                                "Granularity:  ", style={"vertical-align": "middle"}
                            ),
                            dcc.Dropdown(
                                id="query_granularity",
                                options=["1MIN", "15MIN", "1H", "1D", "1M"],
                                value="1D",
                                clearable=False,
                                style={
                                    "display": "inline-block",
                                    "width": "80px",
                                    "vertical-align": "middle",
                                },
                            ),
                        ]
                    ),
                    dbc.Row(
                        [
                            dbc.Label(
                                "Condition:  ", style={"vertical-align": "middle"}
                            ),
                            dcc.Dropdown(
                                id="condition_1_type",
                                options=["SMA"],
                                value="SMA",
                                clearable=False,
                                style={
                                    "display": "inline-block",
                                    "width": "80px",
                                    "vertical-align": "middle",
                                    "height": "30px",
                                },
                            ),
                            dcc.Input(
                                id="condition_1_value",
                                type="number",
                                debounce=True,
                                placeholder="value",
                                min=2,
                                style={
                                    "display": "inline-block",
                                    "margin-right": "0px",
                                    "margin-left": "0px",
                                    "width": "60px",
                                    "height": "22px",
                                },
                            ),
                            dcc.Dropdown(
                                id="condition_equality",
                                options=[">", "=", "<"],
                                value=">",
                                clearable=False,
                                style={
                                    "display": "inline-block",
                                    "width": "50px",
                                    "vertical-align": "middle",
                                    "height": "30px",
                                    "margin-left": "10px",
                                    "margin-right": "10px",
                                },
                            ),
                            dcc.Dropdown(
                                id="condition_2_type",
                                options=["SMA"],
                                value="SMA",
                                clearable=False,
                                style={
                                    "display": "inline-block",
                                    "width": "80px",
                                    "margin-left": "10px",
                                    "vertical-align": "middle",
                                    "height": "30px",
                                },
                            ),
                            dcc.Input(
                                id="condition_2_value",
                                type="number",
                                debounce=True,
                                placeholder="value",
                                min=2,
                                style={
                                    "display": "inline-block",
                                    "margin-left": "10px",
                                    "width": "60px",
                                    "height": "21px",
                                },
                            ),
                        ]
                    ),
                    dbc.Button("Submit", color="primary"),
                ],
            ),
            html.Div(id="query_table"),
        ]
    )
