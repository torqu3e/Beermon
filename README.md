# Beermon
Fermentation vessel temperature monitor

This is a two part project which runs on an embedded system (ESP8266) and any high level machine with reasonable processing power.

**File descriptions**

<pre>beermon_plot.py</pre> pulls temperature data from the ESPP8266 board, parses the HTML output, writes current data to a file and draws a graph of the present data.

<pre>sensor_page.txt</pre> expected sensor board output 

<pre>ts_temp.txt</pre> space separated epoch and temperature sample data as collected every 5 seconds

<pre>plot.png</pre> sample plot

<pre>HTTP_DS18B20.ino</pre> Code for the ESP8266. DS18B20 sensor is wired to pin D3 since it has a builtin 10k pullup resistor, letting you skip using one extra compoonent. The page autorefreshes every 1 second to show the latest temperature without manual intervention.

Sensor board code is reused from https://www.hackster.io/adachsoft_com/esp8266-temperature-sensors-ds18b20-with-http-server-5509ac

Onewire library - https://github.com/PaulStoffregen/OneWire

DS18B20 library - https://github.com/milesburton/Arduino-Temperature-Control-Library
