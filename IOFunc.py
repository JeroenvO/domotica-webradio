#!/usr/bin/python3

__author__ = 'JvO'

#Python Raspberry Pi Domotica
#Jeroen van Oorschot 2014
#IO functions used in Raspberry pi domotica

import GFunc

import PyDatabase
#date and time
import datetime
import time
import json
import socket
import Adafruit_MCP230XX
import Adafruit_I2C



class IOFunc():
    #initialise all IO
    def __init__(self):
        pass

    ########GPIO

    #initialize all ports
    def setPorts():
        GPIO.setmode(GPIO.BCM)
        inputs = [4]
        outputs = [5, 8, 28]  # get these from db in the future
        for input in inputs:
            GPIO.setup(input, GPIO.IN)

        for output in outputs:
            GPIO.setup(output, GPIO.OUT)
