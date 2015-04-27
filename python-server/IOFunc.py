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

import time, math

import struct
#open the db functions and get the database login values
GF = GFunc.GFunc()
#globals for mcp230171 wirinpi

#init the IO
address = 0x20 #23017 for audio and display
OUTPUT = 1
INPUT = 0
PUD_UP = 2  # pull up resistor
PB1 = 64  # pinbase for first (audio and display) expander
PB2 = 16+PB1 #pinbase for relay control expander
OUTPUT_PINS_1 = [64,65,66, 69,70,71,72,73,74,75,76,77,78,79]
INPUT_PINS_1 = [67,68]

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
            wp.pullUpDnControl(pin,PUD_UP)
            wp.pinMode(pin, INPUT)


        #display
        wp.digitalWrite(70,0)  # write mode
        self.display1 = wp.lcdInit(2,16,8, 71,69,72,73,74,75,76,77,78,79) #connected to first expander
        wp.lcdClear(self.display1)


        #pwm driver
        self.pwm = PWM()
        self.pwm.setPWMFreq(200)



    def setSoundInput(self, channel):
        if channel > 3 or channel < 0:  # impossible channels
            return False

        if channel == 0:
            channel = 3           # set channel to raspberry
            self.setOutput(95,0)  # disable amplifier
        else:
            self.setOutput(95,1)  # enable amplifier

        channel = bin(channel)

        if(len(channel)<4):  # channel == 1 or == 0
            bit0 = 0
            bit1 = 1
        else:
            bit0 = int(channel[2])
            bit1 = int(channel[3])
        wp.digitalWrite(PB1+0, bit1)
        wp.digitalWrite(PB1+1, bit0)


        #set output
    def setOutput(self, pin, value):
        if((value == 1 or value == 0) and ( pin in OUTPUT_PINS_1 or pin in OUTPUT_PINS_2)):
            #GF.log("tf switch " + str(pin) + " to " + str(value), 'S')
            #set gpio
            try:
                wp.digitalWrite(pin, value)
            except:
                GF.log("Error in writing output pin");
        else:
            GF.log("Invalid value")

    #clean the display and write a string
    def displayWrite(self,string):
        string=string[0:32]
        #GF.log("writing "+string+" to lcd",'D')
        wp.lcdClear(self.display1)
        wp.lcdHome(self.display1)
        wp.lcdPrintf(self.display1, string)

    #read buttons next to lcd
    def readButtons(self):
        back = wp.digitalRead(67)
        front = wp.digitalRead(68)
        return [front, back]

    #set the dutycycle of a pwm output
    def setPWM(self, pin, dc):
        #GF.log("writing "+str(dc)+" to pwm "+str(pin),"D")
        self.pwm.setPWM(pin, dc*4096.0)

class PWM(object):
    i2c = None

    # Registers/etc.
    __MODE1              = 0x00
    __MODE2              = 0x01
    __SUBADR1            = 0x02
    __SUBADR2            = 0x03
    __SUBADR3            = 0x04
    __PRESCALE           = 0xFE
    __LED0_ON_L          = 0x06
    __LED0_ON_H          = 0x07
    __LED0_OFF_L         = 0x08
    __LED0_OFF_H         = 0x09
    __ALL_LED_ON_L       = 0xFA
    __ALL_LED_ON_H       = 0xFB
    __ALL_LED_OFF_L      = 0xFC
    __ALL_LED_OFF_H      = 0xFD

  # Bits
    __RESTART            = 0x80
    __SLEEP              = 0x10
    __ALLCALL            = 0x01
    __INVRT              = 0x10
    __OUTDRV             = 0x04

    @staticmethod
    def getPiI2CBusNumber():
        """
        Returns the I2C bus number (/dev/i2c-#) for the Raspberry Pi being used.

        Courtesy quick2wire-python-api
        https://github.com/quick2wire/quick2wire-python-api
        """
        try:
            with open('/proc/cpuinfo','r') as f:
                for line in f:
                    if line.startswith('Revision'):
                        return 1
        except:
            return 0

    @staticmethod
    def sanitize_int(x):
        if x < 0:
            return 0
        elif x > 4095:
            return 4095
        else:
            return int(x)

    def __init__(self, address=0x40, debug=False):
        """
        Setup a Pulse-Width Modulation object, for controlling an I2C device.

        Parameters
        address: The address of the I2C device in hex.
                 Find using `i2cdetect -y [0|1]`
        debug: Boolean value specifying whether or not to print debug messages.
        """
        wp.wiringPiSetupSys()
        self.i2c = wp.I2C()
        self.fd = self.i2c.setupInterface('/dev/i2c-' + str(PWM.getPiI2CBusNumber()), address)
        self.address = address
        self.debug = debug
        if (self.debug):
            print("Got an fd: %d" % self.fd)
            print("Reseting PCA9685")
        self.setAllPWM(0, 0)
        #self.i2c.writeReg8(self.fd, self.__MODE1, 0x00)
        self.i2c.writeReg8(self.fd, self.__MODE2, self.__OUTDRV) #set as totempole
        ###############test###self.i2c.writeReg8(self.fd, self.__MODE2, self.__INVRT) #set non-inverted
        #self.i2c.writeReg8(self.fd, self.__MODE1, self.__ALLCALL)
        time.sleep(0.005)                                       # wait for oscillator

        mode1 = self.i2c.readReg8(self.fd, self.__MODE1)
        mode1 = mode1 & ~self.__SLEEP                 # wake up (reset sleep)
        self.i2c.writeReg8(self.fd, self.__MODE1, mode1)
        time.sleep(0.005)

    def setPWMFreq(self, freq):
        """
        Sets the PWM frequency.

        Parameters
        freq: The frequency (int) in hz.
        """
        prescaleval = 25000000.0 # 25MHz
        prescaleval /= 4096.0    # 12-bit
        prescaleval /= float(freq)
        prescaleval -= 1.0
        if (self.debug):
            print("Setting PWM frequency to %d Hz" % freq)
            print("Estimated pre-scale: %d" % prescaleval)
        prescale = math.floor(prescaleval + 0.5)
        if (self.debug):
            print("Final pre-scale: %d" % prescale)

        oldmode = self.i2c.readReg8(self.fd, self.__MODE1);
        newmode = (oldmode & 0x7F) | 0x10 # sleep
        if (self.debug):
            print("oldmode: %d" % oldmode)
            print("newmode: %d" % newmode)
        self.i2c.writeReg8(self.fd, self.__MODE1, newmode) # go to sleep
        self.i2c.writeReg8(self.fd, self.__PRESCALE, int(math.floor(prescale)))
        self.i2c.writeReg8(self.fd, self.__MODE1, oldmode)
        time.sleep(0.005)
        self.i2c.writeReg8(self.fd, self.__MODE1, oldmode | 0x80)

    def setPWM(self, channel, val):
        """
        Sets a single PWM channel.

        Parameters
        channel: The channel (int)
        val: The value to set it to. Between 0 and 4095.
        """
        val = self.sanitize_int(val)
        self.i2c.writeReg8(self.fd, self.__LED0_ON_L+4*channel, 0)
        self.i2c.writeReg8(self.fd, self.__LED0_ON_H+4*channel, 0)
        self.i2c.writeReg8(self.fd, self.__LED0_OFF_L + 4 * channel, val & 0xFF)
        self.i2c.writeReg8(self.fd, self.__LED0_OFF_H + 4 * channel, val >> 8)

    def setAllPWM(self, on, off):
        "Sets a all PWM channels"
        self.i2c.writeReg8(self.fd, self.__ALL_LED_ON_L, on & 0xFF)
        self.i2c.writeReg8(self.fd, self.__ALL_LED_ON_H, on >> 8)
        self.i2c.writeReg8(self.fd, self.__ALL_LED_OFF_L, off & 0xFF)
        self.i2c.writeReg8(self.fd, self.__ALL_LED_OFF_H, off >> 8)

    def readPWM(self, channel):
        """
        Returns the value of a single PWM channel.

        Parameters
        channel: The channel (int)
        """
        low  = self.i2c.readReg8(self.fd, self.__LED0_OFF_L + 4 * channel)
        high = self.i2c.readReg8(self.fd, self.__LED0_OFF_H + 4 * channel)
        return (high << 8) + low