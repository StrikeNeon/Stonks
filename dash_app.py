import requests
from pandas import DataFrame, Series
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from plotly.tools import make_subplots
from dash.dependencies import Input, Output

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div(
    html.Div([
        html.H4('BTC live recount'),
        html.Div(id='live-update-text'),
        html.Div(id='live-update-signal'),
        dcc.Graph(id='live-update-main_candles'),
        dcc.Graph(id='live-update-graph'),
        dcc.Interval(
            id='interval-btc',
            interval=1*(pow(60, 2)*1000),  # hours in milliseconds, 60x60 seconds per interval
            n_intervals=0
        ),
        dcc.Interval(
            id='interval-btc-pivot',
            interval=24*(pow(60, 2)*1000),  # hours in milliseconds, 60x60 seconds per interval
            n_intervals=0
        ),
        dcc.Graph(id='live-update-siggraph'),
        dcc.Graph(id='live-update-pivotgraph')
    ])
)

@app.callback(Output('live-update-text', 'children'),
              Input('interval-btc', 'n_intervals'))
def update_metrics(n):
    request = requests.get("http://127.0.0.1:8082/get_current_data?symbol=BTCRUB")
    if request.status_code == 200:
        data = request.json()
        style = {'padding': '5px', 'fontSize': '16px'}
        return [
            html.Span(f'open: {data.get("data")[-1].get("open")}', style=style),
            html.Span(f'high: {data.get("data")[-1].get("high")}', style=style),
            html.Span(f'low: {data.get("data")[-1].get("low")}', style=style),
            html.Span(f'close: {data.get("data")[-1].get("close")}', style=style)
        ]
    else:
        style = {'padding': '5px', 'fontSize': '16px'}
        return [
            html.Span('error retrieving data', style=style)
        ]

@app.callback(Output('live-update-main_candles', 'figure'),
              Input('interval-btc', 'n_intervals'))
def update_main_candlestick(n):
    current_data = requests.get("http://127.0.0.1:8082/get_current_data?symbol=BTCRUB")
    if current_data.status_code == 200:
        candlestick_dataframe = DataFrame(current_data.json().get("data"))
        fig = make_subplots(rows=1, cols=1, vertical_spacing=0.5, horizontal_spacing=0.1)
        #Candlestick
        fig.append_trace(go.Candlestick(x=candlestick_dataframe.index[-12:],
                        open=candlestick_dataframe['open'][-12:],
                        high=candlestick_dataframe['high'][-12:],
                        low=candlestick_dataframe['low'][-12:],
                        close=candlestick_dataframe['close'][-12:], name='market data'), row=1, col=1)

        # Add titles
        fig.update_layout(
            title='BTC to RUB pair price evolution',
            yaxis_title='BTCRUB share data')

        # X-Axes
        fig.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=15, label="15m", step="minute", stepmode="backward"),
                    dict(count=45, label="45m", step="minute", stepmode="backward"),
                    dict(count=1, label="HTD", step="hour", stepmode="todate"),
                    dict(count=6, label="6h", step="hour", stepmode="backward"),
                    dict(step="all")
                ])
            )
        )
        return fig
    else:
        fig = make_subplots(rows=1, cols=1, vertical_spacing=0.5, horizontal_spacing=0.1)
        fig.append_trace(go.Scatter(x=[0],
                                    y=[0],
                                    mode='lines+markers',
                                    name='error',
                                    line_color="white"),
                        row=1, col=1)
        fig.update_layout(
            title='ERROR')
        return fig


# Multiple components can update everytime interval gets fired.
@app.callback(Output('live-update-graph', 'figure'),
              Input('interval-btc', 'n_intervals'))
def update_graph_live(n):

    candlestick_dataframe = DataFrame(request_data("http://127.0.0.1:8082/get_current_data?symbol=BTCRUB").get("data"))
    sma_data = request_data("http://127.0.0.1:8082/get_current_sma?symbol=BTCRUB").get("data")
    try:
        l_sma = sma_data.get("long_rolling")
        s_sma = sma_data.get("short_rolling")
    except AttributeError:
        pass
    ema_data = request_data("http://127.0.0.1:8082/get_current_ema?symbol=BTCRUB").get("data")
    rsi_data = request_data("http://127.0.0.1:8082/get_current_rsi?symbol=BTCRUB").get("data")
    bbands_data = request_data("http://127.0.0.1:8082/get_current_bbands?symbol=BTCRUB").get("data")
    try:
        upper_bband = bbands_data.get("upper_bb")
        lower_bband = bbands_data.get("lower_bb")
    except AttributeError:
        pass
    if type(candlestick_dataframe) is not None and type(sma_data) is not None and type(ema_data) is not None and type(rsi_data) is not None and type(bbands_data) is not None :

        fig = make_subplots(rows=2, cols=2, vertical_spacing=0.5, horizontal_spacing=0.1)
        #Candlestick
        fig.append_trace(go.Scatter(x=candlestick_dataframe.index[-12:],
                        y=candlestick_dataframe['close'][-12:], name='market data'), row=1, col=1)

        # Add titles
        fig.update_layout(
            title='BTC to RUB ta analysis',
            yaxis_title='BTCRUB share data')

        # X-Axes
        fig.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=15, label="15m", step="minute", stepmode="backward"),
                    dict(count=45, label="45m", step="minute", stepmode="backward"),
                    dict(count=1, label="HTD", step="hour", stepmode="todate"),
                    dict(count=6, label="6h", step="hour", stepmode="backward"),
                    dict(step="all")
                ])
            )
        )
        fig.append_trace(go.Scatter(x=candlestick_dataframe.index[-12:], y=s_sma[-12:], mode='lines', name='short sma'), row=1, col=1)
        fig.append_trace(go.Scatter(x=candlestick_dataframe.index[-12:], y=l_sma[-12:], mode='lines', name='long sma'), row=1, col=1)
        fig.append_trace(go.Scatter(x=candlestick_dataframe.index[-12:], y=ema_data[-12:], mode='lines', name='ema'), row=1, col=1)

        fig.append_trace(go.Scatter(x=candlestick_dataframe.index[-12:],
                        y=candlestick_dataframe['close'][-12:], mode='lines', name='market data'), row=2, col=1)
        fig.append_trace(go.Scatter(x=candlestick_dataframe.index[-12:], y=upper_bband[-12:], mode='lines', name='upper bband'), row=2, col=1)
        fig.append_trace(go.Scatter(x=candlestick_dataframe.index[-12:], y=lower_bband[-12:], mode='lines', name='lower bband'), row=2, col=1)

        fig.append_trace(go.Scatter(x=candlestick_dataframe.index[-12:], y=rsi_data[-12:], mode='lines', name='rsi'), row=1, col=2)

        return fig
    else:
        fig = make_subplots(rows=1, cols=1, vertical_spacing=0.5, horizontal_spacing=0.1)
        fig.append_trace(go.Scatter(x=[0],
                                    y=[0],
                                    mode='lines+markers',
                                    name='error',
                                    line_color="white"),
                        row=1, col=1)
        fig.update_layout(
            title='ERROR')
        return fig

@app.callback(Output('live-update-pivotgraph', 'figure'),
              Input('interval-btc-pivot', 'n_intervals'))
def update_pivot_graph(n):
    current_data = requests.get("http://127.0.0.1:8082/get_current_pivots?symbol=BTCRUB&client=CEOMindset_1")
    if current_data.status_code == 403:
        login_status = requests.get("http://127.0.0.1:8082/activate_client?client=CEOMindset_1&password=TheValueOfVifeIsNegative")
        current_data = requests.get("http://127.0.0.1:8082/get_current_pivots?symbol=BTCRUB&client=CEOMindset_1")
        if login_status.status_code != 200:
            fig = make_subplots(rows=1, cols=1, vertical_spacing=0.5, horizontal_spacing=0.1)
            fig.append_trace(go.Scatter(x=[0],
                                        y=[0],
                                        mode='lines+markers',
                                        name='error',
                                        line_color="white"),
                            row=1, col=1)
            fig.update_layout(
                title='ERROR {current_data.status_code}')
            return fig
    if current_data.status_code == 200:
        pivot_data = current_data.json().get("data")
        fig = make_subplots(rows=1, cols=1, vertical_spacing=0.5, horizontal_spacing=0.1)
        fig.append_trace(go.Scatter(x=list(range(len(pivot_data))), y=pivot_data, mode='lines', name='pivots'), row=1, col=1)
        return fig
    else:
        fig = make_subplots(rows=1, cols=1, vertical_spacing=0.5, horizontal_spacing=0.1)
        fig.append_trace(go.Scatter(x=[0],
                                    y=[0],
                                    mode='lines+markers',
                                    name='error',
                                    line_color="white"),
                        row=1, col=1)
        fig.update_layout(
            title='ERROR')
        return fig

def set_marker_symbol(point):
    if point == 1:
        return 5
    elif point == 0:
        return 0
    elif point == -1:
        return 6


def set_marker_color(point):
    if point == 1:
        return "green"
    elif point == 0:
        return "black"
    elif point == -1:
        return "red"


@app.callback(Output('live-update-siggraph', 'figure'),
              Input('interval-btc', 'n_intervals'))
def update_signal_graph(n):
    signals = request_data("http://127.0.0.1:8082/get_combined_signal?symbol=BTCRUB&thresh=5").get("data")

    if signals and signals != 500:
        fig = make_subplots(rows=1, cols=1, vertical_spacing=0.5, horizontal_spacing=0.1)
        fig.append_trace(go.Scatter(x=Series(signals).index,
                                    y=Series(signals),
                                    mode='lines+markers',
                                    name='signaling',
                                    line_color="white",
                                    marker=dict(color=list(map(set_marker_color, signals)),
                                                symbol=list(map(set_marker_symbol, signals)))),
                        row=1, col=1)
        fig.update_layout(
            title='BTC to RUB signaling')
        return fig
    else:
        fig = make_subplots(rows=1, cols=1, vertical_spacing=0.5, horizontal_spacing=0.1)
        fig.append_trace(go.Scatter(x=[0],
                                    y=[0],
                                    mode='lines+markers',
                                    name='error',
                                    line_color="white"),
                        row=1, col=1)
        fig.update_layout(
            title='ERROR')
        return fig


@app.callback(Output('live-update-signal', 'children'),
              Input('interval-btc', 'n_intervals'))
def update_signals(n):
    signal = requests.get("http://127.0.0.1:8082/combined_signal?symbol=BTCRUB&thresh=5")

    if signal.status_code == 200:
        signal_data = signal.json()
        style = {'padding': '5px', 'fontSize': '16px'}
        return [
            html.Span(f'decided signal: {signal_data.get("message")}', style=style),
            html.Span(f'rsi-backed sma: {signal_data.get("sma_signal")}', style=style),
            html.Span(f'bbands: {signal_data.get("bbands_signal")}', style=style),
            html.Span(f'pivots: {signal_data.get("pivot_signal")}', style=style)
        ]
    else:
        style = {'padding': '5px', 'fontSize': '16px'}
        return [
            html.Span('error retrieving data', style=style)
        ]


def request_data(link: str):
    data_responce = requests.get(link)
    if data_responce.status_code == 200:
        data = data_responce.json()
        return data


if __name__ == '__main__':
    app.run_server(debug=True)
