from flask_socketio import join_room,leave_room,emit
from pyjong import socketio
from flask_login import current_user
from flask import session
from time import time

#information to join room will be held in session
#function to join a room provided a users session data
@socketio.on('joined', namespace='/main/game')
def joined(message):

    room = session.get('room',None)
    join_room(room)
    emit('status', {'msg': session['username'] + 'がチャットルームに入りました'}, room=room)


@socketio.on('text', namespace='/main/game')
def text(message):
    room = session['room']
    print('text')
    emit('message', {'msg': session['username'] + ' : ' + message['msg']}, room=room)


@socketio.on('left', namespace='/main/game')
def left(message):
    room = session['room']
    leave_room(room)
    emit('status', {'msg': session.get('username') + ' has left the room.'}, room=room)
