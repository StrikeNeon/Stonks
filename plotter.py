#Data viz
import plotly.graph_objs as go


class plotter_engine():

    def __init__(self):
        #declare figure
        self.plot = go.Figure()

    def plot_symbol(self, data):

        #Candlestick
        self.plot.add_trace(go.Candlestick(x=data.index,
                        open=data['Open'],
                        high=data['High'],
                        low=data['Low'],
                        close=data['Close'], name='market data'))

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

        #Show
        rendered_plot = self.plot.to_image(format="png")
        return rendered_plot

    def plot_sma(self, short_rolling, long_rolling, data):
        short_trace = go.Scatter(x=data['time'], y=short_rolling, mode='lines', name='short rolling')
        long_trace = go.Scatter(x=data['time'], y=long_rolling, mode='lines', name='long rolling')
        self.plot.add_trace(short_trace)
        self.plot.add_trace(long_trace)

    def show_plot(self):
        self.plot.show()
