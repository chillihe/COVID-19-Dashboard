
import pandas as pd
import numpy as np
import io
import requests
import urllib, json, urllib.request

class DataImporter():

    def __init__(self):
        self.df_covid19 = dict()
        self.df_state_coor = pd.DataFrame()
        self.state_geo = None
        self.level = list(self.df_covid19.keys())
        self.recent_date = None
        self.state_list = list()

    def getImportedData(self):
        # Pull the COVIDE-19 data
        url_dict = {'us': 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us.csv',
                    'state': 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv',
                    'county': 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv'}

        for (level, url) in url_dict.items():
            self.get_covid19_data(url, level)
            self.gen_date_str(level)
            self.cal_diffs(level)

        # df_us.columns = ['country', 'date', 'cases_us', 'deaths_us', 'date_str_us', 'diff_us']

        # Get State Coordinates
        url_coor = 'https://developers.google.com/public-data/docs/canonical/states_csv'
        self.merge_coordinate(url_coor)

        # Get the US state GeoJson data
        url_geojon = "https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/us-states.json"
        self.get_geojson(url_geojon)
        self.add_case_death(('cases', 'deaths'))

        # Update the class attributes based on the data
        self.state_list = self.df_state_coor['state'].unique()

        return self

    # Pull the COVID-19 data
    def get_covid19_data(self, url, level):
        s = requests.get(url).content
        df = pd.read_csv(io.StringIO(s.decode('utf-8')), parse_dates = ['date'])
        df['country'] = ['USA'] * df.shape[0]
        self.df_covid19[level] = df
        self.level = list(self.df_covid19.keys())

    # Generate a new date variable in the string format
    def gen_date_str(self, level):
        def date_to_string(datetime):
            return datetime.strftime("%b-%d-%Y")
        self.df_covid19[level]['date_str'] = self.df_covid19[level]['date'].apply(lambda x: date_to_string(x))
        
    # Calculate the differences in the daily total number of cases compared to the previosu day
    def cal_diffs(self, level):
        my_dict = {'us': ['country','date'],
                   'state': ['state', 'date'],
                   'county': ['state', 'county', 'date']}

        self.df_covid19[level].sort_values(by = my_dict[level], inplace = True)
        self.df_covid19[level].set_index(my_dict[level], inplace= True)
        self.df_covid19[level]['diff'] = np.nan
        idx = pd.IndexSlice
        for ix in self.df_covid19[level].index.levels[0]:
            self.df_covid19[level].loc[ idx[ix,:], 'diff'] = self.df_covid19[level].loc[idx[ix,:], 'cases' ].diff()
        self.df_covid19[level].reset_index(inplace = True)

    # Get the coordinates data & Merge the US-State data with the coordinates
    def merge_coordinate(self, url):
        state_coor = pd.read_html(url)[0]
        state_coor.columns = 'state_abv latitude longitude state'.split()
        recent_date = self.df_covid19['state']['date'].max()
        df_state_recent = self.df_covid19['state'][self.df_covid19['state']['date'] == recent_date]
        self.df_state_coor = df_state_recent.merge(state_coor, how = 'inner', on = 'state')
        self.recent_date = recent_date
       
    # Get the US state GeoJson data
    def get_geojson(self, url):
        data = urllib.request.urlopen(url).read().decode()
        self.state_geo = json.loads(data)
         
    # Add the cases and deaths into the GeoJson file
    def add_case_death(self, metric_tuple):
        for ft in self.state_geo['features']:
            state = ft['properties']['name']
            df = self.df_state_coor[self.df_state_coor['state'] == state]
            for i in metric_tuple:
                ft['properties'][i] = int(df.loc[df.index[0], i])
