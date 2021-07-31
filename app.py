from pyjong import app,db,socketio
from flask import render_template,session,flash,redirect,url_for
from flask_login import logout_user,login_required,current_user
import datetime

#create all db
#with app.app_context is necessary when importing alchemy db
with app.app_context():
    db.create_all()

@app.route('/',methods=['GET','POST'])
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.friends'))
    date_now = datetime.date.today()
    time_now = datetime.datetime.now().strftime('%H:%M:%S')
    return render_template('home.html',date_now=date_now,time_now=time_now)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash("ログアウトしました。",("alert-primary"))
    return redirect(url_for('index'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404



if __name__ == '__main__':
    #socketio.run(app, debug=True)
    app.run(debug=True)
