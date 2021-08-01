from flask_socketio import join_room,leave_room,send
from pyjong import socketio
from flask_login import current_user
from flask import session

    #information to join room will be held in session
    #function to join a room provided a users session data
@socketio.on('joined')
def joined():
    room = session['room']
    join_room(room)
    print('room joined')
    send(f'{session['username']}joined',room=room)

    #function to leave a room
@socketio.on('left')
def left():
    room = session['room']
    leave_room(room)
    print('room left',username)
    send(session['username'] + 'がパーティーから離れました。',room=room)

#send messages
@socketio.on('message')
def message(msg):
    room = session['room']
    print('action')
    send(msg,broadcast=True,room=room)
