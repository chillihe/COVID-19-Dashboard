from DataImporter import DataImporter
from Plots import Plots
from Maps import Maps

class CreateDashboard():

    def __init__(self):
        self.data_import = DataImporter()
        self.plots = Plots()
        self.maps = Maps()
        self.state_list = None

    def run(self):
        self.data_preparation()
        self.create_plots()
        self.create_maps()
        self.create_html()
        print(self.data_import.recent_date)

    def data_preparation(self):

        self.data_import = self.data_import.getImportedData()

    def create_plots(self):
        self.plots = Plots(self.data_import.df_covid19['state'])
        # self.plots.time_series_plot(self.state_list)
        self.plots.time_series_plot(self.data_import.state_list)


    def create_maps(self):
        self.maps = Maps(data_state = self.data_import.df_state_coor, data_geo = self.data_import.state_geo)
        
        # Layer 1: create a choropleth map, colorcoded by number of COVID-19 cases currently
        self.maps.create_choropleth(metric = 'cases')

        # Layer 2: create markers for each state
        ## Convert the Bokeh figures to html
        self.maps.convert_to_html(self.plots.plots_dict)

        ## Create the markers
        self.maps.create_marker(self.plots.plots_dict)

        self.maps.add_layer_control()
        self.maps.save_dashboard()

    def create_html(self):
        
from webbrowser import open_new_tab
        f = open('dashboard.html', 'wb')
        message = """<html>
        <head>
        <title>COVID-19 Statistics on %s by State</title>
        </head>
        </html>"""

        whole = message %self.data_import.recent_date

        f.write(whole)
        f.close()

        open_new_tab('dashboard.html')



dashboard = CreateDashboard()
dashboard.run()
