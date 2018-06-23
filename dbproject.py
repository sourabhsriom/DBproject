from flask import Flask
from flask_ask import Ask, question, statement, session
import pyodbc
#import pymssql
import emailAlert as ea
import excel_creator as ec
import sentiment_analysis as sa


host = "LT-CNU252CCM5"
user = "sds"
passwd = "Master1!"
DB = "SDS_125"



conn = pyodbc.connect('DRIVER={ODBC Driver 11 for SQL Server};SERVER='+host+';DATABASE='+DB+';UID='+user+';PWD='+ passwd)
#conn = pymssql.connect(host,user,passwd,DB)
cursor = conn.cursor()


followup = "...is there any thing else I can help you with?"
error = "I'm sorry, I'm unable to figure that out right now"

def getDenomEmailInfo(date):
    query = "SELECT ava.GAME_DENOM as denom, SUM(SDS_Bets) as coin_in\
  FROM [SDS_125].[ACCOUNTING].[VIEW_SDS_VALUE] as asds inner join ACCOUNTING.VIEW_ASSET as ava\
  on ava.NAMED_ASSET_ID = asds.Mtr_NamedAsstID\
   where Mtr_GameDay = '{}' and PTYP_ID = 1\
    group by ava.GAME_DENOM\
    order by coin_in desc".format(date)

    cursor.execute(query)
    row = cursor.fetchone()

    list = []
    values = []
    while row :
        dollars = '${:,.2f}'.format(row[1])
        list = [row[0], dollars]
        values.append(list)
        row = cursor.fetchone()
    return values


def queryDB(title):

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


def getDBSlotInfo(date):
    query = "SELECT Mtr_NamedAsstID, max(ava.SLOT_NUMBER) as slot_number, SUM(SDS_Bets) as coin_in\
  FROM [SDS_125].[ACCOUNTING].[VIEW_SDS_VALUE] as asds inner join ACCOUNTING.VIEW_ASSET as ava\
  on ava.NAMED_ASSET_ID = asds.Mtr_NamedAsstID\
    where Mtr_GameDay = '{}' and PTYP_ID = 1\
  group by Mtr_NamedAsstID\
    order by coin_in desc".format(date)

    cursor.execute(query)
    row = cursor.fetchone()
    return (row[1],row[2])

def getCoinInfromDB(date):
    query = "SELECT sum(SDS_Bets) as coin_in FROM [SDS_125].[ACCOUNTING].[VIEW_SDS_VALUE] where Mtr_GameDay = '{}' and PTYP_ID = 1".format(date)
    print (query)
    cursor.execute(query)
    row = cursor.fetchone()

    return row[0]


def getDenomInfoDB(date,denom):

    denom = int(denom)/100
    query = "SELECT ava.GAME_DENOM as denom, SUM(SDS_Bets) as coin_in\
  FROM [SDS_125].[ACCOUNTING].[VIEW_SDS_VALUE] as asds inner join ACCOUNTING.VIEW_ASSET as ava\
  on ava.NAMED_ASSET_ID = asds.Mtr_NamedAsstID\
   where Mtr_GameDay = '{}' and PTYP_ID = 1 and ava.GAME_DENOM = {}\
    group by ava.GAME_DENOM\
    order by coin_in desc".format(date, denom)

    cursor.execute(query)
    row = cursor.fetchone()
    return row[1]

app = Flask(__name__)
ask = Ask(app, "/")

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
    coinIn = getDenomInfoDB(date,denom)
    coinIn = round(coinIn,2)
    response = "coin in for the {} cent denom was ${}".format(denom, coinIn)
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
