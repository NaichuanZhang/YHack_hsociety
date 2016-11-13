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

@app.route("/logout_facebook")
def logout_facebook():
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


#login_code
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email from Users")
users = cursor.fetchall()

def getUserList():
    cursor = conn.cursor()
    cursor.execute("SELECT email from Users")
    return cursor.fetchall()

class User(flask_login.UserMixin):
    pass

@login_manager.user_loader
def user_loader(email):
    users = getUserList()
    if not(email) or email not in str(users):
        return
    user = User()
    user.id = email
    return user

@login_manager.request_loader
def request_loader(request):
    users = getUserList()
    email = request.form.get('email')
    if not(email) or email not in str(users):
        return
    user = User()
    user.id = email
    cursor = mysql.connect().cursor()
    cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email))
    data = cursor.fetchall()
    pwd = str(data[0][0] )
    user.is_authenticated = request.form['password'] == pwd
    return user

@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        return render_template('homepage.html')
    #The request method is POST (page is recieving data)
    email = flask.request.form['email']
    cursor = conn.cursor()
    #check if email is registered
    if cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email)):
        data = cursor.fetchall()
        pwd = str(data[0][0] )
        if flask.request.form['password'] == pwd:
            user = User()
            user.id = email
            flask_login.login_user(user) #okay login in user
            return flask.redirect(flask.url_for('protected')) #protected is a function defined in this file

    #information did not match
    return "<a href='/login'>Try again</a>\
            </br><a href='/register'>or make an account</a>"


@app.route('/profile')
@flask_login.login_required
def protected():
    return render_template('index.html')

@app.route('/logout')
def logout():
    flask_login.logout_user()
    return render_template('homepage.html')

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('unauth.html')

#you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register", methods=['GET'])
def register():
    return render_template('register.html', supress='True')

@app.route("/register", methods=['POST'])
def register_user():
    u_fname=request.form.get('u_fname')
    u_lname=request.form.get('u_lname')
    email=request.form.get('email')
    password=request.form.get('password')
    year_of_grad=request.form.get('year_of_grad')
    education=request.form.get('education')
    cursor = conn.cursor()
    test =  isEmailUnique(email)
    if test:
        print cursor.execute("INSERT INTO Users (email, password, u_fname, u_lname, year_of_grad, education) VALUES ('{0}', '{1}','{2}','{3}','{4}','{5}')".format(email, password, u_fname, u_lname, year_of_grad, education))
        conn.commit()
        #log user in
        user = User()
        user.id = email
        flask_login.login_user(user)
        return render_template('index.html', name=u_fname + u_lname, message='Account Created!')
    else:
        print "couldn't find all tokens"
        return flask.redirect(flask.url_for('register'))

def getSkill_id(skill_name):
    cursor = conn.cursor()
    cursor.execute("SELECT skill_id FROM Skills WHERE skill_name ='{0}'".format(skill_name))
    return cursor.fetchall()[0]
def getHackathon_id(hackathon_name):
    cursor = conn.cursor()
    cursor.execute("SELECT hackathon_id FROM Hackathons WHERE hackathon_name ='{0}'".format(hackathon_name))
    return cursor.fetchall()[0][0]

@app.route("/register_skills", methods=['GET','POST'])
@flask_login.login_required
def register_skills():
    if request.method == 'POST':
        skillarray = []
        hackathonarray = []
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Skills")
        for x in cursor:
            skillarray.append(x)
        cursor.execute("SELECT * FROM Hackathons")
        for y in cursor:
            hackathonarray.append(y)
        uid = getUserIdFromEmail(flask_login.current_user.id)
        array = request.form.get('radiobutton')
        skill_id = request.form.get('radiobutton')[1]
        s_level = request.form.get('radiobutton')[3]
        s_level = int(s_level)
        skill_id = int(skill_id)
        print uid
        newcursor=conn.cursor()
        if request.form.get('hackathon_id') != None and (isHackUnique(uid,int(getHackathon_id(request.form.get('hackathon_id'))))):
            hackathon_id = int(getHackathon_id(request.form.get('hackathon_id')))
            newcursor.execute("INSERT INTO H_has_U(u_id, h_id) VALUES('{0}','{1}')".format(uid, hackathon_id))
        if isSkillUnique(skill_id,uid):
            newcursor.execute("INSERT INTO U_has_S(u_id, s_level, s_id) VALUES('{0}','{1}','{2}')".format(uid, s_level, skill_id))
        conn.commit()
        print skill_id
        print s_level
        return render_template('register_skills.html', skills = skillarray)
    else:
        uid = getUserIdFromEmail(flask_login.current_user.id)
        skillarray = []
        hackathonarray = []
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Skills")
        for x in cursor:
            skillarray.append(x)
        cursor.execute("SELECT * FROM Hackathons")
        for y in cursor:
            hackathonarray.append(y)
        print skillarray
        print uid
        return render_template('register_skills.html', skills = skillarray, hackathons = hackathonarray)




def getUserIdFromEmail(email):
    cursor = conn.cursor()
    cursor.execute("SELECT user_id  FROM Users WHERE email = '{0}'".format(email))
    return cursor.fetchone()[0]

def isEmailUnique(email):
    #use this to check if a email has already been registered
    cursor = conn.cursor()
    if cursor.execute("SELECT email  FROM Users WHERE email = '{0}'".format(email)):
        #this means there are greater than zero entries with that email
        return False
    else:
        return True
#end login code

def isSkillUnique(skill_id,uid):
    #use this to check if a email has already been registered
    cursor = conn.cursor()
    if cursor.execute("SELECT *  FROM U_has_S WHERE s_id = '{0}' and u_id = '{1}'".format(skill_id,uid)):
        #this means there are greater than zero entries with that email
        return False
    else:
        return True
def isHackUnique(user_id, hackathon_id):
    #use this to check if a email has already been registered
    cursor = conn.cursor()
    if cursor.execute("SELECT *  FROM H_has_U WHERE h_id = '{0}' and u_id = '{1}'".format(hackathon_id,user_id)):
        #this means there are greater than zero entries with that email
        return False
    else:
        return True

@app.route('/')
def home():
    return render_template('homepage.html')

@app.route('/logged_in')
def welcome():
    return render_template('index.html', message = 'Welcome to hsociety', user_name = get_facebook_name(), user_picture_url = get_facebook_profile_url())





if __name__ == "__main__":
	#this is invoked when in the shell  you run
	#$ python app.py
	app.run(port=5000, debug=True)
