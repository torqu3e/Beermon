#!/usr/bin/env python3

import sys
import logging
import paho.mqtt.client as mqtt
import pandas as pd
from bokeh.plotting import figure, output_file, show
from bokeh.models import ColumnDataSource, HoverTool


SUB_TOPIC = "ha/_temperature/#"
BROKER_IP = "1.2.3.4"
BROKER_PORT = 1883
CLIENT_ID = 'pymqtt-client'
FILENAME = 'ts_temp.txt'    #file to store temperature data

logging.basicConfig(level=logging.INFO, datefmt='%s', filename='runlog.log', filemode='w', format='%(asctime)s %(levelname)s %(funcName)s - %(message)s')


def genframe():
    """
    Generates dataframe from CSV file containing temperature data
    Returns a smoothed data frame and last temperature reading
    """
    data_frame = pd.read_csv(FILENAME, sep=' ', header=None, names=['Timestamp', 'Temperature'], parse_dates=['Timestamp'], date_parser=lambda epoch: pd.to_datetime(epoch, unit='s'))
    #Experimentally determined window length to provide appropriate graph smoothing,
    # +1 is for conditions where the data frame does not contain enough data hence setting window size to 1
    smoothed_df = data_frame.set_index('Timestamp').interpolate().rolling(window=len(data_frame)//17+1).mean()
    return smoothed_df


def plot():
    """
    Plots a bokeh chart from the generated dataframe
    """
    data_frame = genframe()
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

def readtemp():
    """ Attempts connection to MQTT broker and
    subscribes to topic on successful connect
    """
    client = mqtt.Client(client_id=CLIENT_ID, clean_session=False)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER_IP, BROKER_PORT, 1)
    client.loop_forever()


def on_connect(client, userdata, flags, rc):
    """ Callback function for MQTT client connection event """
    logging.info("Connected with result code " + str(rc))
    client.subscribe(SUB_TOPIC)


def on_message(client, userdata, msg):
    """ Callback function for MQTT client new message event """
    logging.debug(msg.topic + ' ' + msg.payload.decode('utf-8'))
    with open(FILENAME, 'a') as open_file:
        open_file.write(msg.payload.decode('utf-8') + '\n')


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Call as {0} (read|plot)".format(sys.argv[0]))
    elif sys.argv[1] == "read":
        readtemp()
    elif sys.argv[1] == "plot":
        plot()
    else:
        print("Call as {0} (read|plot)".format(sys.argv[0]))
