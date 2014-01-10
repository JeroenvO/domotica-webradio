__author__ = 'williewonka'

# import MySQLdb
import pymysql as MySQLdb
import time


class PyDatabase():

    def __init__(self): #creates the database connection itself
        while True:
            try:
                self.con = MySQLdb.connect(host="localhost", # your host, usually localhost
                                      user="root", # your username
                                      passwd="", # your password
                                      db="test") # name of the data base
                #autocommit changes and so autorefresh db
                self.con.autocommit(True)
                self.cursor = self.con.cursor()
                break
            except:
                print("Error connecting to MYSQL, retrying")
                time.sleep(2)

    def Condition(self, condition_and=None, condition_or=None):
        if self.query is None and (condition_or is None and condition_and is None):
            return
        self.query += " WHERE"
        if condition_and is not None:
            for condition in list(condition_and.keys()):
                if "IS" in condition_and[condition]:
                    self.query += condition + condition_and[condition] + " AND"
                else:
                    self.query += " " + condition + "='" + str(condition_and[condition]) + "' AND"
            self.query = self.query.strip(" AND")

        if condition_or is not None:
            for condition in list(condition_or.keys()):
                if "IS" in condition_or[condition]:
                    self.query += condition + condition_or[condition] + " OR"
                else:
                    self.query += " " + condition + "='" + str(condition_or[condition]) + "' OR"

            self.query = self.query.strip(" OR")

    def Update(self, table=None, values=None, condition_and=None, condition_or=None, execute=True):

        if table is None or values is None:
            return False
        self.query = "UPDATE " + table + " SET"
        for column in list(values.keys()):
            self.query += " " + column + " = '" + values[column] + "',"
        self.query = self.query.strip(",")
        self.Condition(condition_and=condition_and, condition_or=condition_or)
        if not execute:
            return True
        try:
            self.cursor.execute(self.query)
            return True
        except:
            return False

    def Select(self, table=None, columns=None, condition_or=None, condition_and=None, order=None, execute=True, fetchall=True):
        if table is None or columns is None:
            return False
        self.query = "SELECT"
        for column in columns:
            self.query += " " + column + ","
        self.query = self.query.strip(",")
        self.query += " FROM " + table
        self.Condition(condition_and=condition_and, condition_or=condition_or)
        if order is not None:
            self.query += " ORDER BY " + order

        if not execute:
            return self.query

        try:
            self.cursor.execute(self.query)
            if fetchall:
                return self.cursor.fetchall()
            else:
                return self.cursor
        except:
            return False

    def Execute(self, query=None, fetchall=True):
        if query is None:
            return False
        self.query = query
        try:
            self.cursor.execute(self.query)
            if fetchall:
                return self.cursor.fetchall()
            else:
                return True
        except:
            return False

    def Insert(self, table=None, values=None, execute=True):
        if table is None or values is None:
            return False

        self.query = "INSERT INTO " + table + " ("

        for column in list(values.keys()):
            self.query += column + ", "
        self.query = self.query.strip(", ")
        self.query += ") VALUES ("
        for value in list(values.values()):
            if "(" in value and ")" in value:
                self.query += value + ", "
            else:
                self.query += "'" + value + "', "

        self.query = self.query.strip(", ")
        self.query += ")"

        if execute:
            try:
                self.cursor.execute(self.query)
                return True
            except:
                return False

    def Escape(self, value):
        return self.cursor.escape_string(value)

    def Close(self):
        self.cursor.close()
        self.con.close()