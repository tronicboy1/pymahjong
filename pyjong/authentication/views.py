from flask import Blueprint,render_template,redirect,url_for,flash,session,abort,request
from pyjong import db,bcrypt
from pyjong.models import UserData,duplicate_username_email_check,username_password_check,get_friends_list,new_game_update
from pyjong.authentication.forms import Login,SignUp
from flask_login import login_user,login_required,logout_user,current_user
import datetime

authentication_blueprint = Blueprint('authentication',__name__,template_folder='templates/authentication')







##################################################
##################################################
##Views for Authentication##
###########################


@authentication_blueprint.route('/login',methods=['GET','POST'])
def login():

    form = Login()

    if form.validate_on_submit():
        user = UserData.query.filter_by(username=form.username.data).first()
        #check if username and password are correct
        if user:
            if user.check_password(form.password.data):
                login_user(user)
                #update session info for use with other request checks
                session['username'] = form.username.data
                session['updated'] = False
                session['in_room'] = False
                session['has_new_invites'] = False
                session['players'] = 1
                get_friends_list(session['username'])
                next = request.args.get('next')
                #check if user was redirected, and send them to the page they were trying to access before login
                if next == None or not next[0] == '/':
                    flash(f"ログインできました。お帰りなさい、{current_user.username}。",'alert-success')
                    return redirect(url_for('index'))
                else:
                    flash(f"ログインできました。お帰りなさい、{current_user.username}。",'alert-success')
                    return redirect(next)
        else:
            flash('パスワードもしくはユーザーネームが間違っていたようです。','alert-danger')
            return render_template('login.html',form=form)

    return render_template('login.html',form=form)

@authentication_blueprint.route('/signup',methods=['GET','POST'])
def signup():

    form = SignUp()

    if form.validate_on_submit():
        #check username to see if no duplicates in db
        if duplicate_username_email_check(form.username.data,form.email_address.data):
            #save data to database
            new_user = UserData(username=form.username.data,email_address=form.email_address.data,password=form.password.data,friends_list="[]",friend_requests="[]",invites="[]",kyoku_win_count=0,game_win_count=0,points=0)
            db.session.add(new_user)
            db.session.commit()
            #add update to board of new player registration
            new_game_update(text=f"{form.username.data}が新しくPyJongに登録しました！友達リクエストを送りましょう！")

            #update session info for use with other request checks
            session['updated'] = False
            session['username'] = form.username.data
            session['in_room'] = False
            session['has_new_invites'] = False
            session['players'] = 0
            login_user(new_user)
            flash(f"{current_user.username}、登録できました！",'alert-success')
            return redirect(url_for('index'))
        #send user back to signup page and display duplicate username error
        else:
            flash('ユーザーネームもしくはメールアドレスはすでに登録されている','alert-danger')
            return render_template('signup.html',form=form)
    return render_template('signup.html',form=form)
