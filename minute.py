#!/usr/bin/python3

__author__ = 'JvO'

#Python Raspberry Pi Domotica
#Jeroen van Oorschot 2013
#Functions that run every minute like alarms and timers

import GFunc

import PyDatabase
#date and time
import datetime
import time
import json
import socket


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

GF = GFunc.GFunc()

# start an alarm, alarmNum = 1,2,3 or 4
def startAlarm(alarmNum,):
    #start alarm
    GF.log("Alarm " + str(alarmNum) + " turning on now", 'N')
    send(json.dumps({'volume' : str( settings['a' + alarmNum + '_alarmVol'][1] ), 'geluidbron' : 'Raspberry'}))


# check alarms
def checkAlarms():
    for i in range(1,5):  # for each alarm that is turned on
        alarmNum = str(i)
        #print(alarmNum)
        if settings['a' + alarmNum + '_alarmOn'][1] == 'true':
            at = settings['a' + alarmNum + '_alarmTime'][1].split(':')
            GF.log('alarm ' + alarmNum + ' is being checked'+str(at), "D")
            if int(at[0]) == th and int(at[1]) == tm:  # time match, alarm should ring now
                alarmDays = settings['a' + alarmNum + '_alarmDays'][1]
                # check if it is an one-time alarm, meaning no repeating days are selected
                if alarmDays == 'fffffff':   # everything false oneTimeAlarm = True
                    try:
                        send(json.dumps({'a' + str(alarmNum) + '_alarmOn' : 'false'}))
                        GF.log('one time alarm ' + str(alarmNum) + ' turned off', 'N')
                        startAlarm(alarmNum)
                    except:
                        GF.log('unable to ring alarm ' + str(alarmNum), 'E')
                else: # oneTimeAlarm = False
                    day = datetime.datetime.today().weekday()  # match days
                    # print('day: ' + str(day) + ' on this day: ' + str(ontThisDay) )
                    if alarmDays[day] == 't':  # play alarm on this day and this time
                        try:
                            startAlarm(alarmNum)
                        except:
                            GF.log('unable to ring alarm ' + str(alarmNum), 'E')


#check whether the radio should turn automatically off now.
def checkAutoOff():
    if settings["soundSleepTimer"][1] != 'uit':
        vl = str(settings["soundSleepTimer"][1]).split(':')  # value seperated by :
        #print(vl)
        ah = int(vl[0])
        am = int(vl[1])
        if ah == th and am == tm:  # time match
            #turn amplifier off
            GF.log('auto turning off', 'N')
            # qry5 = "UPDATE settings set value='versterkerUit', changetime='" + time10() + "' WHERE name='geluidbron'"
            # GF.send('geluidbron', 'versterkerUit')
            send(json.dumps({"geluidbron":'versterkerUit'}))
            #disable the sound sleep timer
            # qry6 = "UPDATE settings set value='uit', changetime='" + time10() + "' WHERE name='soundSleepTimer'"
            # GF.send('soundSleepTimer', 'uit')
            send(json.dumps({"soundSleepTimer":'uit'}))

# send data to server
def send(data):
    sock.sendall(bytes(str(data+'\n'), "utf-8"))

def checkReclame():
    if settings['geluidbron'][1] == 'Raspberry' and settings['skipAds'][1] == 'true': #radio is on
        try:
            if tm == 57:  # time match
                #change station
                GF.log("changing radiostation to skip reclame", "N")
                #send("storeData:"+json.dumps({"radiostation":settings["radiostation"][1]}))

                send(json.dumps({"radiostationTemp": settings["radiostation"][1], "radiostation": "538nonstop40"}))
            elif tm == 6:  # time match
                #set station back
                GF.log("changing radiostation back after reclame", "N")
                #send("getData:radiostation")
                send(json.dumps({"radiostation":settings["radiostationTemp"][1]}))
        except:
            GF.log('failed to skip radio reclame','E')

#####MAIN
try:
    sock.connect(('192.168.1.104', 600))
except:
    print("connection failed")
    sock.close()
    exit()

#GF.log("Connected! Logging in to system ...", "D" )
time.sleep(0.5)
loginData = {
    "username": "minute",
    "password": "",
}
try:
    sock.sendall(bytes(json.dumps(loginData), "utf-8"))
    answer = str(sock.recv(100), "utf-8")
except:
    print("server disconnected during login communication")
    sock.close()
    exit()

if answer[0:2] == 'OK':
    #try:
    msg = str(sock.recv(3000), "utf-8")
    print('msg: '+msg)

    settings = json.loads(msg)
    db = PyDatabase.PyDatabase(host=GF.DBLogin["host"], user=GF.DBLogin["user"], passwd=GF.DBLogin["passwd"], db=GF.DBLogin["db"])
    qry = 'UPDATE RPi.settings SET value = CASE name'
    for key, value in settings.items():
        value=value[1]
        if value is not None and key is not None and value != '' and value != 'null' :
            qry += " WHEN '" + key + "' THEN '" + db.Escape(value) + "' "
    qry += 'END WHERE type IS NOT NULL'
    results = db.Execute(qry)
    if results is False:
        GF.log("failed to execute query: " + db.query, 'E')
    GF.log("Database updated","N")

    th = time.localtime()[3]
    tm = time.localtime()[4]

    #try:
    checkAlarms()
    #except:
    #    print('checkalarm error')
    #try:
    checkAutoOff()
    #except:
     #   print('autooff error')
    try:
        checkReclame()
    except:
        print('reclame error')
    #print('finished')
    #print('closing:')
    sock.sendall(bytes("close", "utf-8"))
    sock.shutdown(1)
    sock.close()
    time.sleep(2)
else:
    GF.log("login to server failed: "+answer)

