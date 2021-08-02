from flask_socketio import join_room,leave_room,emit
from pyjong import socketio
from flask_login import current_user
from flask import session,redirect
from time import time


#data will be stored in a universal variable as a dictionary
#the dictionary will have the current status of a game in a room saved
#{'room1':[kyoku,player1,player2......]}
room_dict = dict()

#room dict is used in Kyoku so import must be done after creation
from pyjong.apps.mahjong.yama import Yama
from pyjong.apps.mahjong.game import Game



#################################################
###MAHJONG FUNCTIONS
#################################################
def cycle_to_human():
    while room_dict[session['room']][0].kyoku.current_player.is_computer:
        room_dict[session['room']][0].kyoku.player_turn()
    room_dict[session['room']][0].kyoku.player_turn()




@socketio.on('start',namespace='/main/game')
def startgame():
    global room_dict
    if session['players'] == 1:
        game = Game()
        game.create_players(session['username'])
        game.oya_gime()
        room_dict[session['room']] = [game,'',0]
        room_dict[session['room']][0].kyoku.kyoku_start()
        #kyoku.game will set index 1 value of room dict to define what the next input will be
        #index2 will be used for iterations



@socketio.on('gamecheck',namespace='/main/game')
def gamecheck():
    global room_dict
    emit('gameupdate',{'msg':str(room_dict[session['room']][0].kyoku.yama.all_yama[0][0][0])})

@socketio.on('gamecontrol',namespace='/main/game')
def gamecontrol(choice):
    choice = choice['msg'].upper()
    print(choice)
    #check what the next input type will be
    if room_dict[session['room']][1] == 'kyokustart_yesno':
        if choice == 'Y':
            room_dict[session['room']][0].kyoku.kyoku_start_non_computer(choice)
            cycle_to_human()
        else:
            room_dict[session['room']][0].kyoku.kyoku_start_non_computer(choice)
            cycle_to_human()
        print('socketio kyoku start yes no')
    #condition for asking to get rid of a hai and accept mochihai
    elif room_dict[session['room']][1] == 'kyoku_yesno':
        if choice == 'Y':
            room_dict[session['room']][0].kyoku.player_turn_input(choice)
        else:
            room_dict[session['room']][0].kyoku.player_turn_input(choice)
            cycle_to_human()
        print('socketio yesno executed')
    #condition for asking which hai to throw into kawa
    elif room_dict[session['room']][1] == 'sutehai':
        if choice.isdigit():
            room_dict[session['room']][0].kyoku.current_player.sutehai_user_input(choice)
            room_dict[session['room']][0].kyoku.after_player_sutehai()
            cycle_to_human()
        else:
            emit('gameupdate',{'msg':'不適切な入力がありました。'})
    #condition for ron atama_check
    elif room_dict[session['room']][1] == 'roncheck':
        if choice in ('Y','N'):
            if choice == 'Y':
                room_dict[session['room']][0].kyoku.current_player.ron_input(choice)
                #Game ends here so should run some sort of function to record score and start new kyoku
            else:
                room_dict[session['room']][0].kyoku.after_player_ron_check()
                cycle_to_human()
        else:
            emit('gameupdate',{'msg':'不適切な入力がありました。'})
    #condition for turn after kan draw
    elif room_dict[session['room']][1] == 'kan_yesno':
        if choice in ('Y','N'):
            if choice == 'Y':
                room_dict[session['room']][0].kyoku.current_player.kan_user_input()
            else:
                room_dict[session['room']][0].kyoku.current_player.tenpai_check()
                room_dict[session['room']][0].kyoku.pon_kan_chi_check_sutehai = self.current_player.kawa[-1]
                room_dict[session['room']][0].kyoku.after_player_kan()
                cycle_to_human()
        else:
            emit('gameupdate',{'msg':'不適切な入力がありました。'})

    #accept user input to pon or not
    elif room_dict[session['room']][1] == 'pon_yesno':
        if choice in ('Y','N'):
            if choice == 'Y':
                #run sutehai func but redirect to 'pon_sutehai'
                room_dict[session['room']][0].kyoku.current_player.tehai.append(room_dict[session['room']][0].kyoku.pon_kan_chi_check_sutehai)
                room_dict[session['room']][0].kyoku.board_gui(False,True)
                emit('gameupdate',{'msg':f'{self.name}、捨て牌を入力してください。'})
                room_dict[session['room']][1] = 'pon_sutehai'

            else:
                room_dict[session['room']][0].kyoku.after_player_pon()
                cycle_to_human()
        else:
            emit('gameupdate',{'msg':'不適切な入力がありました。'})
    #accept user sutehai choice after chi
    elif room_dict[session['room']][1] == 'pon_sutehai':
        if choice.isdigit():
            #check to make sure input is in valid range
            if choice < len(room_dict[session['room']][0].kyoku.current_player.can_sutehai):
                room_dict[session['room']][0].kyoku.current_player.pon_user_input(choice)
                room_dict[session['room']][0].kyoku.after_player_chi()
                cycle_to_human()
        else:
            emit('gameupdate',{'msg':'不適切な入力がありました。'})
    #check if user will chi
    elif room_dict[session['room']][1] == 'chi_yesno':
        if choice in ('Y','N'):
            if choice == 'Y':
                #add sutehai to tehai and redirect to 'chi_sutehai'
                room_dict[session['room']][0].kyoku.current_player.tehai.append(room_dict[session['room']][0].kyoku.pon_kan_chi_check_sutehai)
                room_dict[session['room']][0].kyoku.board_gui(False,True)
                emit('gameupdate',{'msg':f'{self.name}、捨て牌を入力してください。'})
                room_dict[session['room']][1] = 'chi_sutehai'

            else:
                room_dict[session['room']][0].kyoku.after_player_chi()
                cycle_to_human()
        else:
            emit('gameupdate',{'msg':'不適切な入力がありました。'})
    #accept user sutehai choice after chi
    elif room_dict[session['room']][1] == 'chi_sutehai':
        if choice.isdigit():
            #check to make sure input is in valid range
            if choice < len(room_dict[session['room']][0].kyoku.current_player.can_sutehai):
                room_dict[session['room']][0].kyoku.current_player.chi_user_input(choice)
                room_dict[session['room']][0].kyoku.after_player_chi()
                cycle_to_human()
        else:
            emit('gameupdate',{'msg':'不適切な入力がありました。'})

    print(room_dict[session['room']][0].kyoku.current_player.name)
