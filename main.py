import json

import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from druid_handler import list_bus_lines, get_bus_positions

app = dash.Dash(
    __name__,
    external_stylesheets=['../assets/base.css', '../assets/style.css' '../assets/app.css'],
    meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)

# Date picker

datepicker = html.Div(
    className="div-for-dropdown",
    style={"margin-top": "20px"},
    children=[
        dcc.DatePickerSingle(
            id="date-picker",
            min_date_allowed='2019-01-25',
            max_date_allowed='2019-02-25',
            display_format="MMMM D, YYYY",
            date='2019-01-30',
            style={"border": "0px solid black"},
        )
    ],
)


# Bus Selector

@app.callback(Output('lines-holder', 'children'), [Input('date-picker', 'date')])
def update_lines(date):
    data = list_bus_lines(date)
    return json.dumps(data)


@app.callback(Output('line-dropdown', 'options'), [Input('lines-holder', 'children')])
def update_lines(lines):
    lines = list(json.loads(lines).keys())
    return [{"label": line.replace(".0", ""), "value": line} for line in lines]


@app.callback(
  Output('order-dropdown', 'options'),
  [Input('line-dropdown', 'value')],
  [State('lines-holder', 'children')]
)
def update_orders(bus_line, lines):
    if not bus_line or not lines:
        return []
    lines = json.loads(lines)
    orders = lines[bus_line]
    return [{"label": order, "value": order} for order in orders]


lines_holder = html.Div(
    id='lines-holder',
    style={"display": "none"},
    children=json.dumps(list_bus_lines('2019-01-30'))
)

line_selector = dcc.Dropdown(
    id="line-dropdown",
    options=[],
    value='485.0',
    placeholder="Seleciona uma linha de onibus",
)

order_selector = dcc.Dropdown(
    id="order-dropdown",
    options=[],
    value='B31019',
    placeholder="Selecione a ordem",
)


# Map

def create_map(line, order, date):
    data = get_bus_positions(line, order, date)
    fig = px.scatter_mapbox(
        data,
        center={"lat": -22.907171, "lon": -43.341513},
        lat="latitude",
        lon="longitude",
        # hover_name="order",
        hover_data=["datetime", "speed"],
        color_discrete_sequence=["fuchsia"],
        size_max=30,
        zoom=11
    )
    fig.update_layout(
        mapbox_style="dark",
        mapbox_accesstoken='pk.eyJ1Ijoia3JvZ2lhciIsImEiOiJjank2MW1sMG0wZG50M2VsaWNlMm1rYWRyIn0.cZxgJG56NcVWBEPBYphznA'
    )
    return fig


@app.callback(
  Output('location-map', 'figure'),
  [Input('order-dropdown', 'value'), Input('date-picker', 'date')],
  [State('line-dropdown', 'value')]
)
def update_positions(order, date, line):
    return create_map(line, order, date)


location_map = dcc.Graph(
    id='location-map',
    style={"width": "100%", "height": "100%"},
    figure=create_map('485.0', 'B31019', '2019-01-30')
)

# App Layout

app.layout = html.Div(
    id='app',
    children=[
        lines_holder,
        html.Div(
            className="row selectors",
            children=[
                html.Div(
                    className="four columns div-user-controls",
                    children=[
                        html.Img(
                            className="logo-ufrj", src=app.get_asset_url("diversidade.svg")
                        ),
                        html.H1("Mapa - Onibus do Rio de Janeiro"),
                        html.P(
                            "Plot de dados de GPS dos onibus da cidade do Rio de Janeiro coletados de 25/01/2019 à 25/02/219"),
                        datepicker,
                        # Change to side-by-side for mobile layout
                        html.Div(
                            children=[
                                html.Div(
                                    className="div-for-dropdown bus-selector",
                                    children=[
                                        line_selector,
                                        order_selector
                                    ],
                                ),
                            ],
                        ),
                        html.P(id="total-rides"),
                        html.P(id="total-rides-selection"),
                        html.P(id="date-value"),
                    ],
                ),
            ],
        ),
        location_map
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True)
