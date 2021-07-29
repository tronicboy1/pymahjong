from flask import Flask, render_template,flash,request,session,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_socketio import SocketIO,emit,join_room,leave_room
from flask_migrate import Migrate
from wtforms import StringField,SubmitField,PasswordField,SelectField
from wtforms.validators import DataRequired,Regexp,Email,EqualTo,InputRequired
import datetime
import os

#get base dir here for path to create db
basedir = os.path.abspath(os.path.dirname(__file__))

#create flask object
app = Flask(__name__)

app.config['SECRET_KEY'] = 'mykey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir,'data.sqlite')
#keep tracking figures off until necessary
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#create socketio for chat rooms
socketio = SocketIO(app)


#create database object and link to flask object
db = SQLAlchemy(app)
#migration can be added if necessary with flask_migrate.Migrate
Migrate(app,db)

#parent class
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

###FUNCTIONS FOR DB HANDLING############

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
def add_friend(newfriend_username,requester_username):
    pass

#this function will call the username of a friend that a user invited and add to their database the username of the invitee
def send_invite(friend_username):
    pass

#call username and retrieve invites. invites retrieved will be transferred to session memory and deleted form database
def get_invites(session_username):
    current_usr = UserData.query.filter_by(username=session_username).first()
    invites = eval(current_usr.invites)

    if len(invites) > 0:
        current_usr.invites = str([])
        db.session.add(current_usr)
        db.session.commit()
        return [(username,username) for username in invites]
    else:
        return ('no_invites','招待されていないようです')

##################################


#create all db
db.create_all()


class Login(FlaskForm):
    #Username and paassword will be checked to have value
    username = StringField('ユーザーネーム：',validators=[InputRequired(),Regexp('^\w+$',message='英数字のみ入力可能')])
    password = PasswordField('パスワード：',validators=[InputRequired()])
    submit = SubmitField('ログイン')

#form for user sign up with checks on input
class SignUp(FlaskForm):
    #email validator to check email is correct format
    email_address = StringField('メールアドレス：',validators=[InputRequired(),Email("正しいメールアドレスを入力してください")])
    password = PasswordField('パスワード：',validators=[InputRequired()])
    #confirms username has correct characters
    username = StringField('ユーザーネーム：',validators=[InputRequired(),Regexp('^\w+$',message='英数字のみ入力可能')])
    submit = SubmitField('登録')

#Form for users to invite friends to game
class InviteFriend(FlaskForm):
    select_friend = SelectField("招待したい友達を選んでください")
    submit = SubmitField("招待する")

#form for users to send friend requests
class FriendRequest(FlaskForm):
    username = StringField('友達として追加したいユーザーネーム：',validators=[InputRequired(),Regexp('^\w+$',message='英数字のみ入力可能')])
    submit = SubmitField('リクエストを送る')

#form for users to join games invited
class JoinGame(FlaskForm):


    select_friend = SelectField("招待したい友達を選んでください")
    submit = SubmitField("招待する")



@app.route('/')
def index():
    date_now = datetime.date.today()
    time_now = datetime.datetime.now().strftime('%H:%M:%S')
    return render_template('home.html',date_now=date_now,time_now=time_now)

@app.route('/login',methods=['GET','POST'])
def login():

    form = Login()

    if form.validate_on_submit():
        if username_password_check(form.username.data,form.password.data):
            session['username'] = form.username.data
            session['invites_updated'] = False
            session['authenticated'] = True
            return redirect(url_for('logged_in'))
        else:
            return render_template('login.html',form=form,errors=True)

    return render_template('login.html',form=form,errors=False)

@app.route('/signup',methods=['GET','POST'])
def signup():

    form = SignUp()

    if form.validate_on_submit():
        #check username to see if no duplicates in db
        if duplicate_username_check(form.username.data):
            #save data to database
            new_user = UserData(username=form.username.data,email_address=form.email_address.data,password=form.password.data,friends_list="[]",friend_requests="[]",invites="[]",chat_id=None,kyoku_win_count=0,game_win_count=0,points=0)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = form.username.data
            session['invites_updated'] = False
            session['authenticated'] = True
            print(session)
            return redirect(url_for('signed_up'))
        #send user back to signup page and display duplicate username error
        else:
            return render_template('signup.html',form=form,errors=['ユーザーネームはすでに登録されている'])
    return render_template('signup.html',form=form,errors=False)

@app.route('/signed_up')
def signed_up():
    return render_template('signed_up.html')
@app.route('/logged_in')
def logged_in():
    return render_template('logged_in.html')
@app.route('/logout')
def logout():
    session['authenticated'] = False
    session['username'] = ''
    return render_template('logout.html')


@app.route('/friends',methods=['GET','POST'])
def friends():
    #function to generate friend lists for invite choice
    def get_friends(form_invite):
        current_usr = UserData.query.filter_by(username=session['username']).first()
        friends_list = eval(current_usr.friends_list)
        if len(friends_list) > 0:
              [(usr.username,usr.username) for usr in friends_list]
        else:
            form_invite.select_friend.choices = [('no_friends','友達はまだいないようです')]
        return form_invite
    #function to generate friend requests
    def new_friend_requests(form_add):

        return form_add


    try:
        if session['invites_updated'] == False and session['authenticated']:
            session['invites'] = get_invites()
            session['invites_updated'] = True
            session['friends'] = get_friends()

            form_invite = InviteFriend()
            form_invite = get_friends(form_invite)
            form_add = FriendRequest()


    except:
        pass
    return render_template('friends.html')

@app.route('/game')
def game():
    return render_template('game.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
