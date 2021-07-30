from pyjong import db

class UserData(db.Model):

    #override default name
    __tablename__ = 'userdata'

    #create primary keys for user data to be stored
    id = db.Column(db.Integer,primary_key=True)

    #values to be stored in userdata db
    username = db.Column(db.Text)
    email_address = db.Column(db.Text)
    password = db.Column(db.Text)
    #friend list data will be stored as a python list to be evaluated and converted into a variable when necessary
    friends_list = db.Column(db.Text)
    friend_requests = db.Column(db.Text)
    invites = db.Column(db.Text)
    kyoku_win_count = db.Column(db.Integer)
    game_win_count = db.Column(db.Integer)
    points = db.Column(db.Integer)
    #chat data will be stored in seperate db ChatData so multiple users can access
    chat_id = db.Column(db.Integer,db.ForeignKey('chatdata.id'))
    chat = db.relationship('ChatData')

    #assign db values as attributes for easy access
    def __init__(self,username,email_address,password,friends_list,friend_requests,invites,chat_id,kyoku_win_count,game_win_count,points):
        self.username = username
        self.email_address = email_address
        self.password = password
        self.friends_list = friends_list
        self.friend_requests = friend_requests
        self.invites = invites
        self.kyoku_win_count = kyoku_win_count
        self.game_win_count = game_win_count
        self.points = points
        #users will have chatroom id associated with their account while in a chat room
        self.chat_id = chat_id

#child database to hold chat info connected to many users
#may not be necessary with sockeio
class ChatData(db.Model):

    __tablename__ = 'chatdata'

    id = db.Column(db.Integer,primary_key=True)
    #chat data will be stored as '[time_of_post,user_posted,content]' to be evaluted in python
    chat_content = db.Column(db.Text)

    def __init__(self,chat_content):
        self.chat_content = chat_content





###FUNCTIONS FOR DB HANDLING#################
#############################################





#checks username for duplicates
def duplicate_username_check(potential_username):
    result = UserData.query.filter_by(username=potential_username).all()
    if len(result) == 0:
        return True
    else:
        return False

#checks username to see if registered and if supplied password is correct
def username_password_check(potential_username,input_password):
    result = UserData.query.filter_by(username=potential_username).all()
    if len(result) > 0:
        result = result[0]
        if result.password == input_password:
            return True
        else:
            return False
    else:
        return False


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

    if len(new_requests_list) > 0:
        session['requests'] = new_requests_list
        session['new_requests'] = True
        current_usr.friend_requests = str([])
        db.session.add(current_usr)
        db.session.commit()
    else:
        session['new_requests'] = False

#retrieve list of users friends
def get_friends_list(session_username):
    current_usr = UserData.query.filter_by(username=session_username).first()
    friends_list = eval(current_usr.friends_list)
    session['friends'] = friends_list
    if len(friends_list) > 0:
        session['has_friends'] = True
        #retrieve friend stats
        session['friend_stats'] = dict()
        # for friend in session['friends']:
        #     current_usr = UserData.query.filter_by(username=friend).first()


    else:
        session['has_friends'] = False
    return friends_list

#call username and retrieve invites. invites retrieved will be transferred to session memory and deleted form database
def get_invites(session_username):
    current_usr = UserData.query.filter_by(username=session_username).first()
    invites = eval(current_usr.invites)
    if len(invites) > 0:
        session['has_new_invites'] = True
        session['invites'] = invites
        current_usr.invites = str([])
        db.session.add(current_usr)
        db.session.commit()
    else:
        session['has_new_invites'] = False




#########################################################
##########################################################
