import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

#create login manager object
login_manager= LoginManager()

#set login manager warning message to Japanese
login_manager.login_message = u"このページにアクセスするためにはログインする必要があります。"
login_manager.login_message_category = "alert-warning"

#Create Bcrypt object
bcrypt = Bcrypt()

#create flask object
app = Flask(__name__)


#get base dir here for path to create db
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SECRET_KEY'] = 'mykey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir,'data.sqlite')
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

from pyjong.authentication.views import authentication_blueprint
from pyjong.main.views import main_blueprint

app.register_blueprint(authentication_blueprint,url_prefix='/authentication')
app.register_blueprint(main_blueprint,url_prefix='/main')
