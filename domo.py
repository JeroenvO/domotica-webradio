#!/usr/bin/python


#Python Raspberry Pi Domotica
#Jeroen van Oorschot 2013
#Server side script to read the mysql db and execute all commands and save logs
#v 0.9
#changelog
#* logging moved to logging.py
#* alarm moved to alarm.py
#* using subprocess ipv os


from time import sleep

import os

import RPi.GPIO as GPIO

import subprocess
#import db and connect
import MySQLdb
#date and time
import datetime
#time scheduler
#from threading import Timer
#
import time

#####
##Define
checkUpdateTime = 0.1   # every x seconds the database is checked for updates
writeUpdateFactor = 40  # every x updates of checkUpdateTime updates are written

#time in 10*microseconds
def time10():
    return str(int(round(time.time() * 100)))


#clear mpc audio
subprocess.call(["mpc", "clear"])


######main update function
#Get a value from the database
def checkUpdates(firstTime):
    ##read updates from database

    #create connection and cursor
    con = connectDB()
    cursor = con.cursor()
    #make query
    qry = "SELECT settings.name, settings.value, settings.type, settings.extra from RPi.settings WHERE type IS NOT NULL"
    if not firstTime:
        #only get updated items
        qry = qry + " AND changetime>='" + lastCheck + "'"
    global lastCheck
    lastCheck = str(int(time10())-checkUpdateTime)
    #print('lastCheck: ' + lastCheck)
    #execute query
    cursor.execute(qry)
    #fetch results
    results = cursor.fetchall()
    #Get the time, set lastcheck
    for row in results:
        nm = str(row[0])  # name of setting
        vl = str(row[1])  # value
        tp = row[2]  # type
        xt = str(row[3])  # extra info, pin nr
        # toggling button
        if tp == "toggle":
            print("toggle " + nm)
            #do something
        # true-false switch for a port
        elif tp == "tf" and xt.isdigit():
            print("tf switch " + nm + " to " + vl)
            try:
                pn = int(xt)  # pin
                #value should be 'True' or 'False'
                if vl == "true":
                    vl = True
                else:
                    vl = False
                setOutput(pn, vl)
            except:
                print("Error, not possible to set " + str(pn) + " to " + str(vl))
        #drop down list items
        elif tp == "list":
            print("list " + nm + " to " + vl)
            cursor.execute("SELECT settings.value FROM RPi.settings WHERE name='" + vl + "'")
            result = cursor.fetchone()
            listItemValue = result[0]
            if nm == "radiostation":  # radio station changed
                writeDB('geluidbron', 'Raspberry')  # Set amplifier input to radio
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

    #close cursor and connection
    cursor.close()
    con.close()


def writeDB(name, value):
    try:
        con = connectDB()
        cursor = con.cursor()
        qry2 = "UPDATE settings set value='" + con.escape_string(value) + "', changetime='" + time10() + "'  WHERE name='" + con.escape_string(name) + "'"
        cursor.execute(qry2)
        cursor.close()
        con.close()
    except:
        print('writeDB failed, qry: ' + qry2)


def writeUpdates():
    ##write new values to database
    #create connection and cursor

    #make query
    #qry = "SELECT settings.name from RPi.settings WHERE type='value'";
    #execute query
    #cursor.execute(qry)
    #fetch results
    #results = cursor.fetchall()

    #for row in results:
    radioText = getRadioText()
    print("radiotext: " + radioText)
    writeDB('radioText', radioText)


#####GPIO Functions
#set output
def setOutput(pin, value):
    print("set " + pin + " to " + value)
    #set gpio


#####Sound Functions
#switch audio inputs
def switchSound(channel):
    print("change soundinput to " + channel)
    #switch the amplifier input to channel
    #some gpio actions


##radio functions
#set radio volume
def setVolume(volume):
    #change value
    print("volume changed to " + volume)
    subprocess.call(["mpc",  "volume", volume])


#change the volume in a few steps for smooth transition
def smoothVolume(reachVolume):
    reachVolume = int(reachVolume)
    try:
        volume = int((subprocess.check_output("mpc").split('\n')[2])[8:10])  # get current volumevolume = 0
    except:
        print("not possible to read volume, please try again")
        return False
    print("thisvolume = " + str(volume))
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
            print("not possible to set smooth volume")


#stop radio
def stopRadio():
    #clear mpc to stop radio playing
    print("radio stopped")
    subprocess.call(["mpc", "clear"])


#play radio from stream
def playRadio(stream):
    print("start radio playing")
    #stop and clear current stream
    subprocess.call(["mpc", "clear"])
    #make playlist
    subprocess.call(["mpc", "add", stream])
    #play
    resumeRadio()


#resume a paused radio
def resumeRadio():
    print("resume radio")
    #play list
    subprocess.call(["mpc", "play"])


#pause the radio
def pauseRadio():
    print("pause radio")
    #pause radio
    os.system("mpc stop")


#Get radio text, firs line of mpc output
def getRadioText():
    #get text from radio, not supported by all stations
    return subprocess.check_output("mpc").split('\n')[0]

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


"""	
########LOG FUNCTIONS
#write a value in a log
def writeLog(table,value):
	#create connection and cursor
	con = connectDB()
	cursor = con.cursor()
	#write 'value' in 'table'
	cursor.execute("INSERT INTO "+table+" (value, timestamp) VALUES ('"+value+"', NOW())")
	#close cursor
	cursor.close()
	#close con
	con.close()

#cpu temp logger
def logCPUTemp():
	proc = subprocess.Popen(["/opt/vc/bin/vcgencmd measure_temp"], stdout=subprocess.PIPE, shell=True)
	(out, err) = proc.communicate()	
	temp = out[5:7]
	print "CPU Temperature = "
	print temp
	writeLog("log_CPUTemp",temp)

#called by scheduler, calls logging functions
def fillLogs():
	logCPUTemp()
	print "logging finished"
	#every half hour, 1800secs
	Timer(1800, fillLogs, ()).start()
"""


######DB
def connectDB():
    while True:
        try:
            con = MySQLdb.connect(host="localhost", # your host, usually localhost
                                  user="root", # your username
                                  passwd="RPIJvO262SADF", # your password
                                  db="RPi") # name of the data base
            #autocommit changes and so autorefresh db
            #print "db connected"
            con.autocommit(True)
            #print "autocommit enabled"
            break
        except:
            print
            "Error connecting to MYSQL, retrying"
            sleep(2)
    return con

######MAIN
#check instance, quit if already running
"""
file_handle = None
def file_is_locked(file_path):
    global file_handle 
    file_handle= open(file_path, 'w')
    try:
        fcntl.lockf(file_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return False
    except IOError:
        return True

file_path = '/var/lock/domotica'

if file_is_locked(file_path):
    print 'another instance is running exiting now'
    sys.exit(0)
else:
    print 'no other instance is running'
    for i in range(5):
        time.sleep(1)
        print i + 1
		"""
##INIT
#setPorts()

##Settings check loop
#check all settings
checkUpdates(True)
writeUpdateCount = 0
print('starting')
while True:
    try:
        writeUpdateCount += 1
        #check only updated settings
        try:
            checkUpdates(False)
        except:
            print("check updates crashed, restarting")
        #wait for next round
        sleep(checkUpdateTime)
        if writeUpdateCount == writeUpdateFactor:
            try:
                writeUpdates()
                writeUpdateCount = 0
                print("updates written")
            except:
                print("error in write, trying again")
                sleep(5)

    except:
        print("something went wrong, restarting in 10 secs")
        sleep(10)
