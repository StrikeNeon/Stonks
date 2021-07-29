from data_ops import download_symbol
from plotter import plotter_engine

data = download_symbol()

plot_creator = plotter_engine()
plot_creator.plot_symbol(data)
plot_creator.show_plot()
