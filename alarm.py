#!/usr/bin/python


#Python Raspberry Pi Domotica
#Jeroen van Oorschot 2013
#check whether a alarm should play
#check sleep timer auto off

#import db and connect
# import MySQLdb
import PyDatabase
#date and time
import datetime
import time

#time in 10*microseconds
def time10():
    return str(int(round(time.time() * 100)))


# start alarm
def startAlarm(alarmParent, oneTimeAlarm):
    ##read updates from database
    db = PyDatabase.PyDatabase()
    #disable if onetime
    if oneTimeAlarm:
        # qry2 = "UPDATE settings set value='false', changetime='" + time10() + "' WHERE SUBSTRING(settings.name,4,LENGTH(settings.name)-3)='alarmOn' AND parent='" + alarmParent + "'"
        values = {
            'changetime' : time10()
        }
        condition = {
            'SUBSTRING(settings.name,4,LENGTH(settings.name)-3)' : 'alarmOn',
            'parent' : alarmParent
        }
        if not db.Update(table='settings', values=values, condition_and=condition):
            print("could not execute query: " + db.query)
        # try:
        #     cursor.execute(qry2)
        # except:
        #     print('error turning alarm off')
        print('one time alarm turned off')
    #find volume, increasevolume
    qry3 = "SELECT settings.name, SUBSTRING(settings.name,4,LENGTH(settings.name)-3), settings.value FROM RPi.settings where parent='" + alarmParent + "' ORDER BY settings.name"
    columns = ['name', 'SUBSTRING(settings.name,4,LENGTH(settings.name)-3)', 'value']
    condition = {
        'parent' : alarmParent
    }
    results = db.Select(table='settings', columns=columns, condition_and=condition, order='name')
    if results is False:
        print("could not execute query: " + db.query)
    # try:
    #     cursor.execute(qry3)
    # except:
    #     print("query execute error")
    #fetch results
    # try:
    # results = cursor.fetchall()
    for alarmSettings in results:
        fullName = alarmSettings[0]
        value = alarmSettings[2]
        if alarmSettings[1] == 'alarmVol':  # update volume, don't use increase vol yet
            qry4 = "UPDATE settings set value='" + value + "', changetime='" + time10() + "' WHERE name='volume'"
            values = {
                'value' : value,
                'changetime' : time10()
            }
            condition = {
                'name' : 'volume'
            }
            if not db.Update(table='settings', values=value, condition_and=condition):
                print("could not execute query: " + db.query)
            # cursor.execute(qry4)
        #turn radio on
        # qry5 = "UPDATE settings set value='Raspberry', changetime='" + time10() + "' WHERE name='geluidbron'"
        values = {
            'value' : 'Raspberry',
            'changetime' : time10()
        }
        condition = {
            'name' : 'geluidbron'
        }
        if not db.Update(table='settings', values=values, condition_and=condition):
            print("could not execute query: " + db.query)

        # try:
        #     cursor.execute(qry5)
        # except:
        #     print("query execute error")
    # except:
    #     print('problem updating for start alarm')
    # cursor.close()
    # con.close()
    db.Close()


# check alarms
def checkAlarm():
    ##read updates from database
    #create connection and cursor
    db = PyDatabase.PyDatabase()
    # con = connectDB()
    # cursor = con.cursor()
    #make query
    qry = """select settings.name, settings.value, settings.parent from RPi.settings WHERE
        (
            SUBSTRING(settings.name,4,LENGTH(settings.name)-3)='alarmTime'
        ) AND (
        settings.parent IN
            (
            select settings.parent from RPi.settings WHERE
            SUBSTRING(settings.name,4,LENGTH(settings.name)-3)='alarmOn' AND
            settings.value='true'
            )
        )
        """
    results = db.Execute(qry)
    if results is False:
        print("failed to execute query: " + db.query)
    #print(qry)
# OR
#SUBSTRING(settings.name,4,LENGTH(settings.name)-3)='alarmDays'
    #execute query
    #get all the times of alarms that are turned on
    # try:
    #     cursor.execute(qry)
    # except:
    #     print("query execute error")
    #fetch results
    th = time.strftime("%H", time.localtime())
    tm = time.strftime("%M", time.localtime())
    #print("now: " + th + ';' + tm)
    # results = cursor.fetchall()
    for row in results:  # for each alarm that is turned on
        nm = row[0]  # name of setting
        pt = row[2]  # parent
        #print('name: ' + nm + ' value: ' + row[1])
        try:
            vl = row[1].split(':')  # value
            ah = vl[0]
            am = vl[1]
            if len(ah) == 1:
                ah = '0'+ah
            if len(am) == 1:
                am = '0'+am
            #print("alarm: " + ah + ';' + am)

            if ah == th and am == tm:  # time match
                qry = "SELECT settings.name, settings.value FROM RPi.settings WHERE parent='"+pt+"' AND SUBSTRING(settings.name,4,LENGTH(settings.name)-3)='alarmDays'"
                condition = {
                    'parent' : pt,
                    'SUBSTRING(settings.name,4,LENGTH(settings.name)-3)' : 'alarmDays'
                }
                columns = ['name', 'value']
                results = db.Select(table='settings', columns, condition_and=condition, fetchall=False)
                if results is False:
                    print("failed to execute query: " + db.query)
                # try:
                #     cursor.execute(qry)
                # except:
                #     print("query execute error")
                thisAlarm = results.fetchone()
                if thisAlarm[1].count('false') == 7:   # everything false
                    # oneTimeAlarm = True
                    print('one time alarm on: ' + time.strftime("%H %M", time.localtime()))
                    try:
                        startAlarm(pt, True)
                    except:
                        print('alarm kan niet afspelen')
                else:
                    # oneTimeAlarm = False
                    day = datetime.datetime.today().weekday()  # match days
                    onThisDay = thisAlarm[1][thisAlarm[1].index(str(day))+4:thisAlarm[1].index(str(day))+5]
                    # print('day: ' + str(day) + ' on this day: ' + str(ontThisDay) )
                    if onThisDay == 't':  # play alarm on this day and this time
                        try:
                            print('alarm on: ' + time.strftime("%H %M", time.localtime()))
                            startAlarm(pt, False)
                        except:
                            print('alarm kan niet afspelen')
            #else:
                #print("not equal alarm times")
        except:
            print('error parsing and checking time')
    #close cursor and connection
    # cursor.close()
    # con.close()
    db.Close()


def checkAutoOff():
    #create connection and cursor
    db = PyDatabase.PyDatabase()
    # con = connectDB()
    # cursor = con.cursor()
    #make query
    qry = "select settings.value from RPi.settings WHERE settings.name='soundSleepTimer'"
    condition = {
        'name' : 'soundSleepTimer'
    }
    data = db.Select(table='settings', colulmns=['value'], condition_and=condition,fetchall=False)
    if data is False:
        print('auto off failed query: ' + db.query)
    #execute query
    #get all the times of alarms that are turned on
    # try:
    #     cursor.execute(qry)
    # except:
    #     print("query execute error")
    #fetch results
    row = data.fetchone()[0]
    #print(row)
    if not row == 'uit':
        try:
            vl = row.split(':')  # value
            #print(vl)
            ah = vl[0]
            am = vl[1]
            if len(ah) == 1:
                ah = '0'+ah
            if len(am) == 1:
                am = '0'+am
            #print("auto uit: " + ah + ';' + am)
            #print(ah + ';' + am)
            th = time.strftime("%H", time.localtime())
            tm = time.strftime("%M", time.localtime())
            #print(th + ';' + tm)
            if ah == th and am == tm:  # time match
                #turn amplifier off
                print('auto off: ' + time.strftime("%H %M", time.localtime()))
                # qry5 = "UPDATE settings set value='versterkerUit', changetime='" + time10() + "' WHERE name='geluidbron'"
                values = {
                    'value' : 'versterkerUit',
                    'changetime' : time10()
                }
                condition = {
                    'name' : 'geluidbron'
                }
                if not db.Update(table='settings', values=values, condition_and=condition):
                    print("could not execute query: " + db.query)
                # try:
                #     cursor.execute(qry5)
                # except:
                #     print("query execute error")
                #disable the sound sleep timer
                qry6 = "UPDATE settings set value='uit', changetime='" + time10() + "' WHERE name='soundSleepTimer'"
                values = {
                    'value' : 'uit',
                    'changetime' : time10()
                }
                condition = {
                    'name' : 'soundSleepTimer'
                }
                if not db.Update(table='settings', values=values, condition_and=condition):
                    print("could not execute query: " + db.query)
                # try:
                #     cursor.execute(qry6)
                # except:
                #     print("query execute error")
        except:
            print('auto off failed')

    db.Close()



def checkReclame():
    #create connection and cursor
    db = PyDatabase.PyDatabase()
    # con = connectDB()
    # cursor = con.cursor()
    #make query
    # qry = "select settings.value from RPi.settings WHERE settings.name='skipAds' AND settings.value='true'"
    condition = {
        'name' : 'skipAds',
         'value' : 'true'
    }
    results = db.Select(table='settings', columns=['value'], condition_and=condition, fetchall=False)
    if results is False:
        print("could not execute query: " + db.query)
    #execute query
    #get all the times of alarms that are turned on
    # try:
    #     cursor.execute(qry)
    # except:
    #     print("query execute error")
    #fetch results
    if results.fetchone():
        try:
            tm = time.strftime("%M", time.localtime())
            if tm == 56:  # time match
                #change station
                # qry5 = "UPDATE settings set value='538nonstop40', changetime='" + time10() + "' WHERE name='radiostation'"
                values = {
                    'value' : '538nonstop40',
                    'changetime' : time10()
                }
                condition = {
                    'name' : 'radiostation'
                }
                if not db.Update(table='settings', values=values, condition_and=condition):
                    print("could not execute query: " + db.query)
                # try:
                #     cursor.execute(qry5)
                # except:
                #     print("query execute error")

            elif tm == 5:  # time match
                #turn amplifier off
                qry5 = "UPDATE settings set value='3fm', changetime='" + time10() + "' WHERE name='radiostation'"
                values = {
                    'value' : '3fm',
                    'changetime' : time10()
                }
                condition = {
                    'name' : 'radiostation'
                }
                if not db.Update(table='settings', values=values, condition_and=condition):
                    print("could not execute query: " + db.query)
                # try:
                #     cursor.execute(qry5)
                # except:
                #     print("query execute error")
        except:
            print('auto off failed')
    db.Close()


######DB
# def connectDB():
#     while True:
#         try:
#             con = MySQLdb.connect(host="localhost", # your host, usually localhost
#                                   user="root", # your username
#                                   passwd="RPIJvO262SADF", # your password
#                                   db="RPi") # name of the data base
#             #autocommit changes and so autorefresh db
#             #print "db connected"
#             con.autocommit(True)
#             #print "autocommit enabled"
#             break
#         except:
#             print("Error connecting to MYSQL, retrying")
#             sleep(2)
#     return con

######MAIN
try:
    checkAlarm()
    checkAutoOff()
    #checkReclame()
    #print('finished')
except:
    print("something went wrong, quit")
