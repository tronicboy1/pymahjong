from pyjong import db,login_manager,bcrypt
from flask_login import UserMixin,current_user
from datetime import datetime
from sqlalchemy import desc

@login_manager.user_loader
def load_user(user_id):
    return UserData.query.get(user_id)

#rewrite UserData using flask Login
#UserMixin has all the functions to manage users and login
class UserData(db.Model,UserMixin):

    __tablename__ = 'userdata'

    #Login Data
    #########################################################
    id = db.Column(db.Integer,primary_key=True)
    #setting unique to True makes sure no two values are the same in a database
    email_address = db.Column(db.String(64),unique=True,index=True)
    username = db.Column(db.String(64),unique=True,index=True)
    password_hash = db.Column(db.String(128))

    ###########################################################

    #User data
    #friend list data will be stored as a python list to be evaluated and converted into a variable when necessary
    friends_list = db.Column(db.Text)
    friend_requests = db.Column(db.Text)
    invites = db.Column(db.Text)
    kyoku_win_count = db.Column(db.Integer)
    game_win_count = db.Column(db.Integer)
    points = db.Column(db.Integer)

    #connect to seperate database to post user updates to home page
    posts = db.relationship('GameUpdates',backref='userdata',lazy=True)

    ##################################################

    def __init__(self,email_address,username,password,friends_list,friend_requests,invites,kyoku_win_count,game_win_count,points):
        self.email_address = email_address
        self.username = username
        #hash input password when creating user class
        self.password_hash = bcrypt.generate_password_hash(password)
        self.friends_list = friends_list
        self.friend_requests = friend_requests
        self.invites = invites
        self.kyoku_win_count = kyoku_win_count
        self.game_win_count = game_win_count
        self.points = points

    #use bcrypt to check if input password is correct and return boolean
    def check_password(self,password):
        return bcrypt.check_password_hash(self.password_hash,password)

    def get_friends_list(self):
        return eval(self.friends_list)

class GameUpdates(db.Model):
    #add access to UserData db
    users = db.relationship(UserData)

    id = db.Column(db.Integer,primary_key=True)
    #link to UserData database ids, userdata is name of UserData db
    user_id = db.Column(db.Integer,db.ForeignKey('userdata.id'))

    date = db.Column(db.DateTime,nullable=False,default=datetime.now)
    text = db.Column(db.Text,nullable=False)

    def __init__(self,text,user_id):
        self.text = text
        self.user_id = user_id





###FUNCTIONS FOR DB HANDLING#################
#############################################

def new_game_update(text):

    game_update = GameUpdates(user_id=current_user.id,text=text)

    db.session.add(game_update)
    db.session.commit()
    print('gameupdate added')

def retrieve_game_updates():
    #retrieve gameupdates in descending order by date
    game_updates = GameUpdates.query.order_by(GameUpdates.date.desc()).paginate(page=1,per_page=5)
    return game_updates
