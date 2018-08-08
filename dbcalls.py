from flask import Flask, render_template, redirect, url_for
import pyodbc
import pymssql
import json
import webMethods as web
import datetime

f = open('.\\settings\\configuration.json', 'r')
data = json.loads(f.read())

conn_info = data['DB_info']
host = conn_info['host']
user = conn_info['user']
passwd = conn_info['passwd']
DB = conn_info['DB']

today = datetime.date.today()
yesterday = today - datetime.timedelta(days = 1)

today = today.strftime('%Y-%m-%d')

yesterday = yesterday.strftime('%Y-%m-%d')

#conn = pyodbc.connect('DRIVER={ODBC Driver 11 for SQL Server};SERVER='+host+';DATABASE='+DB+';UID='+user+';PWD='+ passwd)
conn = pymssql.connect(host,user,passwd,DB)
cursor = conn.cursor()


def coinInComparision(date1 = today, date2 = yesterday):
    values1 = hourlyCoinIn(date1)
    values2 = hourlyCoinIn(date2)
    total1 = getCoinInfromDB(date1)
    total2 = getCoinInfromDB(date2)
    return (values1, values2, total1, total2)

def hourlyCoinIn(date):
    query = "SELECT DATEPART(hour,HR_DATE_TIME) AS OnHour,sum(HR_BETS_VAL)/100.00 as Hourly_coin_in\
    FROM [sds132].[ACCOUNTING].[VIEW_HOURLY_REPORT]\
    where CONVERT(VARCHAR(25), HR_DATE_TIME, 126) like '%{}%'\
    group by HR_DATE_TIME\
    order by OnHour asc".format(date)

    print (query)

    cursor.execute(query)
    row = cursor.fetchone()

    list = []
    values = []
    while row :
        hour = row[0]
        dollars = int(row[1])
        #dollars = '${:,.2f}'.format(row[1])
        list = [hour, dollars]
        values.append(list)
        row = cursor.fetchone()
    return values

def getByAreaInfo(date):
    query = "SELECT ava.AREA_NAME as denom, SUM(SDS_Bets) as coin_in\
    FROM [ACCOUNTING].[VIEW_SDS_VALUE] as asds inner join ACCOUNTING.VIEW_ASSET as ava\
    on ava.NAMED_ASSET_ID = asds.Mtr_NamedAsstID\
    where Mtr_GameDay = '2016-09-08' and PTYP_ID = 1\
    group by ava.AREA_NAME"

    cursor.execute(query)
    row = cursor.fetchone()
    list = []
    values = []

    while row :
        area = row[0]
        dollars = row[1]
        list = [area,dollars]
        values.append(list)
        row = cursor.fetchone()
    return values

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
        denom = row[0]
        dollars = row[1]
        #dollars = '${:,.2f}'.format(row[1])
        list = [denom, dollars]
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
