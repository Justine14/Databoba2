#CPSC 471 - Databases, T02
#Group #4: Justine Bui, Pavel Chan, and Kevin Lee
#Credit to Flask Web Development, 2nd Edition, by Miguel Grinberg
#Credit to https://www.tutorialspoint.com/sqlite/index.htm for assistance for SQLite
#Credit to Colorlib for the front end 



from flask import Flask, render_template, session, redirect, url_for, flash		#6) render_template is for jinja2 and #11) user sessions #12) for flashing messages
from flask import make_response 				#4) takes the same values that can be returned from a return
from flask import abort							#5) for the username / invalid links
from flask_bootstrap import Bootstrap			#7) flask bootstrap 
from flask_moment import Moment 				#8) Date and time
from datetime import datetime					#9) date and time
from flask_wtf import FlaskForm					#10) checks whether data submitted by user is valid
from wtforms import StringField, SubmitField, PasswordField	#10)
from wtforms.validators import DataRequired, Email		#10)
import os 										#11) database configuration and #13) email
from flask_sqlalchemy import SQLAlchemy 		#11
#from flask_migrate import Migrate 				#12) PG 73 import flask migrate to keep track of database files instead of deleting all and creating all
from flask_mail import Mail 					#13)
from flask_mail import Message 					#14) integrating emails with the application


basedir = os.path.abspath(os.path.dirname(__file__))	#11)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////sqlite3/databoba.db'
	#'sqlite:///' + os.path.join(basedir, 'data.sqlite')		#11)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'This is a string for encrpytion'		#configure a secret key for web forms to protect CSRF attacks
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'					#13) sending email from our web app
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = ['Databoba']				#14)
app.config['FLASKY_MAIL_SENDER'] = 'Databoba Admin <databoba8@gmail.com>'
app.config['FLASKY_ADMIN'] = os.environ.get('FLASKY_ADMIN')			#15) sending mail to the admin after each new user 


bootstrap = Bootstrap(app)						#7) implement bootstrap
moment = Moment(app)
db = SQLAlchemy(app)							#11
#migrate = Migrate(app, db)						#12
mail = Mail(app)								#13






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
	#name = None
	form = NameForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.name.data).first()		#checks each name submitted to see if it has already been used
		#10)name = form.name.data
		#form.name.data = ''
		#11)session['name'] = form.name.data
		#return redirect(url_for('index'))
		#old_name = session.get('name')
		if user is None:
			user = User(username=form.name.data)
			db.session.add(user)
			db.session.commit()
			session['known'] = False
			if app.config['FLASKY_ADMIN']:
				send_email(app.config['FLASKY_ADMIN'], "New User", "mail/new_user", user=user)
		else:
			session['known'] = True

		session['name'] = form.name.data
		form.name.data = ''
		return redirect(url_for('index'))
	return render_template('index.html', current_time=datetime.utcnow(), form=form, name=session.get('name'), known=session.get('known', False))
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

# Shell context processor returns a ditionary that inclues the database instance and models so it does not have to be imported each time
#@app.shell_context_processor
#def make_shell_context():
#	return dict(db=db, User=User, Role=Role)


#10) check whether data in the form is valid & checks all user input for their account
class NameForm(FlaskForm):
	name = StringField('What is your name?', validators=[DataRequired()])					#text field called name
	submit = SubmitField('Submit')															#submit button called submit
	email = StringField('Please provide your email address', validators=[Email()])				#requires email to be filled out & validated
	password = PasswordField('Please enter a password', validators=[DataRequired()])

class Role(db.Model):
	__tablename__ ='roles'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), unique=True)
	users = db.relationship('User', backref='role')

	def __repr__(self):
		return '<Role %r>' % self.name

class User(db.Model):
	__tablename__ ='users'
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), unique=True, index=True)
	#email = db.Column(db.String(120), unique=True)
	role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

	#def __init__(self, username, email):
	#	self.username = username
	#	self.email = email

	def __repr__(self):
		return '<User %r>' % self.username
	

class DrinksTable(db.Model):
	id = db.Column('drink_id', db.Integer, primary_key=True)
	name = db.Column(db.String(100), unique=True)
	drinktype = db.Column(db.String(100))
	drinkflavour = db.Column(db.String(100))

	def __init__(self, name, ingredients):
		self.name = name
		self.ingredients = ingredients 


class FoodTable(db.Model):
	id = db.Column('food_id', db.Integer, primary_key=True)
	name = db.Column(db.String(100), unique=True)
	description = db.Column(db.String(100))
	ingredients = db.Column(db.String(100))

	def __init__(self, name, ingredients):
		self.name = name
		self.ingredients = ingredients



def send_email(to, subject, template, **kwargs):
	msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject, sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
	msg.body = render_template(template + '.txt', **kwargs)
	msg.html = render_template(template + '.html', **kwargs)
	mail.send(msg)