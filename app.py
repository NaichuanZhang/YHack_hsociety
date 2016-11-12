import flask
from flask import Flask, Response, request, render_template, redirect, url_for, send_from_directory, session
from flaskext.mysql import MySQL
import flask.ext.login as flask_login
from flask_oauth import OAuth
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map
import json
import os
from flask import Flask
app = Flask(__name__)


app.config.update(
    DEBUG = True,
)


#database setup

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '112358'
app.config['MYSQL_DATABASE_DB'] = 'hsociety'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'ico/favicon.ico')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

app.secret_key = 'super secret string'  # Change this!
FACEBOOK_APP_ID = '1825456641056295'
FACEBOOK_APP_SECRET = 'edaa003fe370f3ffacc2c3cf26f25e8a'


oauth = OAuth()
facebook = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=FACEBOOK_APP_ID,
    consumer_secret= FACEBOOK_APP_SECRET,
    request_token_params={'scope': 'email'}
)

@facebook.tokengetter
def get_facebook_token():
    return session.get('facebook_token')

def pop_login_session():
    session.pop('logged_in', None)
    session.pop('facebook_token', None)

@app.route("/facebook_login")
def facebook_login():
    return facebook.authorize(callback=url_for('facebook_authorized',next=request.args.get('next'), _external=True))

@app.route("/facebook_authorized")
@facebook.authorized_handler
def facebook_authorized(resp):
    next_url = request.args.get('next') or url_for('welcome')
    if resp is None or 'access_token' not in resp:
        return redirect(next_url)
    session['logged_in'] = True
    session['facebook_token'] = (resp['access_token'], '')
    return redirect(next_url)

@app.route("/logout")
def logout():
    pop_login_session()
    return render_template('index.html', message="Logged out")

#Querying information from facebook
def get_facebook_name():
	data = facebook.get('/me').data
	print data
	if 'id' in data and 'name' in data:
		user_id = data['id']
		user_name = data['name']
		return user_name


def get_facebook_friend_appuser():
	data = facebook.get('/me?fields=friends{first_name,last_name}').data
	print data
	return data


def get_all_facebook_friends():
	data = facebook.get('/me/taggable_friends?fields=first_name,last_name').data
	print data
	return data

def get_facebook_profile_url():
    data = facebook.get('/me?fields=picture{url}').data
    if 'picture' in data:
        print data['picture']
        json_str = json.dumps(data['picture'])
        resp = json.loads(json_str)
        print "json object"
        user_picture_url = data['picture']
        return data['picture']['data']['url']




@app.route('/')
def home():
    return render_template('index.html')

@app.route('/logged_in')
def welcome():
    return render_template('index.html', message = 'Welcome to hsociety', user_name = get_facebook_name(), user_picture_url = get_facebook_profile_url())







if __name__ == "__main__":
	#this is invoked when in the shell  you run
	#$ python app.py
	app.run(port=5000, debug=True)
