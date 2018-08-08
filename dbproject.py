from flask import (Flask,
                   render_template,
                   request,
                   redirect,
                   url_for,
                   flash,
                   jsonify,
                   make_response)
from flask_ask import Ask, question, statement, session
import pyodbc
import pymssql
import emailAlert as ea
import excel_creator as ec
import sentiment_analysis as sa
import json
import webMethods as web
import requests
import httplib2
import dbcalls as db
import datemodule as dm
import datetime
import intent as i

'''
host = '10.11.203.56'
user = "sdsuser"
passwd = "abc@123"
DB = "SDS132"
'''

f = open('.\\settings\\configuration.json', 'r')
data = json.loads(f.read())

conn_info = data['DB_info']
host = conn_info['host']
user = conn_info['user']
passwd = conn_info['passwd']
DB = conn_info['DB']


#conn = pyodbc.connect('DRIVER={ODBC Driver 11 for SQL Server};SERVER='+host+';DATABASE='+DB+';UID='+user+';PWD='+ passwd)
conn = pymssql.connect(host,user,passwd,DB)
cursor = conn.cursor()


followup = "...is there any thing else I can help you with?"
error = "I'm sorry, I'm unable to figure that out right now"

def getDenomEmailInfo(date):
    query = "SELECT ava.GAME_DENOM as denom, SUM(SDS_Bets) as coin_in\
    FROM {}.[ACCOUNTING].[VIEW_SDS_VALUE] as asds inner join ACCOUNTING.VIEW_ASSET as ava\
    on ava.NAMED_ASSET_ID = asds.Mtr_NamedAsstID\
    where Mtr_GameDay = '{}' and PTYP_ID = 1\
    group by ava.GAME_DENOM\
    order by ava.GAME_DENOM asc".format(DB,date)

    cursor.execute(query)
    row = cursor.fetchone()

    list = []
    values = []
    while row :
        dollars = row[1]
        #dollars = '${:,.2f}'.format(row[1])
        list = [row[0], dollars]
        values.append(list)
        row = cursor.fetchone()
    return values


def queryDB(title):

    query = "select * from {}[USER].FUNCTION_GROUP where FUNCGRP_NAME like '%{}%';".format(DB,title)
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


def getDBSlotInfo(date):
    query = "SELECT Mtr_NamedAsstID, max(ava.SLOT_NUMBER) as slot_number, SUM(SDS_Bets) as coin_in\
    FROM {}.[ACCOUNTING].[VIEW_SDS_VALUE] as asds inner join ACCOUNTING.VIEW_ASSET as ava\
    on ava.NAMED_ASSET_ID = asds.Mtr_NamedAsstID\
    where Mtr_GameDay = '{}' and PTYP_ID = 1\
    group by Mtr_NamedAsstID\
    order by coin_in desc".format(DB,date)

    cursor.execute(query)
    row = cursor.fetchone()
    return (row[1],row[2])

def getCoinInfromDB(date):
    query = "SELECT sum(SDS_Bets) as coin_in FROM {}.[ACCOUNTING].[VIEW_SDS_VALUE] where Mtr_GameDay = '{}' and PTYP_ID = 1".format(DB,date)
    print (query)
    cursor.execute(query)
    row = cursor.fetchone()

    return row[0]


def getDenomInfoDB(date,denom):

    denom = int(denom)/100
    query = "SELECT ava.GAME_DENOM as denom, SUM(SDS_Bets) as coin_in\
    FROM {}.[ACCOUNTING].[VIEW_SDS_VALUE] as asds inner join ACCOUNTING.VIEW_ASSET as ava\
    on ava.NAMED_ASSET_ID = asds.Mtr_NamedAsstID\
    where Mtr_GameDay = '{}' and PTYP_ID = 1 and ava.GAME_DENOM = {}\
    group by ava.GAME_DENOM\
    order by coin_in desc".format(DB,date, denom)

    cursor.execute(query)
    row = cursor.fetchone()
    return row[1]

app = Flask(__name__)
ask = Ask(app, "/")

@app.route('/')
def landing():
    return render_template('hello.html')

@app.route('/design/')
def designer():
    return render_template('design.html')


@app.route('/home')
def helloWorld():
    return web.coinInGraph()

@app.route('/help')
def help():
    return render_template('help.html')

@app.route('/graph', methods = ['GET','POST'])
def displayGraph():

    if request.method == 'POST' :
        question = request.form['name']

        try :
            date = dm.returnDates(question)[0]


            values = db.getDenomEmailInfo(date = date)

            print (values)
            return render_template("graph.html", question = question, values = values)
        except :
            return render_template('help.html')
    else :
        return render_template("graph.html")

@app.route('/todaysCoinIn')
def todaysCoinIn():

    today = datetime.date.today().strftime('%Y-%m-%d')
    today = '2016-09-10'
    values = db.getDenomEmailInfo(today)
    total =  '${:,.2f}'.format(db.getCoinInfromDB(today))
    return render_template('graph.html', question = question, values = values, total = total)

today = datetime.date.today()
yesterday = today - datetime.timedelta(days = 1)

today = today.strftime('%Y-%m-%d')

yesterday = yesterday.strftime('%Y-%m-%d')


today = '2016-09-10'
yesterday = '2016-09-09'

@app.route('/comparision')
def coinInCompare(date1 = today, date2 = yesterday):
    values1, values2, total1, total2 = db.coinInComparision(date1, date2)
    total1 = '${:,.2f}'.format(total1)
    total2 = '${:,.2f}'.format(total2)
    values = []
    print ("checkpoint is reached")
    for i in range(len(values1)):
        #print (values1[i][0], values1[i][1], values2[i][1])
        values.append([values1[i][0], values1[i][1], values2[i][1]])
        #values[i] = [values1[i][0], values1[i][1], values2[i][1]]

    return render_template('comparision.html', values = values, total1 = total1, total2 = total2)



@app.route('/intentHandler', methods = ['GET','POST'])
def intentHandler():

    if request.method == 'POST' :
        question = request.form['name']
        dates = dm.returnDates(question)

        if len(dates) > 1 :
            return coinInCompare(dates[0], dates[1])

        date = dates[0]

        if i.isCoinIn(question) and i.isHourly(question):
            values = db.hourlyCoinIn(date)
            return render_template('hourly_graph.html', values = values)

        elif i.isCoinIn(question) and not i.isHourly(question):
            values = db.getDenomEmailInfo(date = date)
            total = '${:,.2f}'.format(db.getCoinInfromDB(date))
            return render_template('graph.html', question = question, values = values, total = total)
        elif i.isHourly(question) :
            values = db.hourlyCoinIn(date)
            return render_template('hourly_graph.html', values = values)

@app.route('/hourly')
def hourlyGraph():
    today = datetime.date.today().strftime('%Y-%m-%d')
    today = '2016-09-10'
    values = db.hourlyCoinIn(today)
    total = '${:,.2f}'.format(db.getCoinInfromDB(today))
    print (values)
    return render_template('hourly_graph.html', values = values, total = total)

@ask.launch
def start_skill():
    greeting = "Hello, how can I help you today?"
    return question(greeting)\
      .reprompt("I didn't get that. How can I help you today?")

@ask.intent("YesIntent")
def getDBInfo(title):
    title = title
    try :
        sites = queryDB(title)
        response = "Here are the jobs you are looking for : {}".format(sites)
    except :
        response = error
    return question(response + followup)

@ask.intent("bestSlot")
def getSlotInfo(date):
    date = date

    try :
        bestSlot, coinIn = getDBSlotInfo(date)
        response = "your best performing slot was :{} with coin in ${}".format(bestSlot,coinIn)
    except :
        response = error
    return question(response + followup)

@ask.intent("denomIntent")
def getDenomInfo(date,denom):
    date = date
    denom = denom
    try :
        coinIn = getDenomInfoDB(date,denom)
        coinIn = round(coinIn,2)
        response = "coin in for the {} cent denom was ${}".format(denom, coinIn)
    except :
        response = error

    return question(response + followup)

@ask.intent("denomEmailIntent")
def getDenomEmail(date):
    date = date
    try :
        values = getDenomEmailInfo(date)
        ec.create_excel(values)
        response = "an excel report has been mailed to your address"
        mail_msg = "PFA the coin in by denom report"
        ea.send_email(mail_msg, filename = "coin_in_by_denom.xlsx")
    except :
        response = error

    return question(response + followup)

@ask.intent("coinIn")
def getCoinIn(date):
    date = date

    try :
        coinIn = getCoinInfromDB(date)
        coinIn = round(coinIn,2)
        response = "Your coin in for the day was : ${}".format(coinIn)

    except :
        response = error

    return question(response + followup)

@ask.intent("sentiment")
def sentimentAnalysis(query):
    query = query

    try :
        pos_tweets,neg_tweets,neutral_tweets = sa.sentiments(query)
        response = "Twitter sentiment for {} is {}% positive, {}% negative and {}% \
                    neutral".format(query, str(pos_tweets), str(neg_tweets), str(neutral_tweets))
    except :
        response = error

    return question(response + followup)

@ask.intent("AMAZON.FallbackIntent")
def fallback():
    response = "I'm sorry, I didnt understand that..could you please try again?"
    return question(response)


@ask.intent("AMAZON.CancelIntent")
def cancel():
    bye = "OK, I'm gonna get some sleep then...Goodbye!"
    return statement(bye)

@ask.intent("NoIntent")
def goodBye():
    bye = "OK, I'm gonna get some sleep then...Goodbye!"
    return statement(bye)

@ask.intent("FarziIntent")
def farzi():
    farz = "Why are you messing with me?"
    return statement(farz)


if __name__ == "__main__":
    app.run(debug=True)
