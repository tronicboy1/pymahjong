from flask_socketio import join_room,leave_room,emit
from pyjong import socketio
from flask_login import current_user
from flask import session

    #information to join room will be held in session
    #function to join a room provided a users session data
@socketio.on('join')
def on_join(session):
    username = session['username']
    room = session['room']
    join_room(room)
    emit(username + 'がパーティーに入りました。',to=room)

    #function to leave a room
@socketio.on('leave')
def on_leave(session):
    username = session['username']
    room = session['room']
    leave_room(room)
    emit(username + 'がパーティーから離れました。',to=room)

#send messages
@socketio.on('text')
def text(session,message):
    room = session['room']
    emit('message',{'msg':session['username']+' : ' + message},room=room)
