from flask_socketio import join_room,leave_room,emit
from pyjong import socketio
from flask_login import current_user
from flask import session,redirect
from pyjong.apps.mahjong.yama import Yama
from pyjong.apps.mahjong.game import Game
from time import time


#data will be stored in a universal variable as a dictionary
#the dictionary will have the current status of a game in a room saved
#{'room1':[kyoku,player1,player2......]}
room_dict = dict()


@socketio.on('start',namespace='/main/game')
def startgame():
    global room_dict
    if session['players'] == 1:
        game = Game()
        game.create_players(session['username'])
        room_dict[session['room']] = [game]
        emit('gameupdate',{'msg':'\n'+str(room_dict[session['room']][0].kyoku.current_player.name)+'\n'+str(room_dict[session['room']][0].kyoku.hai_remaining)})

@socketio.on('gamecheck',namespace='/main/game')
def gamecheck():
    global room_dict
    emit('gameupdate',{'msg':str(room_dict[session['room']][0].kyoku.yama.all_yama[0][0][0])})
