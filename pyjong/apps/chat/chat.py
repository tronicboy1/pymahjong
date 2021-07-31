from flask_socketio import join_room,leave_room,emit
from pyjong import socketio
from flask_login import current_user
from flask import session

    #information to join room will be held in session
    #function to join a room provided a users session data
@socketio.on('joined',namespace='main/game')
def joined(message):
    room = session['room']
    join_room(room)
    print('room joined',username)
    emit('msg',{'msg':session['username'] + 'がパーティーに入りました。'},room=room)

    #function to leave a room
@socketio.on('left',namespace='main/game')
def left(message):
    room = session['room']
    leave_room(room)
    print('room left',username)
    emit('msg',{'msg':session['username'] + 'がパーティーから離れました。',room=room)

#send messages
@socketio.on('text',namespace='main/game')
def text(message):
    room = session['room']
    print('action')
    emit('msg',{'msg':session['username']+' : ' + message['msg']},room=room)
