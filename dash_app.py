import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from plotly.tools import make_subplots
from dash.dependencies import Input, Output
from data_ops import technical_indicators

from temp_main import binance_client

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div(
    html.Div([
        html.H4('BTC live recount'),
        html.Div(id='live-update-text'),
        dcc.Graph(id='live-update-graph'),
        dcc.Interval(
            id='interval-btc',
            interval=(60*60)*1000, # in milliseconds, 60 minutes per interval
            n_intervals=0
        )
    ])
)

@app.callback(Output('live-update-text', 'children'),
              Input('interval-btc', 'n_intervals'))
def update_metrics(n):
    ticker = binance_client.get_data_tick('BTCUSDT')
    style = {'padding': '5px', 'fontSize': '16px'}
    return [
        html.Span(f'open: {ticker["open"][0]}', style=style),
        html.Span(f'high: {ticker["high"][0]}', style=style),
        html.Span(f'low: {ticker["low"][0]}', style=style),
        html.Span(f'close: {ticker["close"][0]}', style=style)
    ]


# Multiple components can update everytime interval gets fired.
@app.callback(Output('live-update-graph', 'figure'),
              Input('interval-btc', 'n_intervals'))
def update_graph_live(n):
    initial_data = binance_client.get_current_data('BTCUSDT')

    s_sma, l_sma = technical_indicators.get_sma(initial_data)
    ema = technical_indicators.get_ema(initial_data)
    rsi = technical_indicators.get_rsi(initial_data, periods=15)

    fig = make_subplots(rows=1, cols=2, vertical_spacing=0.5, horizontal_spacing=0.1)
    #Candlestick
    fig.append_trace(go.Candlestick(x=initial_data.index,
                    open=initial_data['open'],
                    high=initial_data['high'],
                    low=initial_data['low'],
                    close=initial_data['close'], name='market data'), row=1, col=1)

    # Add titles
    fig.update_layout(
        title='ETH to BTC pair price evolution',
        yaxis_title='ETHBTC share data')

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

    fig.append_trace(go.Scatter(x=initial_data.index, y=s_sma, mode='lines', name='short sma'), row=1, col=1)
    fig.append_trace(go.Scatter(x=initial_data.index, y=l_sma, mode='lines', name='long sma'), row=1, col=1)
    fig.append_trace(go.Scatter(x=initial_data.index, y=ema, mode='lines', name='ema'), row=1, col=1)

    fig.append_trace(go.Scatter(x=initial_data.index, y=rsi, mode='lines', name='rsi'), row=1, col=2)

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)