import flask
from flask import Flask, Response, request, render_template, redirect, url_for, send_from_directory, session
from flaskext.mysql import MySQL
import flask.ext.login as flask_login
from flask_oauth import OAuth
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map
import json
import os

#database setup
'''
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'your database password'
app.config['MYSQL_DATABASE_DB'] = 'roundtable'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)
'''

from flask import Flask
app = Flask(__name__)


app.config.update(
    DEBUG = True,
)


@app.route('/')
def welcome():
    return render_template('index.html')




if __name__ == "__main__":
	#this is invoked when in the shell  you run
	#$ python app.py
	app.run(port=5000, debug=True)
