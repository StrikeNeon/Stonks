import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

app = dash.Dash(__name__)

app.layout = html.Div([
    html.P("Render Option:"),
    dcc.RadioItems(
        id='render-option',
        options=[{'value': x, 'label': x} 
                 for x in ['interactive', 'image']],
        value='image'
    ),
    html.Div(id='output'),
])

@app.callback(
    Output("output", "children"), 
    [Input('render-option', 'value')])
def display_graph(render_option):
    if render_option == 'image':
        img_bytes = fig.to_image(format="png")
        encoding = b64encode(img_bytes).decode()
        img_b64 = "data:image/png;base64," + encoding
        return html.Img(src=img_b64, style={'width': '100%'})
    else:
        return dcc.Graph(figure=fig)

app.run_server(debug=True)


# import dash
# from dash.dependencies import Output, Input
# import dash_core_components as dcc
# import dash_html_components as html
# import plotly
# import random
# import plotly.graph_objs as go
# from collections import deque
  
# X = deque(maxlen = 20)
# X.append(1)
  
# Y = deque(maxlen = 20)
# Y.append(1)
  
# app = dash.Dash(__name__)
  
# app.layout = html.Div(
#     [
#         dcc.Graph(id = 'live-graph', animate = True),
#         dcc.Interval(
#             id = 'graph-update',
#             interval = 1000,
#             n_intervals = 0
#         ),
#     ]
# )
  
# @app.callback(
#     Output('live-graph', 'figure'),
#     [ Input('graph-update', 'n_intervals') ]
# )
  
# def update_graph_scatter(n):
#     X.append(X[-1]+1)
#     Y.append(Y[-1]+Y[-1] * random.uniform(-0.1,0.1))
  
#     data = plotly.graph_objs.Scatter(
#             x=list(X),
#             y=list(Y),
#             name='Scatter',
#             mode= 'lines+markers'
#     )
  
#     return {'data': [data],
#             'layout' : go.Layout(xaxis=dict(range=[min(X),max(X)]),yaxis = dict(range = [min(Y),max(Y)]),)}
  
# if __name__ == '__main__':
#     app.run_server()