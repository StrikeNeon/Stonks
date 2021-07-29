from data_ops import download_symbol, get_sma
from plotter import plotter_engine

data = download_symbol()
s_sma, l_sma = get_sma(data)

plot_creator = plotter_engine()
plot_creator.plot_symbol(data)
# plot_creator.plot_sma(s_sma, l_sma, data)
plot_creator.show_plot()
