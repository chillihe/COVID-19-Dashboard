import folium
import numpy as np
from bokeh.resources import CDN
from bokeh.embed import file_html
from folium import IFrame

class Maps():

    def __init__(self, data_state = None, data_geo = None):
        self.map = folium.Map(location = [38.58, -99.09], 
                zoom_start=5, 
                tiles = 'Stamen Terrain')
        self.data_state = data_state
        self.data_geo = data_geo
    
    def create_choropleth(self, metric = 'cases'):
        bins = list(self.data_state[metric].quantile([0,0.5,0.9,0.99,1]))
        recent_date = self.data_state['date'].max()

        choropleth = folium.Choropleth(
            geo_data=self.data_geo,
            name='COVID-19 Current Cases Choropleth on {}'.format(recent_date.date()),
            data=self.data_state,
            columns=['state', 'cases'],
            key_on='feature.properties.name',
            fill_color='YlGn',
            fill_opacity=0.7,
            line_opacity=0.2,
            bins = bins,
            legend_name='COVID-19 Cases',
            reset = True,
            smooth_factor = 0
        ).add_to(self.map)

        choropleth.geojson.add_child(folium.features.GeoJsonTooltip(
            fields = ['name', 'cases', 'deaths'],
            aliases = ['State:', 'Total Cases:', 'Total Deaths:'],
            localize = True
            #style = ('background-color: grey; color: white;')
        )) 

    def convert_to_html(self, plots_dict):
        for state in plots_dict.keys():
            plots_dict[state] = file_html(plots_dict[state], CDN, 'plot')

    def create_marker(self, plots_dics):
        lat = list(self.data_state['latitude'])
        lon = list(self.data_state['longitude'])
        date = list(self.data_state['date'])
        state = list(self.data_state['state'])
        cases = list(self.data_state['cases'])
        deaths = list(self.data_state['deaths'])
    
        fgm = folium.FeatureGroup(name = 'Time-Series State COVID-19 Stats')
        for lat, lon, date, state, cases, deaths in zip(lat, lon, date, state, cases, deaths):
            iframe = folium.IFrame(html=plots_dics[state], width=900, height=500)
            fgm.add_child(folium.CircleMarker(location = [lat,lon],
                    radius = 6,
                    popup=folium.Popup(iframe, max_width=2650),
                    tooltip = '{} (click for time-series info)'.format(state),
                    color = 'grey',
                    weight = 2,
                    fill = True,
                    fill_color = 'green',
                    fill_opacity = 0.7))
        self.map.add_child(fgm)

    def add_layer_control(self):
        self.map.add_child(folium.LayerControl())

    def save_dashboard(self):
        self.map.save('Map1.html')


    
        

