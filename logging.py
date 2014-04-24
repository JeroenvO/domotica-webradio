#!/usr/bin/python


#Python Raspberry Pi Logging
#Jeroen van Oorschot 2014
#Server side script write logs to database
#v 0.1
#changelog
#* logging moved to logging.py

#from time import sleep

#import os

import RPi.GPIO as GPIO

import subprocess
#import db and connect
# import MySQLdb
import PyDatabase
import GFunc
#date and time
#import datetime
#time scheduler
#from threading import Timer

#import time
#import fcntl
#import sys


GF = GFunc.GFunc()

######main update function
#Get a value from the database

#####GPIO Functions
#set output
def setOutput(pin, value):
    print ("set " + pin + " to " + value)
    #set gpio

	
	########GPIO
#initialize all ports

def setPorts():
    GPIO.setmode(GPIO.BCM)
    #inputs = [4]
    #outputs = [5,8]
    #for input in inputs:
    #    GPIO.setup(input, GPIO.IN)
#
    #for output in outputs:
    #    GPIO.setup(output, GPIO.OUT)
	
########LOG FUNCTIONS
#write a value in a log
def writeLog(table,value):
    db = PyDatabase.PyDatabase(host=GF.DBLogin["host"], user=GF.DBLogin["user"], passwd=GF.DBLogin["passwd"], db=GF.DBLogin["db"])
    #create connection and cursor

    # cursor.execute("INSERT INTO "+table+" (value, timestamp) VALUES ('"+value+"', NOW())")
    values = {
        'value' : value,
        'timestamp' : 'NOW()'
    }
    if not db.Insert(table=table, values=values):
        print("Could not execute query: " + db.query)

    db.Close()
#cpu temp logger
def logCPUTemp():
    proc = str(subprocess.check_output(["/opt/vc/bin/vcgencmd", "measure_temp"], universal_newlines=True, stderr=subprocess.STDOUT))


    temp = proc[5:7]
    #print("CPU Temperature = ")
    #print(temp)
    writeLog("log_CPUTemp",temp)

#called by scheduler, calls logging functions
def fillLogs():
    logCPUTemp()
    print("logging finished")

	
	
######DB
# def connectDB():
# 	while True:
# 		try:
# 			con = MySQLdb.connect(host="localhost", # your host, usually localhost
# 								 user="root", # your username
# 								  passwd="RPIJvO262SADF", # your password
# 								  db="RPi") # name of the data base
# 			#autocommit changes and so autorefresh db
# 			print "db connected"
# 			con.autocommit(True)
# 			print "autocommit enabled"
# 			break
# 		except:
# 			print "Error connecting to MYSQL, retrying"
# 			sleep(2)
# 	return con
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
# file_path = '/var/lock/logging'
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
#call for logs
fillLogs()
