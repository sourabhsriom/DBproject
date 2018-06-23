from flask import Flask
from flask_ask import Ask, question, statement, session
import pyodbc

def queryDB(title):
    host = "LT-CNU252CCM5"
    user = "sds"
    passwd = "Master1!"
    DB = "SDS_125"



    conn = pyodbc.connect('DRIVER={ODBC Driver 11 for SQL Server};SERVER='+host+';DATABASE='+DB+';UID='+user+';PWD='+ passwd)
    cursor = conn.cursor()
    query = "select * from [USER].FUNCTION_GROUP where FUNCGRP_NAME like '%{}%';".format(title)
    print (query)
    cursor.execute(query)
    row = cursor.fetchone()
    #row = '...'.join(i for i in row[2])
    rows = ""
    while row :
        rows = rows + "..." + row[2]
        row = cursor.fetchone()

    print (rows)
    return rows
    '''while row:
        print (row[0])
        row = cursor.fetchone()
        '''

#queryDB(title)


app = Flask(__name__)
ask = Ask(app, "/")

@ask.launch
def start_skill():
    greeting = "Hello, would you like to know the Job Titles you have?"
    return question(greeting)

@ask.intent("YesIntent")
def getDBInfo(title):
    title = title
    sites = queryDB(title)
    response = "Here are the jobs you are looking for : {}".format(sites)
    return statement(response)


@ask.intent("NoIntent")
def goodBye():
    bye = "Then why did you wake me up?"
    return statement(bye)

@ask.intent("FarziIntent")
def farzi():
    farz = "Why are you messing with me?"
    return statement(farz)


if __name__ == "__main__":
    app.run(debug=True)
