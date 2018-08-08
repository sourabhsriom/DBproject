import dbcalls as db
import datetime
from flask import Flask, render_template, redirect, url_for

today = datetime.datetime.today().strftime('%Y-%m-%d')

def coinInGraph(date = today):
    return render_template("hello.html")
