#!/usr/bin/env python3

import time
import threading
import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
from bokeh.plotting import figure, output_file, show
from bokeh.models import ColumnDataSource, HoverTool

URL = 'http://192.168.1.18/' #Temperature sensor endpoint
FILENAME = 'ts_temp.txt'    #file to store temperature data


def genframe():
    """
    Generates dataframe from CSV file containing temperature data
    Returns a smoothed data frame and last temperature reading
    """
    data_frame = pd.read_csv(FILENAME, sep=' ', header=None, names=['Timestamp', 'Temperature'], parse_dates=['Timestamp'], date_parser=lambda epoch: pd.to_datetime(epoch, unit='s'))
    #Experimentally determined window length to provide appropriate smoothing of the graph, 
    # +1 is for conditions where the data frame does not contain enough data hence setting window size to 1
    smoothed_df = data_frame.set_index('Timestamp').interpolate().rolling(window=len(data_frame)//17+1).mean() 
    prev_temp = data_frame['Temperature'].iloc[-1]
    return(smoothed_df, prev_temp)


def plot(data_frame):
    """
    Plots a bokeh chart from the generated dataframe
    """
    data_frame = data_frame
    source = ColumnDataSource(data_frame)
    output_file("output.html")

    plot_chart = figure(plot_width=1200, plot_height=800, sizing_mode='scale_height', x_axis_type='datetime', title=u'Fermentor Temperature \xb0C', tools='pan,wheel_zoom,hover,save,reset')

    hover = plot_chart.select(dict(type=HoverTool))
    hover.tooltips = [
    ("index", "$index"),
    ('Temperature', u'$y\xb0C'),
    ('Timestamp', '@Timestamp{%m-%d/%H:%M:%S}')
    ]
    hover.formatters = {
    'Timestamp' : 'datetime'
    }

    plot_chart.line(x='Timestamp', y='Temperature', source=source, line_width=3)
    show(plot_chart)

def main():
    #threading to request data in the background while generating plot
    data_frame, prev_temp = genframe()
    readtemp_thread = threading.Thread(target=readtemp(prev_temp))
    readtemp_thread.start()
    plot(data_frame)


# Reading temp in function to run it in thread because GUI needs to be run in main thread
def readtemp(prev_temp):
    """
    Reads temperature from the ESP8266 endpoint
    """
    prev_temp = prev_temp
    try:
        req_page = requests.get(URL)
    except():
        cur_temp = np.nan
    else:
        soup = BeautifulSoup(req_page.text, 'html.parser')
        cur_temp = soup.b.string[0:5]
    finally:
        if str(cur_temp) != str(prev_temp): #only write to file if temperature has changed since last reading
            cur_time = int(time.time()) #dropping resolution to 1s, saving 7 bytes a line
            with open(FILENAME, 'a') as open_file:
                open_file.write(str(cur_time) + ' ' + str(cur_temp) + '\n')
            print('Fermentation vessel temperature at', cur_time, 'is', cur_temp, u'\xb0C')

if __name__ == "__main__":
    main()
