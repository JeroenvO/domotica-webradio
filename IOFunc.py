#!/usr/bin/python3

__author__ = 'JvO'

#Python Raspberry Pi Domotica
#Jeroen van Oorschot 2014
#IO functions used in Raspberry pi domotica

import GFunc
#import sys
#print(sys.path)
#import RPi.GPIO as GPIO
import wiringpi2 as wp
import struct
#open the db functions and get the database login values
GF = GFunc.GFunc()
#globals for mcp230171 wirinpi

#init the IO
address = 0x20 #23017 for audio and display
OUTPUT = 1
INPUT = 0
PB1 = 64  # pinbase for first (audio and display) expander
PB2 = 16+PB1 #pinbase for relay control expander
OUTPUT_PINS_1 = [64,65, 69,70,71,72,73,74,75,76,77,78,79]
INPUT_PINS_1 = [66,67,68]

OUTPUT_PINS_2 = [80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95]
INPUT_PINS_2 = []
class IOFunc():

    #initialise all IO
    def __init__(self):
        wp.wiringPiSetup()

        #left 23017, for audio
        wp.mcp23017Setup( PB1,0x20)
        for pin in OUTPUT_PINS_1:
            wp.pinMode(pin,OUTPUT)
        for pin in INPUT_PINS_1:
            wp.pinMode(pin, INPUT)

        #right 23017 for 230v switching
        wp.mcp23017Setup( PB2,0x21)
        for pin in OUTPUT_PINS_2:
            wp.pinMode(pin,OUTPUT)
        for pin in INPUT_PINS_2:
            wp.pinMode(pin, INPUT)

        #display

      #  wp.lcdInit(2, 16, 8, rs, strb, d0, d1, d2, d3, d4, d5, d6, d7)


    def setSoundInput(self, channel):
        if channel > 3 or channel < 0:
            return False

        if channel == 0:
            channel = 3
        channel = bin(channel)

        if(len(channel)<4):  # channel == 1 or == 0
            bit0 = 0
            bit1 = 1  # int(channel[2])
        else:
            bit0 = int(channel[2])
            bit1 = int(channel[3])
        wp.digitalWrite(PB1+0, bit1)
        wp.digitalWrite(PB1+1, bit0)


        #set output
    def setOutput(self, pin, value):
        if(value == 1 or value == 0):
            GF.log("tf switch " + str(pin) + " to " + str(value), 'S')
            #set gpio
            try:

                wp.digitalWrite(pin, value)
            except:
                GF.log("Error in writing output pin");
        else:
            GF.log("Invalid value")
