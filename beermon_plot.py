#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import time
import matplotlib.pyplot as pp
import numpy as np
import datetime
import threading
import pandas as pd

URL = 'http://192.168.2.55/' #Temperature sensor endpoint
FILENAME = 'ts_temp.txt'    #file to store temperature data

def plot():
    df = pd.read_csv(FILENAME,sep=' ', header=None, names=['Timestamp','Temperature'], parse_dates=['Timestamp'], date_parser=lambda epoch: pd.to_datetime(epoch, unit='s')).set_index('Timestamp').interpolate().rolling(window=131,center=True).mean()
    df.plot(kind='line',y='Temperature',figsize=(30,21),linewidth=4,fontsize=20,rot=45)
    pp.ylabel(u'\xb0C',fontsize=24)
    pp.xlabel('Timestamp',fontsize=24)
    pp.title(label='Fermentor Temperature',fontsize=32)
    pp.show()

def main():
    #threading to request data in the background while generating plot
    t = threading.Thread(target=readtemp)
    t.start()
    plot()

# Reading temp in function to run it in thread because GUI needs to be run in main thread
def readtemp():
    try:
        r = requests.get(URL)
    except:
        cur_temp = np.nan
    else:
        soup = BeautifulSoup(r.text, 'html.parser')
        cur_temp = soup.b.string[0:5]
    finally:
        cur_time = int(time.time()) #dropping resolution to 1s, saving 7 bytes a line
        with open(FILENAME, 'a') as open_file:
            open_file.write(str(cur_time) + ' ' + str(cur_temp) + '\n')
        print('Fermentation vessel temperature at', cur_time, 'is', cur_temp, u'\xb0C')


if __name__ == "__main__":
    main()
