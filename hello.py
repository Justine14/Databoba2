from flask import Flask, render_template, session, redirect, url_for, flash		#6) render_template is for jinja2 and #11) user sessions #12) for flashing messages
from flask import make_response 				#4) takes the same values that can be returned from a return
from flask import abort							#5) for the username / invalid links
from flask_bootstrap import Bootstrap			#7) flask bootstrap 
from flask_moment import Moment 				#8) Date and time
from datetime import datetime					#9) date and time
from flask_wtf import FlaskForm					#10) checks whether data submitted by user is valid
from wtforms import StringField, SubmitField, PasswordField	#10)
from wtforms.validators import DataRequired, Email		#10)
import os 										#11) database configuration
from flask_sqlalchemy import SQLAlchemy 		#11

basedir = os.path.abspath(os.path.dirname(__file__))	#11)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:snowman7@localhost/databobadb' #could be localhost instead of 5432
	#'postgresql:///' + os.path.join(basedir, 'data.postgresql')		#11)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'This is a string for encrpytion'		#configure a secret key for web forms to protect CSRF attacks
bootstrap = Bootstrap(app)						#7) implement bootstrap
moment = Moment(app)
db = SQLAlchemy(app)							#11


#@app.route('/')
#def index():
#	return '<h1>Hello world!</h1>'

#@app.route('/user/<name>')
#def user(name):
#	return '<h1>Hello, {}!</h1>'.format(name)


#To handle bad requests
#@app.route('/')
#def index():
#	return '<h1>Bad Request</h1>', 400


#4)	create a response and set a cookie in it
#@app.route('/')
#def index():
#	response = make_response('<h1>This document carries a cookie</h1>')
#	response.set_cookie('answer', '42')
#	return response



#6) render_template 
#9) date and time 
#10) how to handle a web form with GET and POST request methods
#11) user sessions and redirect forms 
@app.route('/', methods=['GET', 'POST'])
def index():
	name = None
	form = NameForm()
	if form.validate_on_submit():
		#10)name = form.name.data
		#form.name.data = ''
		#11)session['name'] = form.name.data
		#return redirect(url_for('index'))
		old_name = session.get('name')
		if old_name is not None and old_name != form.name.data:
			flash('You have changed your name.')
		session['name'] = form.name.data
		return redirect(url_for('index'))
	return render_template('index.html', current_time=datetime.utcnow(), form=form, name=session.get('name'))
	#name=name

#Function takes filename as the first argument and the second is receiving a name variable
#name on the LHS represents the variable name, on the RHS, it is the current scope to provide the
#value on the left
@app.route('/user/<name>')
def user(name):
#	return '<h1>Hello, {}!<h1>'.format(name)
	return render_template('user2.html', name=name)


#5) This is for if a user / username links are not valid
#	load the user, if not valid, give 404 error, else, return Hello User
@app.route('/user/<id>')
def get_user(id):
	user = load_user(id)
	if not user:
		abort(404)
	else:
		return '<h1>Hello, {}</h1>'.format(user.name)


# Handling custom error pages
@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
	return render_template('500.html'), 500


#10) check whether data in the form is valid & checks all user input for their account
class NameForm(FlaskForm):
	name = StringField('What is your name?', validators=[DataRequired()])					#text field called name
	submit = SubmitField('Submit')															#submit button called submit
	email = StringField('Please provide your email address', validators=[Email()])				#requires email to be filled out & validated
	password = PasswordField('Please enter a password', validators=[DataRequired()])

#class Role(db.Model):
#	__drinks__=='roles'
#	id = db.Column(db.Integer, primary_key=True)
#	name = db.Column(db.String(64), unique=True)

#	def __repr__(self):
#		return '<Role %r>' % self.name

class User(db.Model):
	#__drinks__='users'
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), unique=True, index=True)
	email = db.Column(db.String(120), unique=True)

	def __init__(self, username, email):
		self.username = username
		self.email = email

	def __repr__(self):
		return '<User %r>' % self.username
	


