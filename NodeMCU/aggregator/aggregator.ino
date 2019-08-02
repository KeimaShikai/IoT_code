#include "data.h"
#include <vector>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <ESP8266WiFi.h>

//SETUP block
const char* ssid = "WIFI-F619";
const char* password = "4871487675";
IPAddress ip(192,168,1,10);  //static IP
IPAddress gateway(192,168,1,1);
IPAddress subnet(255,255,255,0);

//Global things block
WiFiServer aggregator(8888);
LiquidCrystal_I2C lcd(0x27,16,2);
std::vector<Data> device_range;

bool is_in_range(int index)
{
  for (auto i : device_range) {
    if ((i.get_index() == index) || (index == 0)) {
      return true;
    }
  }
  return false;
}

void setup(void) {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  WiFi.config(ip, gateway, subnet);
  Serial.println("");
  // Wait for the connection
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("Connected to ");
  Serial.println(ssid);
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  aggregator.begin();
  Wire.begin(4,5); //4 - SDA, 5 - SCL    
  lcd.begin(4,5); //4 - SDA, 5 - SCL                    
  lcd.backlight(); //Lit the display
  lcd.print("Oh, shit!");
  lcd.setCursor(0, 1);
  lcd.print("Here we go again!");
}

void loop(void) {
  // Check if a client has connected
  WiFiClient client = aggregator.available();
  if (!client) {
    return;
  }

  // Wait until the client sends some data
  Serial.println("new client");
  unsigned long timeout = millis() + 3000;
  while (!client.available() && millis() < timeout) {
    delay(1);
  }
  if (millis() > timeout) {
    Serial.println("timeout");
    client.flush();
    client.stop();
    return;
  }

  // Read the line of the request
  String req = client.readStringUntil('\r');
  Serial.println(req);
  client.flush();

  // Find all separators
  int a[4], j = 0;
  for (int i = 0; i < req.length(); ++i) {
    if (req.charAt(i) == '|') {
      a[j] = i;
      ++j;
    }
  }

  // Convert number of the current connected device into int
  String temp;
  temp = req.substring(a[0]+1, a[1]);
  int deviceIndex = temp.toInt();

  // Convert current value of temperature into float
  temp = req.substring(a[1]+1, a[2]);
  char *T = new char[a[1] - a[0] - 1];
  temp.toCharArray(T, temp.length());
  float temperature = atof(T);

  // Convert current value of humidity into float
  temp = req.substring(a[2]+1, a[3]);
  char *H = new char[a[3] - a[2] - 1];
  temp.toCharArray(H, temp.length());
  float humidity = atof(H);

  // Check whether this device was added into range or not
  // If it wasn't added - initialised new object of Data class
  // And add it to the range-vector
  // Otherwise, find index of current connected device
  // And update its data
  if (!is_in_range(deviceIndex)) {
    Data new_one(deviceIndex, temperature, humidity);
    device_range.emplace_back(new_one);
    Serial.print("New device is attached! Its # is ");
    Serial.println(deviceIndex);
  }
  else
  {
    if ((temperature != 0.0) && (humidity != 0.0)) {
      int cur_device;
      for (int i = 0; i < device_range.size(); ++i) {
        if (device_range.at(i).get_index() == deviceIndex) {
          cur_device = i;
          Serial.println("I already know this one!");
        }
      }
      device_range.at(cur_device).update(temperature, humidity);
      Serial.println("Data updated!");
    }
  }

  delete T;
  delete H;

  // Calculate average values for T and H for all existing devices
  float avr_T_value = 0;
  float avr_H_value = 0;
  for (int i = 0; i < device_range.size(); ++i) {
    avr_T_value += device_range.at(i).get_avr_T();
    avr_H_value += device_range.at(i).get_avr_H();
  }
  avr_T_value = avr_T_value / device_range.size();
  avr_H_value = avr_H_value / device_range.size();
  Serial.print("avr_T = ");
  Serial.println(avr_T_value);
  Serial.print("avr_H = ");
  Serial.println(avr_H_value);

  //Update LCD output
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("average T:");
  lcd.print(avr_T_value);
  lcd.print("C");
  lcd.setCursor(0, 1);
  lcd.print("average H:");
  lcd.print(avr_H_value);
  lcd.print("%");
  
  // The client will actually be disconnected
  // when the function returns and 'client' object is detroyed
  Serial.println("Disconnected!");
  Serial.println();
}
