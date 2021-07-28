from flask import Flask, render_template,flash,request,session,redirect,url_for
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,PasswordField
from wtforms.validators import DataRequired,Regexp,Email,EqualTo,InputRequired
import datetime

app = Flask(__name__)

app.config['SECRET_KEY'] = 'mykey'

login_status = False

#form for user sign up with checks on input
class SignUp(FlaskForm):

    #email validator to check email is correct format
    email_address = StringField('メールアドレス',validators=[InputRequired(),Email("正しいメールアドレスを入力してください")])
    #confirms password is input correctly twice
    password = PasswordField('パスワード',validators=[InputRequired()])
    #confirms username has correct characters
    username = StringField('ユーザーネーム',validators=[InputRequired(),Regexp('^\w+$',message='英数字のみ入力可能')])


@app.route('/')
def index():
    date_now = datetime.date.today()
    time_now = datetime.datetime.now().strftime('%H:%M:%S')
    return render_template('home.html',date_now=date_now,time_now=time_now,
    login_status=login_status)

@app.route('/login')
def login():
    return render_template('login.html',login_status=login_status)

@app.route('/signup',methods=['get','post'])
def signup():

    form = SignUp()

    if form.validate_on_submit():
        #save data to database
        session['email_address'] = form.email_address.data
        session['password'] = form.password.data
        session['username'] = form.username.data
        print(session)
        return redirect(url_for('signed_up'))

    return render_template('signup.html',login_status=login_status,form=form)

@app.route('/signed_up')
def signed_up():
    return render_template('signed_up.html')


@app.route('/friends')
def friends():
    return render_template('friends.html',login_status=login_status)

@app.route('/game')
def game():
    return render_template('game.html',login_status=login_status)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
