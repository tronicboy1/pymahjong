from flask import Flask, render_template,flash,request,session,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO,emit,join_room,leave_room
from flask_migrate import Migrate
from apps.forms import Login,SignUp,InviteFriend,FriendRequest,AcceptFriendRequest,JoinGame
from apps.model import UserData,ChatData,duplicate_username_check,username_password_check,add_friend,send_request,get_new_requests,get_friends_list,get_invites
import datetime
import os

#get base dir here for path to create db
basedir = os.path.abspath(os.path.dirname(__file__))

#create flask object
app = Flask(__name__)

#create database object
db = SQLAlchemy()
#link database to flask object
db.init_app(app)

#migration can be added if necessary with flask_migrate.Migrate
Migrate(app,db)

#create all db
#with app.app_context is necessary when importing alchemy db
with app.app_context():
    db.create_all()

app.config['SECRET_KEY'] = 'mykey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir,'data.sqlite')
#keep tracking figures off until necessary
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#create socketio for chat rooms
socketio = SocketIO(app)


#############################
####PAGE ROUTING############
##################################



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
        if session['authenticated']:
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
            return render_template('home.html',date_now=date_now,time_now=time_now,form_invite=form_invite,form_add=form_add,form_req=form_req)
        else:
            flash('入力に問題があるようです。すでにリクエストを送ったか、ユーザーネームが間違っていないかご確認ください。','alert-warning')
            return render_template('home.html',date_now=date_now,time_now=time_now,form_invite=form_invite,form_add=form_add,form_req=form_req)
    if form_add.validate_on_submit():
        for friend in form_add.select_friend.data:
            add_friend(requested_username=session['username'],requester_username=friend)
        session['new_requests'] = False
        session['requests'] = []
        get_friends_list(session['username'])
        flash('友達を追加しました！','alert-success')
        return render_template('home.html',date_now=date_now,time_now=time_now,form_invite=form_invite,form_add=form_add,form_req=form_req)
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
