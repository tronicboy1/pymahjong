import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


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


from pyjong.authentication.views import authentication_blueprint
from pyjong.main.views import main_blueprint

app.register_blueprint(authentication_blueprint,url_prefix='/authentication')
app.register_blueprint(main_blueprint,url_prefix='/main')
