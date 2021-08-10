from flask_socketio import join_room,leave_room,emit
from pyjong import app,db,socketio
from pyjong.models import retrieve_game_updates
from flask import render_template,session,flash,redirect,url_for
from flask_login import logout_user,login_required,current_user

import os

#create all db
#with app.app_context is necessary when importing alchemy db
with app.app_context():
    db.create_all()

#function to retrieve gameupdates for display on index page
def get_gameupdates():
    pass
    #gameupdates = GameUpdates.query.


@app.route('/',methods=['GET','POST'])
def index():
    game_updates = retrieve_game_updates()
    if current_user.is_authenticated:
        return redirect(url_for('main.friends'))
    return render_template('home.html',game_updates=game_updates)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash("ログアウトしました。",("alert-primary"))
    return redirect(url_for('index'))


print(os.path.dirname(__file__))

if __name__ == '__main__':
    socketio.run(app)
    #,host='0.0.0.0',port=5000
