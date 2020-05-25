from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import figure
from bokeh.io import output_file, show
from bokeh.layouts import column
import numpy as np

class Plots():

    def __init__(self, embed_data = None):
        self.embed_data = embed_data
        self.plots_dict = dict()
        self.state = list(self.plots_dict.keys())

    def time_series_plot(self, state_list):
        for state in state_list:
            df = self.embed_data[self.embed_data['state'] == state]
            #df = df.merge(df_us, how='outer', on='date').sort_values('date')

            source = ColumnDataSource(data = df)

            my_dic = {'cases': 'Total Cases', 'diff': "Daily Change"}

            def add_figure(metric):
                f = figure(title = "COVID-19 {} Over Time in {}".format(my_dic[metric], state), 
                        x_axis_label = 'Date', 
                        y_axis_label = 'COVID-19 {}'.format(my_dic[metric]), 
                        x_axis_type = 'datetime', 
                        plot_width = 800,
                        plot_height = 400,
                        tools = 'pan, box_zoom, wheel_zoom, reset, save')
                        #sizing_mode = 'scale_width')
                f.title.text_color = 'Green'
                f.title.text_font = 'ariel'
                f.title.text_font_style = 'bold'
                f.grid.grid_line_color = 'white'
                f.background_fill_color = '#f5f5f5'
                f.yaxis.minor_tick_line_color = None
                f.xaxis.minor_tick_line_color = None

                f.line('date', metric, source = source, color = '#ebbd5b', alpha = 0.5, line_width = 2)
                f.circle('date', metric, source = source, size= 4, line_color = '#ebbd5b', fill_color = 'white')
                #f.line('date', "{}_us".format(metric), source = source, color = '#FF6347', alpha = 0.5, line_width = 2)
                #f.circle('date', "{}_us".format(metric), source = source, size= 4, line_color = '#FF6347', fill_color = 'white')
            
                f.add_tools(HoverTool(
                    tooltips = [
                        ("State", "@state"),
                        ("Date", "@date_str"),
                        ("{}".format(my_dic[metric]), "@{}".format(metric))
                    ],

                    mode = 'vline'
                ))
                return f

            f_cases = add_figure('cases')
            f_deaths = add_figure('diff')

            p = column(f_cases, f_deaths)

            self.plots_dict[state] = p
            self.state = list(self.plots_dict.keys())
            
    