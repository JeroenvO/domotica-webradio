#!/usr/bin/python


#Python Raspberry Pi Domotica
#Jeroen van Oorschot 2013
#Server side script to read the mysql db and execute all commands and save logs
#v 0.9
#changelog
#* logging moved to logging.py
#* alarm moved to alarm.py
#* using subprocess ipv os

import GFunc
from time import sleep
import os
import RPi.GPIO as GPIO
import subprocess
import PyDatabase


#import db and connect
# import MySQLdb
#date and time
# import datetime
#time scheduler
#from threading import Timer
#
import time

#####
##Define
checkUpdateTime = 0.1   # every x seconds the database is checked for updates
writeUpdateFactor = 40  # every x updates of checkUpdateTime updates are written

#open the db functions and get the database login values
GF = GFunc.GFunc()

#clear mpc audio for a clean start
subprocess.call(["mpc", "clear"])


######main update function
#Get a value from the database
def checkUpdates(firstTime):
    #var used to check when the db was checked last
    global lastCheck
    ##read updates from database
    db = PyDatabase.PyDatabase(host=GF.DBLogin["host"], user=GF.DBLogin["user"], passwd=GF.DBLogin["passwd"], db=GF.DBLogin["db"])
    #  make query
    columns = ['name', 'value', 'type', 'extra']
    results = None
    if not firstTime:
        #only get updated items
        condition = {
            'settings.type' : 'IS NOT NULL',
            'changetime>' : str(lastCheck)
        }
        results = db.Select(table='settings', columns=columns, condition_and=condition)
        if results is False:
            GF.log("could not execute query: " + db.query,'E')
    else:
        GF.log("first time check, set every value",'N')
        condition = {
            'settings.type' : 'IS NOT NULL'
        }
        results = db.Select(table='settings', columns=columns, condition_and=condition)
        if results is False:
            GF.log("could not execute query: " + db.query,'E')

    lastCheck = str(int(GF.time10())-0*checkUpdateTime)

    if results is not None:
        # apply all changes
        for row in results:
            nm = str(row[0])  # name of setting
            vl = str(row[1])  # value
            tp = row[2]  # type
            xt = str(row[3])  # extra info, pin nr
            # toggling button
            #if tp == "toggle":
                #do something
            # true-false switch for a port
            if tp == "tf" and xt.isdigit():
                try:
                    pn = int(xt)  # pin
                    #value should be 'True' or 'False'
                    if vl == "true":
                        vl = True
                    else:
                        vl = False
                    setOutput(pn, vl)
                except:
                    GF.log("Error, not possible to set " + str(pn) + " to " + str(vl),'E')
            #drop down list items
            elif tp == "list":
                # cursor.execute("SELECT settings.value FROM RPi.settings WHERE name='" + vl + "'")
                #get selected list value.
                data = db.Select(table='settings', columns=['value'], condition_and={ 'name' : vl }, fetchall=False)
                if data is False:
                    GF.log("Could not execute query: " + db.query, 'E')
                result = data.fetchone()
                listItemValue = result[0]
                if nm == "radiostation":  # radio station changed
                    GF.update('geluidbron', 'Raspberry')  # Set amplifier input to radio
                    playRadio(listItemValue)
                elif nm == "geluidbron":  # sound source changed
                    switchSound(listItemValue)  # choose sound source and play that source
                    if vl == "Raspberry":
                        #raspberry sound source chosen
                        resumeRadio()
                    else:
                        pauseRadio()  # stop music playing
            elif tp == "slider":      # slider input
                if nm == "volume":    # change volume
                    smoothVolume(vl)

    db.Close()


##write new values to database
def writeUpdates():
    #qry = "SELECT settings.name from RPi.settings WHERE type='value'";

    #for row in results:
    radioText = getRadioText()
    GF.log("radiotext: " + radioText,'N')
    GF.update('radioText', radioText)


#####GPIO Functions
#set output
def setOutput(pin, value):
    GF.log("tf switch " + pin + " to " + value, 'S')
    #set gpio


#####Sound Functions
#switch audio inputs
def switchSound(channel):
    GF.log("change soundinput to " + channel, 'S')
    #switch the amplifier input to channel
    #some gpio actions


##radio functions
#set radio volume
def setVolume(volume):
    #change value
    GF.log("change volume to " + volume, 'S')
    subprocess.call(["mpc",  "volume", volume])


#change the volume in a few steps for smooth transition
def smoothVolume(reachVolume):
    reachVolume = int(reachVolume)
    try:
        volume = int((subprocess.check_output("mpc").split('\n')[2])[8:10])  # get current volumevolume = 0
    except:
        GF.log("volume not changed",'E')
        return False
    while True:
        try:
            if reachVolume > (volume+10):  # increase volume
                volume += 10
            elif reachVolume < (volume-10):  # decrease volume
                volume -= 10
            else:  # small volume difference
                volume = reachVolume
                setVolume(str(volume))
                break
            setVolume(str(volume))
            sleep(0.1)
        except:
            GF.log("Failed to change volume",'E')


#stop radio
def stopRadio():
    #clear mpc to stop radio playing
    GF.log("mpc stopped",'S')
    subprocess.call(["mpc", "clear"])


#play radio from stream
def playRadio(stream):
    GF.log("radio started: " + stream, 'S')
    #stop and clear current stream
    subprocess.call(["mpc", "clear"])
    #make playlist
    subprocess.call(["mpc", "add", stream])
    #play
    resumeRadio()


#resume a paused radio
def resumeRadio():
    GF.log("mpc resumed", 'S')
    #play list
    subprocess.call(["mpc", "play"])


#pause the radio
def pauseRadio():
    GF.log("mpc paused", 'S')
    #pause radio
    subprocess.call(["mpc", "stop"])


#Get radio text, firs line of mpc output, get text from radio, not supported by all stations
def getRadioText():
    txt = subprocess.check_output("mpc").split('\n')[0]
    a = ['volume:','repeat:','random:','single:','consume:']
    if all(x in txt for x in a):
        #if the radio is not playing
        return 'Radio tekst is niet beschikbaar'
    #otherwise return the radio text
    return txt

#radio functions


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

######MAIN
#check instance, quit if already running
# """
# file_handle = None
# def file_is_locked(file_path):
#     global file_handle
#     file_handle= open(file_path, 'w')
#     try:
#         fcntl.lockf(file_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
#         return False
#     except IOError:
#         return True
#
# file_path = '/var/lock/domotica'
#
# if file_is_locked(file_path):
#     print 'another instance is running exiting now'
#     sys.exit(0)
# else:
#     print 'no other instance is running'
#     for i in range(5):
#         time.sleep(1)
#         print i + 1
# 		"""
##INIT
#setPorts()

##Settings check loop
#check all settings
checkUpdates(True)
writeUpdateCount = 0
GF.log('starting','N')
while True:
    try:
        writeUpdateCount += 1
        #check only updated settings
        try:
            checkUpdates(False)
        except:
            GF.log("error in checkupdates, trying again", 'E')

        #wait for next round
        sleep(checkUpdateTime)

        if writeUpdateCount == writeUpdateFactor:
            try:
                writeUpdates()
                writeUpdateCount = 0
                GF.log("updates written","N")
            except:
                GF.log("error in write, trying again", 'E')
                sleep(5)

    except:
        GF.log("error in main loop, restarting in 10 secs", 'E')
        sleep(10)
