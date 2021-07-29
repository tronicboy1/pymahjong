from flask import Flask, render_template,flash,request,session,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_socketio import SocketIO,emit,join_room,leave_room
from flask_migrate import Migrate
from wtforms import StringField,SubmitField,PasswordField,SelectField,RadioField,SelectMultipleField
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
    #try to check and see if requests pulled from the database still havent been addressed in same session
    try:
        if len(new_requests_list) > 0:
            session['requests'] = new_requests_list
            session['new_requests'] = True
            current_usr.friend_requests = str([])
            db.session.add(current_usr)
            db.session.commit()
        elif session['new_requests']:
            pass
        else:
            session['new_requests'] = False
            session['requests'] = []
    except:
        if len(new_requests_list) > 0:
            session['requests'] = new_requests_list
            session['new_requests'] = True
            current_usr.friend_requests = str([])
            db.session.add(current_usr)
            db.session.commit()
        else:
            session['new_requests'] = False
            session['requests'] = []

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
    username = StringField('追加したいユーザーネーム：',validators=[InputRequired(),Regexp('^\w+$',message='英数字のみ入力可能')])
    submit = SubmitField('リクエストを送る')

#form to accept friend requests if user has new ones
class AcceptFriendRequest(FlaskForm):
    select_friend = SelectMultipleField("承諾したいリクエストを選んでください")
    submit = SubmitField("承諾する")

#form for users to join games invited
class JoinGame(FlaskForm):
    pass


    select_friend = SelectField("招待したい友達を選んでください")
    submit = SubmitField("招待する")



@app.route('/',methods=['GET','POST'])
def index():
    date_now = datetime.date.today()
    time_now = datetime.datetime.now().strftime('%H:%M:%S')
    #function to generate friend lists for invite choice
    def add_friends_to_form(form_invite):
        if len(session['friends']) > 0:
            form_invite.select_friend.choices = [(usr,usr) for usr in session['friends']]
        else:
            form_invite.select_friend.choices = [('no_friends','友達はまだいないようです')]
        return form_invite
    #function to add friend requests to form
    def add_friend_requests_to_form(form_add):
        if session['new_requests']:
            form_add.select_friend.choices = [(usr,usr) for usr in session['requests']]
        else:
            form_add.select_friend.choices = [('no_friends','友達はまだいないようです')]
        return form_add

    #pull user data from database to session for easy access
    try:
        if session['updated'] == False and session['authenticated']:
            get_new_requests(session['username'])
            get_invites(session['username'])
            get_friends_list(session['username'])
            session['updated'] = True
        elif session['authenticated']:
            get_new_requests(session['username'])
            get_invites(session['username'])
            get_friends_list(session['username'])
    except:
        return render_template('home.html',date_now=date_now,time_now=time_now)

    #add choices to forms
    form_invite = InviteFriend()
    form_invite = add_friends_to_form(form_invite)
    form_req = FriendRequest()
    form_add = AcceptFriendRequest()
    form_add = add_friend_requests_to_form(form_add)

    #check all forms for positive return
    if form_invite.validate_on_submit():
        pass
    if form_req.validate_on_submit():
        if send_request(requester_username=session['username'],requested_username=form_req.username.data):
            flash(f'{form_req.username.data}にリクエストを送りました！','alert-success')
            return render_template('home.html',form_invite=form_invite,form_add=form_add,form_req=form_req)
        else:
            flash('入力に問題があるようです。すでにリクエストを送ったか、ユーザーネームが間違っていないかご確認ください。','alert-warning')
            return render_template('home.html',form_invite=form_invite,form_add=form_add,form_req=form_req)
    if form_add.validate_on_submit():
        for friend in form_add.select_friend.data:
            add_friend(requested_username=session['username'],requester_username=friend)
        session['new_requests'] = False
        session['requests'] = []
        get_friends_list(session['username'])
        flash('友達を追加しました！','alert-success')
        return render_template('home.html',form_invite=form_invite,form_add=form_add,form_req=form_req)
    return render_template('home.html',date_now=date_now,time_now=time_now,form_invite=form_invite,form_add=form_add,form_req=form_req)

@app.route('/login',methods=['GET','POST'])
def login():

    form = Login()

    if form.validate_on_submit():
        if username_password_check(form.username.data,form.password.data):
            session['username'] = form.username.data
            session['updated'] = False
            session['authenticated'] = True
            flash(f"ログインできました。お帰りなさい、{session['username']}。",'alert-success')
            return redirect(url_for('index'))
        else:
            flash('パスワードもしくはユーザーネームが間違っていたようです。','alert-danger')
            return render_template('login.html',form=form)

    return render_template('login.html',form=form)

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
            session['updated'] = False
            session['authenticated'] = True
            flash(f"{session['username']}、登録できました！",'alert-success')
            return redirect(url_for('index'))
        #send user back to signup page and display duplicate username error
        else:
            flash('ユーザーネームはすでに登録されている','alert-warning')
            return render_template('signup.html',form=form)
    return render_template('signup.html',form=form)


@app.route('/logout')
def logout():
    session.clear()
    flash("ログアウトしました。",("alert-primary"))
    return redirect(url_for('index'))

@app.route('/game')
def game():
    return render_template('game.html')

@app.route('/info')
def info():
    return render_template('info.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
