 /*
 * WebSocketClient.ino
 * 
 *  Created on: 24.05.2015
 * Jeroen van Oorschot 2015-2017
 * Using https://github.com/Links2004/arduinoWebSockets and https://github.com/adafruit/Adafruit-PWM-Servo-Driver-Library
 * 
 */

#include <Arduino.h>

#include <ESP8266WiFi.h>
#include <ESP8266WiFiMulti.h>

#include <WebSocketsClient.h>

#include <Hash.h>

// this file contains defines for 'ssid' and 'pass' to connect to wifi.
#include "password.h"

ESP8266WiFiMulti WiFiMulti;
WebSocketsClient webSocket;


#define USE_SERIAL Serial

//number of chars between start of message and array of color values
#define MSG_OFFSET 28


#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

// called this way, it uses the default address 0x40
Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();
// you can also call it with a different address you want
//Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver(0x41);

void parseInput(char* payloadChar){
  uint16_t rgb[3]={0};
  String RGB[3];
  String payload = String(payloadChar);
  //format: "S{\"keuken_rgb\": [\"colorRGB\",[%f,%f,%f]]}",r,g,b);
  //[0.616, 0.119, 0.59]]}
  uint8_t startR = MSG_OFFSET+2;
  uint8_t startG = payload.indexOf(',',startR+1);
  uint8_t startB = payload.indexOf(',',startG+1);
  uint8_t endB = payload.indexOf(']',startB);
  RGB[0] = payload.substring(startR,startG);
  RGB[1] = payload.substring(startG+2,startB);
  RGB[2] = payload.substring(startB+2,endB);
/*  USE_SERIAL.print("\nR");
  USE_SERIAL.print(RGB[0]);
  USE_SERIAL.print("\nG");
  USE_SERIAL.print(RGB[1]);  
  USE_SERIAL.print("\nB");
  USE_SERIAL.print(RGB[2]);  
  USE_SERIAL.print("\n");
*/
  //apply
  for(int i=0;i<3;i++){
    rgb[i] = (int) (RGB[i].toFloat()*4095);
    //USE_SERIAL.print("\n");
    //USE_SERIAL.print(rgb[i]);  
    //USE_SERIAL.print("\n");
    pwm.setPWM(i, 0, rgb[i] );
    pwm.setPWM(i+3, 0, rgb[i] );
  }
}
void webSocketEvent(WStype_t type, uint8_t * payload, size_t lenght) {


    switch(type) {
        case WStype_DISCONNECTED:
  //          USE_SERIAL.printf("[WSc] Disconnected!\n");
            break;
        case WStype_CONNECTED:
            {
    //            USE_SERIAL.printf("[WSc] Connected to url: %s\n",  payload);
                webSocket.sendTXT("{\"username\":\"espKeuken\",\"password\":\"\"}");
                //enableAll();
          // send message to server when Connected
        //webSocket.sendTXT("Connected");
            }
            break;
        case WStype_TEXT:
     //       USE_SERIAL.printf("[WSc] get text: %s\n", payload);
            //Format: S{"keuken_rgb": ["colorRGB", [0.7884, 0.38552759999999997, 0.212868]]}
            if(strncmp((char*)payload,"S{\"keuken_rgb\": [\"colorRGB\",",MSG_OFFSET)==0){
      //        USE_SERIAL.printf("Keuken RGB Received");
              parseInput((char*)payload);
            }
            break;
        case WStype_BIN:
        //    USE_SERIAL.printf("[WSc] get binary lenght: %u\n", lenght);
          //  hexdump(payload, lenght);

            // send data to server
            // webSocket.sendBIN(payload, lenght);
            break;
    }

}

void setup() {
  /*SERIAL DEBUG POEP*/
  //wait for boot
  delay(3000);
  /*
    // USE_SERIAL.begin(921600);
    USE_SERIAL.begin(115200);

    //Serial.setDebugOutput(true);
    USE_SERIAL.setDebugOutput(true);

    USE_SERIAL.println();
    USE_SERIAL.println();
    USE_SERIAL.println();

      for(uint8_t t = 4; t > 0; t--) {
          USE_SERIAL.printf("[SETUP] BOOT WAIT %d...\n", t);
          USE_SERIAL.flush();
          delay(1000);
      }
*/
    /*PIN SETTINGS*/
    //esp power source keep alive
    //pinMode(0,OUTPUT); 
    //input to read the second push of button
    //pinMode(2,INPUT); 
    //keep the power supply to the esp
    //digitalWrite(0,HIGH); 
  
    /*for ESP, the i2c pins*/
    Wire.pins(0,2);
  
    //PWM for 9685 via i2c
    pwm.begin();
    pwm.setPWMFreq(1600);  // This is the maximum PWM frequency

    /*WIFI SETTINGS*/
    WiFiMulti.addAP(ssid, pass);

    while(WiFiMulti.run() != WL_CONNECTED) {
        delay(1000);
        //reconnect
    }

    /*WEBSOCKET SETTINGS*/
    webSocket.begin("192.168.1.104", 600);
    webSocket.onEvent(webSocketEvent);
}

void loop() {
    webSocket.loop();
    //checkButton();
    yield();
}
