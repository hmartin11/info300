from dash import Dash, html, dcc, callback, Output, Input
from dash_extensions.javascript import assign
import dash_leaflet as dl
import plotly.express as px
import pandas as pd
import os
import geopandas as gpd
from whitenoise import WhiteNoise 
import gunicorn


tile_url = 'https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png'

df = pd.read_csv('static/occurrence.csv', sep='\t')
cols = ['vernacularName', 
        'specificEpithet',
        'dateIdentified',
        'decimalLatitude',
        'decimalLongitude', 
        'locality', 
        'waterBody', 
        'year', 'month', 'day', 'eventTime', 'organismID']

df = df[cols]
data = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.decimalLongitude, df.decimalLatitude))
data = data.__geo_interface__


use_icon = assign("""function(feature, latlng){
const i = L.icon({iconUrl: `https://img.icons8.com/color/48/orca.png`, iconSize: [30, 30]});
return L.marker(latlng, {icon: i});
}""")
                  

markers = [dl.Marker(position=[row["decimalLatitude"], row["decimalLongitude"]]) for i, row in df.iterrows()]
app = Dash(__name__)
server = app.server
geojson = dl.GeoJSON(data=data, pointToLayer=use_icon, id='geo')
map = dl.Map([
                dl.TileLayer(
                    url=tile_url),

                dl.LocateControl(
                    locateOptions={'enableHighAccuracy': True}), 
              
                geojson
                ],
                    center=[49,-123],
                    zoom=9,
                    style={'height': '100%'},
                    id='main_map',
                    dragging=True,
                    zoomControl=True,
                    scrollWheelZoom=True,
                    doubleClickZoom=True,
                    boxZoom=True,
                )

cell_style = {'padding': '20px',
              'text-align': 'center'}


image_path = 'figma.png'

# Set the layout right the first time!
app.layout = html.Div(
    style={
        'display': 'grid',
        'gridTemplateColumns': '33% 33% 33%',
        'gridTemplateRows': '33% 33% 33%',
        'gap': '5px',
        'height': '100vh',
        'width': '100vw', 
    },
    children=[
        html.Div(  html.Img(src=app.get_asset_url(image_path)),style={
                 'backgroundColor': '#b3e6ff', 'gridColumn': 'span 3','gridRow':1, **cell_style}),
        html.Div(map, style={'backgroundColor': '#b3e6ff',
                 **cell_style, 'gridColumn': 'span 2', 'gridRow': 'span 2'}),
        html.Div([dcc.Graph(id='graph-w-dropdown'),
                dcc.Dropdown(
                options= ['locality', 'waterBody'], 
                value = 'locality',
                id='dropdown1'
                ), 
                dcc.Dropdown(
                options=[{"label": y, "value": y} for y in df["year"].unique()],
                value=df["year"].unique()[0],
                id='years'
                )
                    
                ], style={
                 'backgroundColor': '#b3e6ff', **cell_style, 'gridColumn': 'span 1', 'gridRow': 'span 2'})
        # html.Div(['Env Map'], style={
        #          'backgroundColor': 'lightpink', **cell_style})
    ]
)
@callback(
    Output(component_id='graph-w-dropdown', component_property='figure'),
    Input(component_id='dropdown1', component_property='value'),
    Input('years', 'value'),
    
)

def update_graph(col_chosen, selected_year):
    filtered_df = df[df.year == selected_year]
    fig = px.histogram(filtered_df, x=col_chosen, title="Count of Orcas By Year and Region", y='specificEpithet', histfunc='count')
    return fig
   return dl.GeoJSON(data=data, pointToLayer=use_icon, id='geo')



if __name__ == "__main__":
    app.run(debug=True)
