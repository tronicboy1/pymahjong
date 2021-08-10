import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
#from sqlalchemy.orm import scoped_session,sessionmaker
#from sqlalchemy.ext.declarative import declarative_base
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO


#create login manager object
login_manager= LoginManager()

#set login manager warning message to Japanese
login_manager.login_message = u"このページにアクセスするためにはログインする必要があります。"
login_manager.login_message_category = "alert-warning"
login_manager.login_view = 'authentication.login'

#Create Bcrypt object
bcrypt = Bcrypt()

#create flask object
app = Flask(__name__)


#get base dir here for path to create db
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SECRET_KEY'] = 'mykey'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir,'data.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://tygdtcltbosejz:1a622409a191010e308c49a607343f1ab72d2bc66e7f90bba894f5dc42140cb0@ec2-44-194-145-230.compute-1.amazonaws.com:5432/d5g33isn665nuf'
#keep tracking figures off until necessary
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#create database object
db = SQLAlchemy(app)
#migration can be added if necessary with flask_migrate.Migrate
Migrate(app,db)

#link login manager to flask app
login_manager.init_app(app)
#designate login managers page to be used
login_manager.login_view = 'authentication.login'

#add socket IO
socketio = SocketIO(app)



#data will be stored in a universal variable as a dictionary
#the dictionary will have the current status of a game in a room saved
#{'room1':[kyoku,player1,player2......]}
room_dict = dict()

#Data to make start new game will be stored in this global dictionary
room_players = dict()


from pyjong.authentication.views import authentication_blueprint
from pyjong.main.views import main_blueprint
from pyjong.error_handler.errors import error_pages

app.register_blueprint(authentication_blueprint,url_prefix='/authentication')
app.register_blueprint(main_blueprint,url_prefix='/main')
app.register_blueprint(error_pages,url_prefix='/error/')
