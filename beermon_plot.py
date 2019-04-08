#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import time
import matplotlib.pyplot as pp
import numpy as np
import datetime
import threading
from scipy.signal import savgol_filter


URL = 'http://192.168.2.55/' #Temperature sensor endpoint
FILENAME = 'ts_temp.txt'    #file to store temperature data

def plot():
    with open(FILENAME, 'r') as f:
        #Converting column 1 to dateobject where temperature is not logged as -1 (error condition)
        ts = [datetime.datetime.fromtimestamp(float(x.split(' ')[0])) for x in f.readlines() if float(x.split(' ')[1]) >= 0]
        f.seek(0) #ugly
        cur_temp = [y.split(' ')[1] for y in f.readlines() if float(y.split(' ')[1]) >= 0]
        #Savgol filter to smooth the noise from sensor data, window and polynomial setting are tweakable
        smoothed_temp = savgol_filter(cur_temp, 131, 3)
    pp.figure(figsize=(30,21))
    pp.title('Frementor Temperature',fontsize=32)
    pp.ylabel(u'\xb0C',fontsize=24)
    pp.yticks(fontsize=20)
    pp.xticks(rotation=270,fontsize=20)
    pp.xlabel('Date-hour',fontsize=24)
    pp.plot(ts,smoothed_temp,linewidth=4) #replace smoothed_temp to cur_temp to see noisy plot
    pp.show()

def main():
    t = threading.Thread(target=readtemp)
    t.start()
    plot()

# Reading temp in function to run it in thread because GUI needs to be run in main thread
def readtemp():
    try:
        r = requests.get(URL)
    except:
        cur_temp = -1
    else:
        soup = BeautifulSoup(r.text, 'html.parser')
        cur_temp = soup.b.string[0:5]
    finally:
        cur_time = time.time()
        with open(FILENAME, 'a') as open_file:
            open_file.write(str(cur_time) + ' ' + str(cur_temp) + '\n')
        print('Fermentation vessel temperature at', cur_time, 'is', cur_temp, '*C')


if __name__ == "__main__":
    main()