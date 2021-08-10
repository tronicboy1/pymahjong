from flask_socketio import join_room,leave_room,emit
from pyjong import socketio,room_dict,room_players,db
from flask_login import current_user
from pyjong.models import UserData,new_game_update
from flask import session,redirect,flash,url_for
from time import sleep




#room dict is used in Kyoku so import must be done after creation
from pyjong.apps.mahjong.yama import Yama
from pyjong.apps.mahjong.game import Game

#################################################
#DATABASE FUNCTIONS
#################################################

def add_game_results(game,players):
    global room_dict
    if players == 1:
        #search for first player
        username1 = room_dict[session['room']][0].player1.name
        result = UserData.query.filter_by(username=username1).first()
        #add kyoku wins to UserData
        result.kyoku_win_count += room_dict[session['room']][0].player1_kyokuwin_count
        #add game wins to UserData
        result.game_win_count += room_dict[session['room']][0].player1_gamewin_count
        #add points to user data
        result.points += (room_dict[session['room']][0].player1.balance - 30000)
        db.session.add(result)
        db.session.commit()
        print('game data added to db')
        result = UserData.query.filter_by(username=username1).first()


    elif players == 2:
        # first player
        username1 = room_dict[session['room']][0].player1.name
        result1 = UserData.query.filter_by(username=username1).first()
        result1.kyoku_win_count += room_dict[session['room']][0].player1_kyokuwin_count
        result1.game_win_count += room_dict[session['room']][0].player1_gamewin_count
        result1.points += (room_dict[session['room']][0].player1.balance - 30000)
        #second player
        #in the game object player invited to room is referred to as player 3
        username2 = room_dict[session['room']][0].player3.name
        result2 = UserData.query.filter_by(username=username2).first()
        result2.kyoku_win_count += room_dict[session['room']][0].player3_kyokuwin_count
        result2.game_win_count += room_dict[session['room']][0].player3_gamewin_count
        result2.points += (room_dict[session['room']][0].player3.balance - 30000)
        db.session.add_all([result1,result2])
        db.session.commit()
        flash(f'プレーヤーの情報が更新されました！',"alert-success")
        redirect(url_for('main.friends'))


#################################################
###MAHJONG FUNCTIONS
#################################################

def cycle_to_human():
    #changed to 'cycle' key so cycler stops whenever user input is necessary

    while room_dict[session['room']][1] == 'cycle':
        room_dict[session['room']][0].kyoku.player_turn()
        room_dict[session['room']][0].kyoku.board_gui()
        socketio.sleep(1.5)

def kanchiponron_no_input():
    room_dict[session['room']][1] = 'cycle'
    #check to see if there was an action and new pon kan chi check needs to be started
    if room_dict[session['room']][0].kyoku.pon_kan_chi_check():
        room_dict[session['room']][0].kyoku.kanchipon_with_player_change(room_dict[session['room']][0].kyoku.current_player.kawa[-1])
    else:
        room_dict[session['room']][0].kyoku.next_player()
        room_dict[session['room']][0].kyoku.next_player()
    cycle_to_human()





@socketio.on('start',namespace='/main/game')
def startgame():
    global room_dict
    if session['players'] == 1:
        new_game_update(text=f"{session['username']}がゲームを開始しました！")
        game = Game()
        room_dict[session['room']] = [game,'',0]
        room_dict[session['room']][0].create_players(players=1,player1_name=room_players[session['room']][0])
        room_dict[session['room']][0].kyoku.kyoku_start()
        cycle_to_human()
        #kyoku.game will set index 1 value of room dict to define what the next input will be
        #index2 will be used for iterations
    elif session['players'] == 2:
        emit('new-game',namespace='/main/game',room=session['room'])
        new_game_update(text=f"{room_players[session['room']][0]}と{room_players[session['room']][1]}が対戦を開始しました！")
        game = Game()
        room_dict[session['room']] = [game,'',0]
        room_dict[session['room']][0].create_players(players=2,player1_name=room_players[session['room']][0],player3_name=room_players[session['room']][1])
        room_dict[session['room']][0].kyoku.kyoku_start()
        cycle_to_human()



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
        if choice in ('Y','N'):
            if choice == 'Y':
                room_dict[session['room']][0].kyoku.kyoku_start_non_computer(choice)
            else:
                room_dict[session['room']][0].kyoku.kyoku_start_non_computer(choice)
                #'cycle' added to prevent false input and stop cycler for kan chi pon check
                room_dict[session['room']][1] = 'cycle'
                cycle_to_human()
        else:
            emit('gameupdate',{'msg':'不適切な入力がありました。'},namespace='/main/game')
    #condition for asking to get rid of a hai and accept mochihai
    elif room_dict[session['room']][1] == 'kyoku_yesno':
        if choice in ('Y','N'):
            if choice == 'Y':
                room_dict[session['room']][0].kyoku.player_turn_input(choice)
            else:
                room_dict[session['room']][0].kyoku.player_turn_input(choice)
                room_dict[session['room']][1] = 'cycle'
                socketio.sleep(1)
                cycle_to_human()
        else:
            emit('gameupdate',{'msg':'不適切な入力がありました。'},namespace='/main/game')
    #condition for asking which hai to throw into kawa
    elif room_dict[session['room']][1] == 'sutehai':
        if choice.isdigit():
            #convert choice to integer
            choice = int(choice)
            #check to make sure input is in valid range
            if choice < len(room_dict[session['room']][0].kyoku.current_player.can_sutehai):
                room_dict[session['room']][0].kyoku.current_player.sutehai_user_input(choice)
                room_dict[session['room']][0].kyoku.current_player.tenpai_check()
                room_dict[session['room']][0].kyoku.board_gui()
                socketio.sleep(1)

                #do nothing if riichi check is necessary
                if room_dict[session['room']][1] == 'riichi_yesno':
                    pass
                else:
                    room_dict[session['room']][0].kyoku.after_tenpai_check()
                    cycle_to_human()
        else:
            emit('gameupdate',{'msg':'不適切な入力がありました。'},namespace='/main/game')
    #condition for ron atama_check
    elif room_dict[session['room']][1] == 'roncheck':
        if choice in ('Y','N'):
            if choice == 'Y':
                room_dict[session['room']][0].kyoku.current_player.ron_input(choice)
                #kyoku ends here so run end kyoku shori
                room_dict[session['room']][0].end_kyoku_check()
                room_dict[session['room']][0].kyoku_suu_change()
                room_dict[session['room']][0].kyoku_summary()

            else:
                kanchiponron_no_input()
        else:
            emit('gameupdate',{'msg':'不適切な入力がありました。'},namespace='/main/game')
    #condition to staaart new kyoku
    elif room_dict[session['room']][1] == 'newkyoku_yesno':
            if choice in ('Y','N'):
                if choice == 'Y':
                    room_dict[session['room']][0].kyoku_summary_choice('Y')
                    room_dict[session['room']][0].kyoku_suu_change()
                    room_dict[session['room']][0].kyoku.kyoku_start()
                    cycle_to_human()
                else:
                    #handling for 1 player mode
                    if session['players'] == 1:
                        add_game_results(room_dict[session['room']][0],1)
                        flash("プレーヤー情報が更新されました！","alert-success")
                        return redirect(url_for('main.friends'))
                    #handling for 2 player mode
                    elif session['players'] == 2:
                        add_game_results(room_dict[session['room']][0],2)
                        flash("プレーヤー情報が更新されました！","alert-success")
                        return redirect(url_for('main.friends'))

                    #will add features to store game data to database here

            else:
                emit('gameupdate',{'msg':'不適切な入力がありました。'},namespace='/main/game')
    #condition for turn after kan draw
    elif room_dict[session['room']][1] == 'kan_yesno':
        if choice in ('Y','N'):
            if choice == 'Y':
                #remove pon hai from other player's kawa
                kan_hai = room_dict[session['room']][0].kyoku.ponkanchi_start_player.kawa.pop(-1)
                new_game_update(text=f"{session['username']}が{kan_hai}をカンしました！")
                room_dict[session['room']][0].kyoku.current_player.kan_user_input()
                #reset player to player at start of pon kan chi check
                room_dict[session['room']][0].kyoku.player_turn()

            else:
                kanchiponron_no_input()
        else:
            emit('gameupdate',{'msg':'不適切な入力がありました。'},namespace='/main/game')

    #accept user input to pon or not
    elif room_dict[session['room']][1] == 'pon_yesno':
        if choice in ('Y','N'):
            if choice == 'Y':
                #run sutehai func but redirect to 'pon_sutehai'
                room_dict[session['room']][0].kyoku.current_player.tehai.append(room_dict[session['room']][0].kyoku.pon_kan_chi_check_sutehai)
                #remove pon hai from other player's kawa
                room_dict[session['room']][0].kyoku.ponkanchi_start_player.kawa.pop(-1)
                room_dict[session['room']][0].kyoku.current_player.is_monzen = False
                room_dict[session['room']][0].kyoku.current_player.tenpai_check(not_turn=True)
                for mentu in room_dict[session['room']][0].kyoku.current_player.mentuhai: #add pon mentu into pon hai
                    if room_dict[session['room']][0].kyoku.pon_kan_chi_check_sutehai in mentu:
                        room_dict[session['room']][0].kyoku.current_player.pon_hai.extend(mentu)
                room_dict[session['room']][0].kyoku.board_gui(False,True)
                emit('gameupdate',{'msg':'{}、捨て牌を入力してください。'.format(room_dict[session['room']][0].kyoku.current_player.name)},namespace='/main/game')
                room_dict[session['room']][1] = 'pon_sutehai'
                print('pon choice yes')

            else:
                kanchiponron_no_input()
        else:
            emit('gameupdate',{'msg':'不適切な入力がありました。'},namespace='/main/game')
    #accept user sutehai choice after chi
    elif room_dict[session['room']][1] == 'pon_sutehai':
        if choice.isdigit():
            #convert choice to integer
            choice = int(choice)
            #check to make sure input is in valid range
            if choice < len(room_dict[session['room']][0].kyoku.current_player.can_sutehai):
                room_dict[session['room']][0].kyoku.current_player.pon_user_input(choice)
                #change to next player
                room_dict[session['room']][0].kyoku.next_player()
                room_dict[session['room']][1] = 'cycle'
                cycle_to_human()
        else:
            emit('gameupdate',{'msg':'不適切な入力がありました。'},namespace='/main/game')
    #check if user will chi
    elif room_dict[session['room']][1] == 'chi_yesno':
        if choice in ('Y','N'):
            if choice == 'Y':
                #add sutehai to tehai and redirect to 'chi_sutehai'
                room_dict[session['room']][0].kyoku.current_player.tehai.append(room_dict[session['room']][0].kyoku.pon_kan_chi_check_sutehai)
                #add chihai to player chihai list
                room_dict[session['room']][0].kyoku.current_player.tenpai_check(not_turn=True)
                for mentu in room_dict[session['room']][0].kyoku.current_player.mentuhai: #add chi mentu into chi hai
                    if room_dict[session['room']][0].kyoku.pon_kan_chi_check_sutehai in mentu:
                        room_dict[session['room']][0].kyoku.current_player.chi_hai.extend(mentu)

                #remove hai from other player's kawa
                room_dict[session['room']][0].kyoku.ponkanchi_start_player.kawa.pop(-1)
                room_dict[session['room']][0].kyoku.board_gui(False,True)
                emit('gameupdate',{'msg':'{}、捨て牌を入力してください。'.format(room_dict[session['room']][0].kyoku.current_player.name)},namespace='/main/game')
                room_dict[session['room']][1] = 'chi_sutehai'

            else:
                #check to see if sutehai is also in players can pon hai
                if room_dict[session['room']][0].kyoku.pon_kan_chi_check_sutehai in room_dict[session['room']][0].kyoku.current_player.can_pon_hai:
                    self.current_player.pon(room_dict[session['room']][0].kyoku.pon_kan_chi_check_sutehai)
                else:
                    kanchiponron_no_input()
        else:
            emit('gameupdate',{'msg':'不適切な入力がありました。'},namespace='/main/game')
    #accept user sutehai choice after chi
    elif room_dict[session['room']][1] == 'chi_sutehai':
        if choice.isdigit():
            choice = int(choice)
            #check to make sure input is in valid range
            if choice < len(room_dict[session['room']][0].kyoku.current_player.can_sutehai):
                room_dict[session['room']][0].kyoku.current_player.chi_user_input(choice)
                #reset player to player at start of pon kan chi check
                room_dict[session['room']][0].kyoku.current_player = room_dict[session['room']][0].kyoku.ponkanchi_start_player
                #change to next player
                room_dict[session['room']][0].kyoku.next_player()
                room_dict[session['room']][1] = 'cycle'
                cycle_to_human()
        else:
            emit('gameupdate',{'msg':'不適切な入力がありました。'},namespace='/main/game')
    #user input for riichi
    elif room_dict[session['room']][1] == 'riichi_yesno':
        print('riichi input:',choice)
        if choice in ('Y','N'):
            if choice == 'Y':
                new_game_update(text=f"{session['username']}がリーチしました！")
                room_dict[session['room']][0].kyoku.current_player.player_riichi_input()
                room_dict[session['room']][0].kyoku.after_tenpai_check()
                cycle_to_human()
            else:
                room_dict[session['room']][0].kyoku.after_tenpai_check()
                if room_dict[session['room']][1] == 'cycle':
                    cycle_to_human()
        else:
            emit('gameupdate',{'msg':'不適切な入力がありました。'},namespace='/main/game')

    #user input for mochihai kan
    elif room_dict[session['room']][1] == 'mochihai_kan_yesno':
        if choice in ('Y','N'):
            if choice == 'Y':
                room_dict[session['room']][0].kyoku.after_mochihai_kan()
            else:
                cycle_to_human()
        else:
            emit('gameupdate',{'msg':'不適切な入力がありました。'},namespace='/main/game')
