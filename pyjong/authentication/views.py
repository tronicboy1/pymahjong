from flask import Blueprint,render_template,redirect,url_for,flash,session
from pyjong import db
from pyjong.models import UserData
from pyjong.authentication.forms import Login,SignUp
import datetime

authentication_blueprint = Blueprint('authentication',__name__,template_folder='templates/authentication')



############################################
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


##################################################
##################################################
##Views for Authentication##
###########################


@authentication_blueprint.route('/login',methods=['GET','POST'])
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

@authentication_blueprint.route('/signup',methods=['GET','POST'])
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
