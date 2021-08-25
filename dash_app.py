import requests
from pandas import DataFrame
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
        dcc.Graph(id='live-update-graph'),
        dcc.Interval(
            id='interval-btc',
            interval=(1*60)*1000,  # in milliseconds, 60 minutes per interval
            n_intervals=0
        ),
        html.Div(id='live-update-signals'),
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
    if type(candlestick_dataframe) != None and type(sma_data) != None and type(ema_data) != None and type(rsi_data) != None and type(bbands_data) != None:

        fig = make_subplots(rows=2, cols=2, vertical_spacing=0.5, horizontal_spacing=0.1)
        #Candlestick
        fig.append_trace(go.Candlestick(x=candlestick_dataframe.index,
                        open=candlestick_dataframe['open'],
                        high=candlestick_dataframe['high'],
                        low=candlestick_dataframe['low'],
                        close=candlestick_dataframe['close'], name='market data'), row=1, col=1)

        # Add titles
        fig.update_layout(
            title='BTC to USD pair price evolution',
            yaxis_title='BTCUSD share data')

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
        fig.append_trace(go.Scatter(x=candlestick_dataframe.index, y=s_sma, mode='lines', name='short sma'), row=1, col=1)
        fig.append_trace(go.Scatter(x=candlestick_dataframe.index, y=l_sma, mode='lines', name='long sma'), row=1, col=1)
        fig.append_trace(go.Scatter(x=candlestick_dataframe.index, y=ema_data, mode='lines', name='ema'), row=1, col=1)

        fig.append_trace(go.Scatter(x=candlestick_dataframe.index,
                        y=candlestick_dataframe['close'], mode='lines', name='market data'), row=2, col=1)
        fig.append_trace(go.Scatter(x=candlestick_dataframe.index, y=upper_bband, mode='lines', name='upper bband'), row=2, col=1)
        fig.append_trace(go.Scatter(x=candlestick_dataframe.index, y=lower_bband, mode='lines', name='lower bband'), row=2, col=1)

        fig.append_trace(go.Scatter(x=candlestick_dataframe.index, y=rsi_data, mode='lines', name='rsi'), row=1, col=2)

        return fig
    else:
        style = {'padding': '5px', 'fontSize': '16px'}
        return [
            html.Span('error retrieving data', style=style)
        ]


@app.callback(Output('live-update-signals', 'children'),
              Input('interval-btc', 'n_intervals'))
def update_signals(n):
    sma_signal = requests.get("http://127.0.0.1:8082/compute_sma_scalp?symbol=BTCRUB")
    sma_cross_signal = requests.get("http://127.0.0.1:8082/compute_sma_cross_scalp?symbol=BTCRUB")
    bband_signal = requests.get("http://127.0.0.1:8082/compute_bband_scalp?symbol=BTCRUB")
    rsi_signal = requests.get("http://127.0.0.1:8082/compute_rsi_scalp?symbol=BTCRUB&thresh=5")

    if sma_signal.status_code == 200 and bband_signal.status_code == 200 and sma_cross_signal.status_code == 200 and rsi_signal.status_code == 200:
        sma_data = sma_signal.json()
        sma_cross_data = sma_cross_signal.json()
        bband_data = bband_signal.json()
        rsi_data = rsi_signal.json()

        style = {'padding': '5px', 'fontSize': '16px'}
        return [
            html.Span(f'sma signal: {sma_data.get("message")}', style=style),
            html.Span(f'sma cross  signal: {sma_cross_data.get("message")}', style=style),
            html.Span(f'bband signal: {bband_data.get("message")}', style=style),
            html.Span(f'rsi signal: {rsi_data.get("message")}', style=style)
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
