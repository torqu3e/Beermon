# Beermon
Fermentation vessel temperature monitor

This is a two part project which runs on an embedded system (ESP8266) and any high level machine with reasonable processing power (read raspberry pi).

**File descriptions**

Pulls temperature data from the MQTT broker, writes current data to a file and draws a graph of the present data based on mode the code is run in.
<pre>beermon_plot.py</pre> 

e.g. 
<pre>python3 beermon_plot.py read</pre>
starts the MQTT listener and runs it asynchronously
<pre>python3 beermon_plot.py plot</pre>
generates the graph

Space separated epoch and temperature sample data as collected every 5 seconds
<pre>ts_temp.txt</pre>

Sample plot
<pre>plot.png</pre>

Code for the ESP8266. Connect the DS18B20 sensor to a pin with an inbuilt pull up resistor to avoid soldering another component. Configure the parameters, and power the board, connecting the RST pin to the GPIO16 (wake up pin) else the board will only post data the first time and then never wake up from deep sleep.
<pre>beermon_mqtt_client.ino</pre> 

This code has been optimized to improve the power characterstics of the board without adding a lot of extra hacks. It takes an average of ~600 ms to execute everything and go to sleep.

A lot of good reference information about optimizing power utilization is found at https://www.bakke.online/index.php/2017/05/21/reducing-wifi-power-consumption-on-esp8266-part-1/

Onewire library - https://github.com/PaulStoffregen/OneWire

DS18B20 library - https://github.com/milesburton/Arduino-Temperature-Control-Library

To do: Docker compose file for MQTT broker.
