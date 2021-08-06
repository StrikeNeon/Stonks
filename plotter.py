#Data viz
import plotly.graph_objs as go
from plotly.subplots import make_subplots


class plotter_engine():

    def __init__(self):
        #declare figure
        # self.plot = go.Figure()
        self.plot = make_subplots(rows=1, cols=2)

    def plot_symbol(self, data):

        #Candlestick
        self.plot.add_trace(go.Candlestick(x=data.index,
                        open=data['open'],
                        high=data['high'],
                        low=data['low'],
                        close=data['close'], name='market data'), row=1, col=1)

        # Add titles
        self.plot.update_layout(
            title='Bitcoin live share price evolution',
            yaxis_title='Bitcoin Price (kUS Dollars)')

        # X-Axes
        self.plot.update_xaxes(
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

    def plot_sma(self, short_rolling, long_rolling, data):
        self.plot.add_trace(go.Scatter(x=data.index, y=short_rolling, mode='lines', name='short sma'), row=1, col=1)
        self.plot.add_trace(go.Scatter(x=data.index, y=long_rolling, mode='lines', name='long sma'), row=1, col=1)

    def plot_ema(self, ema, data):
        self.plot.add_trace(go.Scatter(x=data.index, y=ema, mode='lines', name='ema'), row=1, col=1)

    def plot_rsi(self, rsi, data):
        self.plot.add_trace(go.Scatter(x=data.index, y=rsi, mode='lines', name='rsi'), row=1, col=2)

    def show_plot(self):
        self.plot.show()
