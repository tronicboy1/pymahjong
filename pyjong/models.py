from pyjong import db,login_manager,bcrypt
from flask_login import UserMixin,current_user
from datetime import datetime
from sqlalchemy import desc
from flask import session
import pytz

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

    ##################################################

    def __init__(self,email_address,username,password,friends_list,friend_requests,invites,kyoku_win_count,game_win_count,points):
        self.email_address = email_address
        self.username = username
        #hash input password when creating user class
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        self.friends_list = friends_list
        self.friend_requests = friend_requests
        self.invites = invites
        self.kyoku_win_count = kyoku_win_count
        self.game_win_count = game_win_count
        self.points = points

    #use bcrypt to check if input password is correct and return boolean
    def check_password(self,password):
        return bcrypt.check_password_hash(self.password_hash,password.encode('utf-8'))

    def get_friends_list(self):
        return eval(self.friends_list)

class GameUpdates(db.Model):

    id = db.Column(db.Integer,primary_key=True)

    date = db.Column(db.DateTime,nullable=False,default=datetime.now)
    text = db.Column(db.Text,nullable=False)

    def __init__(self,text,user_id):
        self.text = text





###FUNCTIONS FOR DB HANDLING#################
#############################################

def new_game_update(text):

    game_update = GameUpdates(user_id=current_user.id,text=text)

    db.session.add(game_update)
    db.session.commit()


def retrieve_game_updates():
    #retrieve gameupdates in descending order by date
    game_updates = GameUpdates.query.order_by(GameUpdates.date.desc()).paginate(page=1,per_page=5)
    return game_updates

#adds new friend to both the requester and requested
def add_friend(requested_username,requester_username):
    #add requester to requested
    result1 = UserData.query.filter_by(username=requested_username).first()
    new_friends_list = eval(result1.friends_list)
    new_friends_list.append(requester_username)
    result1.friends_list = str(new_friends_list)
    #add requested to requester
    result2 = UserData.query.filter_by(username=requester_username).first()
    new_friends_list = eval(result2.friends_list)
    new_friends_list.append(requested_username)
    result2.friends_list = str(new_friends_list)

    db.session.add_all([result1,result2])
    db.session.commit()

    ##check to see if written correctly
    # result1 = UserData.query.filter_by(username=requested_username).first()
    # result2 = UserData.query.filter_by(username=requester_username).first()
    # print(result1.friends_list,result2.friends_list)

#removes friends from both users
def delete_friend(requested_username,requester_username):
    #add requester to requested
    result1 = UserData.query.filter_by(username=requested_username).first()
    new_friends_list = eval(result1.friends_list)
    new_friends_list.remove(requester_username)
    result1.friends_list = str(new_friends_list)
    #add requested to requester
    result2 = UserData.query.filter_by(username=requester_username).first()
    new_friends_list = eval(result2.friends_list)
    new_friends_list.remove(requested_username)
    result2.friends_list = str(new_friends_list)

    db.session.add_all([result1,result2])
    db.session.commit()

    ##check to see if written correctly
    result1 = UserData.query.filter_by(username=requested_username).first()
    result2 = UserData.query.filter_by(username=requester_username).first()
    print(result1.friends_list,result2.friends_list)


#adds new friend request to requested user from requesting user
def send_request(requester_username,requested_username):
    result = UserData.query.filter_by(username=requested_username).all()
    if len(result) > 0 and requester_username != requested_username:
        result = result[0]
        new_friend_requests = eval(result.friend_requests)
        #check to make sure multiple requests are not being sent
        if requester_username in new_friend_requests:
            return False
        else:
            new_friend_requests.append(requester_username)
            result.friend_requests = str(new_friend_requests)
            db.session.add(result)
            db.session.commit()
            return True
    else:
        return False

#gets new friend request from db and adds to session, deleting from db
def get_new_requests(session_username):
    current_usr = UserData.query.filter_by(username=session_username).first()
    new_requests_list = eval(current_usr.friend_requests)

    if session['updated'] == False:
        if len(new_requests_list) > 0:
            session['requests'] = new_requests_list
            session['new_requests'] = True
            current_usr.friend_requests = str([])
            db.session.add(current_usr)
            db.session.commit()
            session['updated'] = True
        else:
            session['new_requests'] = False
            session['updated'] = True
            session['requests'] = []
    else:
        if len(new_requests_list) > 0:
            for request in new_requests_list:
                session['requests'].append(request)
            session['new_requests'] = True
            current_usr.friend_requests = str([])
            db.session.add(current_usr)
            db.session.commit()
        else:
            pass

#retrieve list of users friends
def get_friends_list(session_username):
    current_usr = UserData.query.filter_by(username=session_username).first()
    friends_list = eval(current_usr.friends_list)
    session['friends'] = friends_list

    #add self to see users own stat
    friends_list_stat = friends_list.copy()
    friends_list_stat.insert(0,session['username'])
    if len(friends_list) > 0:
        session['has_friends'] = True
        #retrieve friend stats
        session['friend_stats'] = list()
        for friend in friends_list_stat:
            friend_info = UserData.query.filter_by(username=friend).first()
            session['friend_stats'].append([friend,friend_info.kyoku_win_count,friend_info.game_win_count,friend_info.points])
    else:
        session['has_friends'] = False
        session['friend_stats'] = list()
        for friend in friends_list_stat:
            friend_info = UserData.query.filter_by(username=friend).first()
            session['friend_stats'].append([friend,friend_info.kyoku_win_count,friend_info.game_win_count,friend_info.points])


#call username and retrieve invites. invites retrieved will be transferred to session memory and deleted form database
def get_invites(session_username):
    current_usr = UserData.query.filter_by(username=session_username).first()
    invites = eval(current_usr.invites)
    if session['has_new_invites'] and len(invites) > 0:
        for invite in invites:
            session['invites'].append(invite)
        current_usr.invites = str([])
        db.session.add(current_usr)
        db.session.commit()
    elif len(invites) > 0 and session['has_new_invites'] == False:
        session['has_new_invites'] = True
        session['invites'] = invites
        current_usr.invites = str([])
        db.session.add(current_usr)
        db.session.commit()
    elif session['has_new_invites']:
        pass
    else:
        session['has_new_invites'] = False

#invites will include senders name and room name '['username','room']'
def send_invite(session_username,invited_username,room):
    user = UserData.query.filter_by(username=invited_username).first()
    invites = eval(user.invites)
    invites.append((session_username,room))
    user.invites = str(invites)
    db.session.add(user)
    db.session.commit()


#checks username for duplicates
def duplicate_username_email_check(potential_username,potential_email):
    if len(UserData.query.filter_by(username=potential_username).all()) == 0:
        if len(UserData.query.filter_by(email_address=potential_email).all()) == 0:
            return True
    else:
        return False

#checks username to see if registered and if supplied password is correct
def username_password_check(potential_username,input_password):
    result = UserData.query.filter_by(username=potential_username).all()
    if len(result) > 0:
        result = result[0]
        if bcrypt.check_password_hash(result.password,input_password):
            return True
        else:
            return False
    else:
        return False
