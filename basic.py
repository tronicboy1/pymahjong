from flask import Flask, render_template,request
import datetime

app = Flask(__name__)

login_status = False

@app.route('/')
def index():
    date_now = datetime.date.today()
    time_now = datetime.datetime.now().strftime('%H:%M:%S')
    return render_template('home.html',date_now=date_now,time_now=time_now,
    login_status=login_status)

@app.route('/login')
def login():
    return render_template('login.html',login_status=login_status)

@app.route('/signup')
def signup():
    return render_template('signup.html',login_status=login_status)

@app.route('/signed_up')
def signed_up():
    #checks username to see if it fits criteria
    def username_check(username):
        has_lower = False
        has_upper = False
        ends_num = username[-1].isdigit()
        for char in username:
            if char.islower():
                has_lower = True
            elif char.isupper():
                has_upper = True
            elif char == ' ':
                return False
                
        if has_lower and has_upper and ends_num:
            return True
        else:
            return False

    #retrieve information from submitted form
    request.args.get('email')
    request.args.get('password')
    username = request.args.get('username')

    username_result = username_check(username)
    #send user to signed up page if username meets criteria
    if username_result:
        return render_template('signed_up.html', login_status=login_status,username=username)
    #send user back to signup page and display error
    else:
        return render_template('signup.html', username_result=False)


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
