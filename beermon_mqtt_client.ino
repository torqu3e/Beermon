#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <EasyNTPClient.h>
#include <WiFiUdp.h>


// Data wire is plugged into pin 2 on the Arduino
#define ONE_WIRE_BUS 2
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

// Update these with values suitable for your setup.
const char* SSID = "WIFI_SSID";
const char* PASSWORD = "WIFI_PASSWORD";
const char* MQTT_SERVER = "1.2.3.4";
const char* TOPIC_PREFIX = "ha/_temperature/";
const char* CLIENTID = "ESP8266TempMon";

// NTP server hostname. TZ_OFFSET is timezone difference in seconds e.g. IST is +5:30 so 5*60*60 + 30*60 = 19800. Similarly negative values.
const char* NTP_SERVER = "ca.pool.ntp.org";
uint16_t TZ_OFFSET = 0;

//Set sleept interval in microseconds
uint32_t SLEEP_INT = 6e6;

// Global variables - DO NOT EDIT
unsigned long timeNow = 0;
const char* suffix = "";

WiFiUDP udp;
EasyNTPClient ntpClient(udp, NTP_SERVER, TZ_OFFSET);
WiFiClient espClient;
PubSubClient client(espClient);

void setup_wifi() {
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(SSID);
  WiFi.persistent(false);
  WiFi.mode(WIFI_STA);
  WiFi.begin(SSID, PASSWORD);

  while (WiFi.status() != WL_CONNECTED) 
  {
    delay(5);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("WiFi connected. IP address: ");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect
    if (client.connect(CLIENTID)) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 0.5 seconds");
      delay(500);
    }
  }
}

void publishMsg(unsigned long timeNow, float temp, String suffix) {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
  String payload = String(timeNow) + " " + String(temp);
  String topic_id = TOPIC_PREFIX + suffix;
  client.publish(topic_id.c_str(), String(payload).c_str());
  delay(1);
  Serial.print("Published : ");
  Serial.print(payload);
  Serial.print(" to ");
  Serial.println(topic_id);
}


void setup()
{
  Serial.begin(115200); 
  sensors.begin();
  sensors.setResolution(12);
  sensors.requestTemperatures();
  uint8_t devCount = sensors.getDeviceCount();
  
  client.setServer(MQTT_SERVER, 1883);
  setup_wifi();
  while(timeNow == 0) { 
    timeNow = ntpClient.getUnixTime();
    if (timeNow == 0) {
      delay(100);
    }
  }
  
  for (uint8_t i = 0; i < devCount; i++){
    publishMsg(timeNow, sensors.getTempCByIndex(i), String(i));
  }

  Serial.print("Time taken(ms) : ");
  Serial.println(millis());
  ESP.deepSleep(SLEEP_INT);
}

void loop(){
}
