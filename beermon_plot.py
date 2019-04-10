#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import time
import matplotlib.pyplot as pp
import numpy as np
import datetime
import threading
import pandas as pd
from bokeh.plotting import figure, output_file, show
from bokeh.models import ColumnDataSource, HoverTool

URL = 'http://192.168.2.55/' #Temperature sensor endpoint
FILENAME = 'ts_temp.txt'    #file to store temperature data

def genframe():
    df = pd.read_csv(FILENAME,sep=' ', header=None, names=['Timestamp','Temperature'], parse_dates=['Timestamp'], date_parser=lambda epoch: pd.to_datetime(epoch, unit='s'))
    smoothed_df = df.set_index('Timestamp').interpolate(method='polynomial',order=3)
    prev_temp = df['Temperature'].iloc[-1]
    return(smoothed_df, prev_temp)
    
def plot(df):
    df = df
    source = ColumnDataSource(df)
    output_file("output.html")

    p = figure(plot_width=1200,plot_height=800,sizing_mode='scale_height',x_axis_type='datetime',title=u'Fermentor Temperature \xb0C',tools='pan,wheel_zoom,hover,save,reset')

    hover = p.select(dict(type=HoverTool))
    hover.tooltips = [
    ("index", "$index"),
    ('Temperature', u'$y\xb0C'),
    ('Timestamp', '@Timestamp{%m-%d/%H:%M:%S}')
    ]
    hover.formatters = {
    'Timestamp' : 'datetime'
    }

    p.line(x='Timestamp',y='Temperature',source=source,line_width=3)
    show(p)

def main():
    #threading to request data in the background while generating plot
    df, prev_temp = genframe()
    rt = threading.Thread(target=readtemp(prev_temp))
    rt.start()
    plot(df)

# Reading temp in function to run it in thread because GUI needs to be run in main thread
def readtemp(prev_temp):
    prev_temp = prev_temp
    try:
        r = requests.get(URL)
    except:
        cur_temp = np.nan
    else:
        soup = BeautifulSoup(r.text, 'html.parser')
        cur_temp = soup.b.string[0:5]
    finally:
        if str(cur_temp) != str(prev_temp): #only write to file if temperature has changed since last reading
            cur_time = int(time.time()) #dropping resolution to 1s, saving 7 bytes a line
            with open(FILENAME, 'a') as open_file:
                open_file.write(str(cur_time) + ' ' + str(cur_temp) + '\n')
            print('Fermentation vessel temperature at', cur_time, 'is', cur_temp, u'\xb0C')

if __name__ == "__main__":
    main()
