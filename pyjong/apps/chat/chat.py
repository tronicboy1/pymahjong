from flask_socketio import join_room,leave_room,emit
from pyjong import socketio
from flask_login import current_user
from flask import session

    #information to join room will be held in session
    #function to join a room provided a users session data
@socketio.on('joined', namespace='/main/game')
def joined(message):
    """Sent by clients when they enter a room.
    A status message is broadcast to all people in the room."""
    room = session['room']
    print('joined')
    join_room(room)
    emit('status', {'msg': session.get('username') + ' has entered the room.'}, room=room)


@socketio.on('text', namespace='/main/game')
def text(message):
    """Sent by a client when the user entered a new message.
    The message is sent to all people in the room."""
    room = session['room']
    print('text')
    emit('message', {'msg': session.get('username') + ':' + message['msg']}, room=room)


@socketio.on('left', namespace='/main/game')
def left(message):
    """Sent by clients when they leave a room.
    A status message is broadcast to all people in the room."""
    room = session['room']
    leave_room(room)
    print('left room')
    emit('status', {'msg': session.get('username') + ' has left the room.'}, room=room)
