#!/usr/bin/python3

__author__ = 'JvO'

#Python Raspberry Pi Domotica
#Jeroen van Oorschot 2014
#Functions that run every minute like alarms and timers

import GFunc

import PyDatabase
#date and time
import datetime
import time
from time import sleep
import json
import socket
#import pickle


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

GF = GFunc.GFunc()

def setSunlight(time):
    x = 0;
    while x <= 100:
        send(json.dumps({'kamer_sunrise' : x, 'keuken_sunrise' : x}))
        x+=1
        sleep(time/10.0)

# start an alarm, alarmNum = 1,2,3 or 4
def startAlarm(alarmNum,):
    #start alarm
    GF.log("Alarm " + str(alarmNum) + " turning on now", 'N')

    print(json.dumps({'volume' : settings['a' + alarmNum + '_alarmVol'][1], 'geluidbron' : 'Raspberry'}))
    send(json.dumps({'volume' : settings['a' + alarmNum + '_alarmVol'][1], 'geluidbron' : 'Raspberry'}))
    try:
        x = settings['a'+alarmNum+'_alarmLight'][1]
        if x != 0:
            send(json.dumps({'kamer_sunrise' : 0 , 'keuken_sunrise' : 0, 'ledlampAanUit' : True}))
            setSunlight(x)
    except:
        x = 0


# check alarms
def checkAlarms():
    for i in range(1,5):  # for each alarm that is turned on
        alarmNum = str(i)
        #print(alarmNum)
        if settings['a' + alarmNum + '_alarmOn'][1] == True:
            at = settings['a' + alarmNum + '_alarmTime'][1].split(':')
           #GF.log('alarm ' + alarmNum + ' is being checked'+str(at), "D")
            if int(at[0]) == th and int(at[1]) == tm:  # time match, alarm should ring now
                alarmDays = settings['a' + alarmNum + '_alarmDays'][1]
                GF.log("Alarm "+str(alarmNum) + " now starting")
                # check if it is an one-time alarm, meaning no repeating days are selected
                if alarmDays == 'fffffff':   # everything false oneTimeAlarm = True
                    #try:
                    send(json.dumps({'a' + str(alarmNum) + '_alarmOn' : False}))
                    GF.log('one time alarm ' + str(alarmNum) + ' turned off', 'N')
                    startAlarm(alarmNum)
                   # except:
                    #    GF.log('unable to ring alarm ' + str(alarmNum), 'E')
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

#check whether to change radiostation to skip the adds
def checkReclame():
    if settings['geluidbron'][1] == 'Raspberry' and settings['skipAds'][1] == True: #radio is on
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


# send data to server
def send(message):
    sleep(1)  # wait some time to prevent sending too fast
    message = 'S'+message
    GF.log("Tx: "+message)
    message = GF.create_frame(message)
    sock.sendall(message)


try:
    sock.connect(('192.168.1.104', 600))
except:
    GF.log("Failed to connect to server","E")
    sock.close()
    exit()

time.sleep(0.5)
loginData = {
    "username": "minute",
    "password": "",
}

#send login info without websocket protocol
try:
    sock.sendall(bytes(json.dumps(loginData), "utf-8"))
    sleep(1)
except:
    print("server disconnected during login communication, quiting")
    sock.close()
    exit()
	
#try:
data = GF.parse_frame(sock, False)
answer = str(data, "utf-8")
#except:
#    print("parsing frame failed, quiting")
#    sock.close()
#    exit()

if answer[0:1] == 'A':
    sleep(0.1)

    #retrieve the settings, minute user gets data automatically
    msg = str(GF.parse_frame(sock,False), "utf-8")  # str(sock.recv(3000), "utf-8")
    GF.log('data: '+msg, "N")  # print all data that is going to be written to db

    settings = json.loads(msg)
    db = PyDatabase.PyDatabase(host=GF.DBLogin["host"], user=GF.DBLogin["user"], passwd=GF.DBLogin["passwd"], db=GF.DBLogin["db"])
    qry = 'UPDATE RPi.settings SET value = CASE name'
    for key, value in settings.items():
        value=value[1]
        if value is not None and key is not None and value != '' and value != 'null' :
            qry += " WHEN '" + key + "' THEN '" + json.dumps(value) + "' "
    qry += 'END WHERE type IS NOT NULL'
    results = db.Execute(qry)
    if results is False:
        GF.log("failed to execute query: " + db.query, 'E')
    #GF.log("Database updated","N")

    th = time.localtime()[3]
    tm = time.localtime()[4]

    try:
        checkReclame()
    except:
        print('reclame error')
    #try:
    checkAlarms()
    #except:
    #    print('checkalarm error')
    #try:
    checkAutoOff()
    #except:
     #   print('autooff error')

    #print('finished')
    #print('closing:')
    #send("close")
    #sock.shutdown(1)
    sock.close()
    time.sleep(1)
else:
    GF.log("login to server failed: "+answer)

