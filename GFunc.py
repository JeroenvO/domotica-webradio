__author__ = 'jvo'

#General functions used in Raspberry pi webradio

import time
from time import sleep
import datetime
import PyDatabase

class GFunc():

    def __init__(self): #creates the database connection itself
        while True:
            try:
                DBLoginFile = open("/home/pi/DBLogin.txt",'r')
                DBLoginLines = DBLoginFile.readlines()
                DBLoginFile.close()
                DBLogin = {}
                for line in DBLoginLines:
                    if line[0] == "#" or line == "":
                        continue
                    line = line.split("=")
                    DBLogin[line[0]] = line[1].split('"')[1].strip()
                print("Logging in with: " + str(DBLogin))
                break
            except:
                self.log("Error parsing db login parameters, retrying in 5s",'E')
                sleep(5)

        self.DBLogin = DBLogin


    #time in 10*microseconds
    def time10(self):
        return str(int(round(time.time() * 100)))

    #write a changed setting to the database
    def update(self, name, value):
        db = PyDatabase.PyDatabase(host=self.DBLogin["host"], user=self.DBLogin["user"], passwd=self.DBLogin["passwd"], db=self.DBLogin["db"])
        values = {
            'value' : db.Escape(value),
            'changetime' : str(self.time10())
        }
        condition = {
            'name' : db.Escape(name)
        }
        if not db.Update(table='settings', values=values, condition_and=condition):
            self.log("Could not execute query: " + db.query,'E')
        db.Close()


    #log
    def log(self, txt, code="Unspecified"):
        ts = datetime.datetime.today().strftime("%Y-%m-%d %H:%M")
        print("["+str(ts)+"] ["+str(code[0])+"] "+str(txt))
