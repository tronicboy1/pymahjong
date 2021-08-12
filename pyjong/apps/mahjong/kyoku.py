import random
from PIL import Image,ImageDraw,ImageFont
import time
import os
from pyjong.apps.mahjong.yama import Yama
from pyjong.apps.socketioapps.mahjongsocketio import room_dict
from pyjong import socketio

from flask_socketio import emit
from flask import session
import io



class Kyoku():

    def __init__(self,player1,player2,player3,player4,bakaze=0,oya=0):


        self.player1 = player1
        self.player2 = player2
        self.player3 = player3
        self.player4 = player4
        self.player_dict = {0:self.player1,1:self.player2,2:self.player3,3:self.player4}

        basedir = os.path.abspath(os.path.dirname(__file__))
        basedir = basedir + '/static/'
        self.bakaze = {0:Image.open(basedir+'ton.jpg'),1:Image.open(basedir+'nan.jpg'),2:Image.open(basedir+'sha.jpg'),3:Image.open(basedir+'pe.jpg')}[bakaze] #{0:ton,1:nan,2:sha,3:pe}
        if oya == 3:
            self.turn = 0
        else:
            self.turn = oya + 1
        self.oya = self.player_dict[oya]
        self.current_player = self.oya
        self.yama = Yama()
        self.first_yama = None
        self.wanpai = [[],[]]
        self.dora = []
        self.uradora = []
        self.current_yama = 0
        self.hai_remaining = 0
        self.kyoku_on = True #use this to end kyoku when winner is declared
        self.winner = None
        self.board_pic = Image.new('RGB',(1000,600),(31,61,12))
        self.board_pic.paste(Image.new('RGB',(150,150),(148,107,69)),(425,225))
        self.senbou = Image.open(basedir+'senbou.jpeg').reduce(3)
        self.riichi_turn_count = 0
        self.turn_count = 0
        self.ponkanchi_start_player = 0
        self.possible_chankan = False
        self.possible_rinshan = False

        self.board_pic.paste(self.bakaze.resize((50,50)),(475,275))
        #add jikaze hai to board
        jikaze_coord = {0:(480,330),1:(530,280),2:(480,230),3:(430,280)}
        rotation = {0:0,1:90,2:180,3:270}
        path = {0:'ton_jikaze.jpg',1:'nan_jikaze.jpg',2:'sha_jikaze.jpg',3:'pe_jikaze.jpg'}
        haichi_dic = {0:(0,1,2,3),1:(1,2,3,0),2:(2,3,0,1),3:(3,0,1,2)}
        haichi = haichi_dic[oya]
        for i,player in enumerate(haichi):
            bg = Image.new('RGB',(110,110),(255,255,255))
            img = Image.open(basedir+path[i])
            bg.paste(img,(5,5))
            img = bg.rotate(rotation[player],expand=True)
            self.board_pic.paste(img.resize((40,40)),jikaze_coord[player])
            self.player_dict[player].jikaze = i


    def next_player(self):
        if self.turn == 3:
            self.turn = 0
            self.current_player = self.player_dict[3]
        else:
            self.current_player = self.player_dict[self.turn]
            self.turn += 1


    def board_gui(self,player_turn=False,clear_mochihai=False): #add feature to rotate pic for player2 in future
        def send_tehai(player_id=1):
            self.current_player.refresh_can_sutehai_list()
            byte_arr = io.BytesIO()
            self.current_player.can_sutehai_pic_gen().save(byte_arr,format='jpeg')
            byte_arr = byte_arr.getvalue()
            if player_id == 1:
                emit('p1-tehaiimg',{'img':byte_arr},broadcast=True,namespace='/main/game',room=session['room'])
            if player_id == 2:
                emit('p2-tehaiimg',{'img':byte_arr},broadcast=True,namespace='/main/game',room=session['room'])

        def send_mochihai(player_id=1):
            img = self.current_player.mochihai.pic
            background = Image.new('RGB',(70,110),(31,61,12))
            background.paste(img,(5,5),img)

            result = background.rotate(90,expand=True)
            result = result.resize((55,35))

            byte_arr = io.BytesIO()
            result.save(byte_arr,format='jpeg')
            byte_arr = byte_arr.getvalue()
            emit(f'p{player_id}-mochihai',{'img':byte_arr},broadcast=True,namespace='/main/game',room=session['room'])

        def send_board(player_id=1):
            if player_id == 1:
                byte_arr = io.BytesIO()
                self.board_pic.save(byte_arr,format='jpeg')
                byte_arr = byte_arr.getvalue()
                emit('p1-board_gui',{'img':byte_arr},broadcast=True,namespace='/main/game',room=session['room'])


                #player 2 gui Emit
            elif player_id == 2:
                byte_arr = io.BytesIO()
                rotated_board = self.board_pic.rotate(180)
                rotated_board.save(byte_arr,format='jpeg')
                byte_arr = byte_arr.getvalue()
                emit('p2-guiimg',{'img':byte_arr},broadcast=True,namespace='/main/game',room=session['room'])


        def kawa_update():
            #player 1 kawa and kanchipon
            self.board_pic.paste(self.player1.kawa_pic_gen().resize((180,200)),(420,390))
            try:
                self.board_pic.paste(self.player1.kanchipon_pic_gen(),(10,540))
            except:
                pass
            if self.player1.is_riichi:
                self.board_pic.paste(self.senbou,(450,350))

            #Player2
            self.board_pic.paste(self.player2.kawa_pic_gen().resize((180,200)).rotate(90,expand=True),(790,200))
            try:
                self.board_pic.paste(self.player2.kanchipon_pic_gen().rotate(90,expand=True),(890,450))
            except:
                pass
            if self.player2.is_riichi:
                self.board_pic.paste(self.senbou.rotate(90,expand=True),(750,270))

            #player3
            self.board_pic.paste(self.player3.kawa_pic_gen().resize((180,200)).rotate(180,expand=True),(420,10))
            try:
                self.board_pic.paste(self.player3.kanchipon_pic_gen().rotate(180,expand=True),(900,10))
            except:
                pass
            if self.player3.is_riichi:
                self.board_pic.paste(self.senbou.rotate(180,expand=True),(450,270))

            #player4
            self.board_pic.paste(self.player4.kawa_pic_gen().resize((180,200)).rotate(270,expand=True),(10,200))
            try:
                self.board_pic.paste(self.player4.kanchipon_pic_gen().rotate(270,expand=True),(10,100))
            except:
                pass
            if self.player4.is_riichi:
                self.board_pic.paste(self.senbou.rotate(270,expand=True),(340,270))


        #update kawa for all players
        kawa_update()

        if self.current_player == self.player1:
            send_tehai(player_id=1)
            send_board(player_id=1)
            send_board(player_id=2)
            try:
                #send mochihai if mochihai object is not None
                send_mochihai(player_id=1)
            except:
                pass

        elif self.current_player == self.player3 and self.player3.is_computer == False:
            send_tehai(player_id=2)
            send_board(player_id=2)
            send_board(player_id=1)
            try:
                send_mochihai(player_id=2)
            except:
                pass
        #send new board pic to players
        else:
            send_board(player_id=2)
            send_board(player_id=1)
            #update kawa pics




    def refresh_hai_remaining(self):
        self.hai_remaining = self.yama.yama_hai_count()

    def yama_manager(self,hai_num=1):
        if self.yama.yama_hai_count() == 0 or hai_num > self.yama.yama_hai_count():
            raise ValueError('Not enough hai in all_yama')
        else:
            hai_to_append = []

            while len(hai_to_append) < hai_num:
                #move current yama count to ton (0) if no hai in pe (3) yama
                if self.current_yama == 3 and len(self.yama.all_yama[3][0]+self.yama.all_yama[3][1]) == 0:
                    self.current_yama = 0
                elif len(self.yama.all_yama[self.current_yama][0]+self.yama.all_yama[self.current_yama][1]) == 0:
                    self.current_yama += 1

                #take from top if top greater than equal to bottom
                else:
                    if len(self.yama.all_yama[self.current_yama][0])>=len(self.yama.all_yama[self.current_yama][1]):
                        hai_to_append.append(self.yama.all_yama[self.current_yama][0].pop(-1))
                    else:
                        hai_to_append.append(self.yama.all_yama[self.current_yama][1].pop(-1))
            #update current hai remaining size
            self.refresh_hai_remaining()
            if len(hai_to_append) == 1:
                return hai_to_append[0]
            else:
                return hai_to_append

    #have the oya roll dice to decide which yama to take from
    def saikoro_furi(self):
        saikoro_result = random.randint(1,6)
        emit('gameupdate',{'msg':f'親の{self.current_player.name}がサイコロを振りました。\n{saikoro_result}が出ました！'},room=session['room'])
        return saikoro_result


    def tehai_tori(self):
        saikoro_result = self.saikoro_furi()

        #move the current yama around the amount of times the saikoro says
        for i in range(0,saikoro_result+1):
            if self.current_yama == 3:
                self.current_yama = 0
            else:
                self.current_yama += 1

        #pop the first 7 top and bottom hai into wanpai
        while len(self.wanpai[0]) != 7: #top wanpai
            self.wanpai[0].append(self.yama.all_yama[self.current_yama][0].pop(0))
        while len(self.wanpai[1]) != 7: #bottom wanpai
            self.wanpai[1].append(self.yama.all_yama[self.current_yama][1].pop(0))

        #have each player draw 4 hai at a time until all players have 12 hai
        while (len(self.player1.tehai)+len(self.player2.tehai)+len(self.player3.tehai)+len(self.player4.tehai))< (12*4):
            self.current_player.draw_hai(self.yama_manager(hai_num=4))
            self.next_player()
        #have each player draw final hai
        i = 0
        while i < 4:
            self.current_player.draw_hai(self.yama_manager(hai_num=1))
            self.next_player()
            i += 1
        #append last hai to oya's mochihai
        self.current_player.mochihai = self.yama_manager(hai_num=1)

    def new_dora(self):
        try:
            self.dora.append(self.wanpai[0].pop(0))
            self.uradora.append(self.wanpai[1].pop(0))
            self.board_pic.paste(self.dora[len(self.dora)-1].pic,(((len(self.dora)-1)*60),0))
        except:
            pass

    def kyoku_start(self):
        #have players take their hai
        self.tehai_tori()
        #set the first dora and uradora
        self.new_dora()
        #have oya go first
        self.current_player.tenpai_check()
        if self.current_player.is_computer == False:
            self.board_gui(player_turn=True)
            if self.current_player.mochihai in self.current_player.can_kan_hai:
                #break here to wait for user input
                emit('gameupdate',{'msg':'持ち牌をカンしますか？（YもしくはN)'},room=session['room'])
                #set room dict index1 value to type of next input
                room_dict[session['room']][1] = 'mochihai_kan_yesno'

            if self.current_player.mochihai in self.current_player.machihai:
                self.current_player.ron(self.current_player.mochihai)
            if self.kyoku_on == True:
                #break here to wait for user input
                emit('gameupdate',{'msg':'持ち牌を手牌に入れますか？（YもしくはN)','type':'yesno'},room=session['room'])
                #set room dict index1 value to type of next input
                room_dict[session['room']][1] = 'kyokustart_yesno'

        elif self.current_player.is_computer == True:
            self.current_player.swap_hai()
            self.current_player.tenpai_check()
            self.board_gui()
            socketio.sleep(1)
            sutehai = self.current_player.kawa[-1]
            #set key to 'cycle' before pon kan chi check, will be changed to other key if player action is necesary
            room_dict[session['room']][1] = 'cycle'
            self.kanchipon_with_player_change(sutehai)

            self.turn_count += 1

        #start kyoku loop:
        # while self.kyoku_on == True and self.hai_remaining > 0:
        #     self.player_turn()
    def after_mochihai_kan(self):
        emit('gameupdate',{'msg':f'{self.current_player.mochihai}をカンしました！'},room=session['room'])


        self.kan_hai.append(self.current_player.mochihai)
        self.current_player.mochihai = None
        self.tenpai_check(not_turn=True)
        self.current_player.mochihai = self.yama_manager()
        self.current_player.tenpai_check(not_turn=True)
        if self.current_player.mochihai in self.current_player.machihai:
            self.possible_rinshan = True
            self.current_player.ron(self.current_player.mochihai,is_ron=False)
        else:
            self.player_turn()
            self.next_player()



    def kyoku_start_non_computer(self,choice):
        if choice == 'Y':
            self.current_player.tehai.append(self.current_player.mochihai)
            self.current_player.mochihai = None
            self.current_player.tehai.sort()
            self.board_gui(True,clear_mochihai=True)
            ####Sutehai func here
            self.current_player.sutehai()
        else:
            self.current_player.kawa.append(self.current_player.mochihai)
            self.current_player.mochihai = None
            self.board_gui(clear_mochihai=True)
            sutehai = self.current_player.kawa[-1]
            #set key to 'cycle' before pon kan chi check, will be changed to other key if player action is necesary
            room_dict[session['room']][1] = 'cycle'
            self.start_pon_kan_chi(sutehai)

            #do not go to next player unless in 'cycle', stop for user input
            if room_dict[session['room']][1] == 'cycle' or room_dict[session['room']][1] == 'kan_cycle':
                self.next_player()
                self.next_player()
        self.turn_count += 1


    def new_mochihai(self):
        #check if game on and hai in yama at start and end
        if self.kyoku_on != True or self.hai_remaining == 0:
            return False

        if self.turn_count < 4:
            if self.current_player.first_round_kan():
                self.player_turn()
        self.current_player.mochihai = self.yama_manager()
        return True

    def kanchipon_with_player_change(self,sutehai):
        #only change player once if kanchipon action
        action = self.start_pon_kan_chi(sutehai)
        if action:
            self.kanchipon_with_player_change(self.current_player.kawa[-1])
        #do not go to next player unless in 'cycle', stop for user input
        elif room_dict[session['room']][1] == 'cycle' and self.kyoku_on:
            self.next_player()
            self.next_player()


    def player_turn(self):
        #run only if new mochihai is available

        if self.new_mochihai():
            self.current_player.tenpai_check(not_turn=True)
            if self.current_player.is_computer == False:
                self.board_gui(player_turn=True)
                if self.current_player.mochihai in self.current_player.machihai:
                    self.current_player.ron(self.current_player.mochihai)
                elif self.current_player.mochihai in self.current_player.can_kan_hai:
                    self.current_player.kan(self.current_player.mochihai)

                elif self.current_player.is_riichi == True:
                    self.current_player.is_ippatu = False
                    self.current_player.kawa.append(self.current_player.mochihai)
                    sutehai = self.current_player.kawa[-1]
                    self.current_player.mochihai = None
                    self.current_player.kawa_pic_gen()
                    #set key to 'cycle' before pon kan chi check, will be changed to other key if player action is necesary
                    room_dict[session['room']][1] = 'cycle'

                    self.board_gui(clear_mochihai=True)
                    self.kanchipon_with_player_change(sutehai)
                else:
                    emit('gameupdate',{'msg':f'{self.current_player.name}持ち牌を手牌に入れますか？（YもしくはN)'},room=session['room'])
                    #set room dict index1 value to type of next input
                    room_dict[session['room']][1] = 'kyoku_yesno'


            elif self.current_player.is_computer == True:
                if self.current_player.mochihai in self.current_player.machihai:
                    if self.current_player.ron(self.current_player.mochihai):
                        self.is_monzen = True
                    else:
                        pass
                elif self.current_player.is_riichi == True:
                    self.current_player.kawa.append(self.current_player.mochihai)
                    self.board_gui()
                    sutehai = self.current_player.kawa[-1]
                    emit('gameupdate',{'msg':f'{self.current_player.name}が{sutehai}を川に捨てました！'},room=session['room'])
                    self.current_player.mochihai = None
                    #set key to 'cycle' before pon kan chi check, will be changed to other key if player action is necesary
                    room_dict[session['room']][1] = 'cycle'
                    self.kanchipon_with_player_change(sutehai)
                else:
                    self.current_player.swap_hai()
                    self.current_player.tenpai_check()
                    self.board_gui()
                    sutehai = self.current_player.kawa[-1]
                    #set key to 'cycle' before pon kan chi check, will be changed to other key if player action is necesary
                    room_dict[session['room']][1] = 'cycle'
                    self.kanchipon_with_player_change(sutehai)

            self.turn_count += 1
            #check if game on and hai in yama
            if self.kyoku_on != True or self.hai_remaining == 0:
                room_dict[session['room']][0].end_kyoku_check()

                room_dict[session['room']][0].kyoku_suu_change()

                room_dict[session['room']][0].kyoku_summary()

    def player_turn_input(self,choice):
        if choice == 'Y':
            self.current_player.tehai.append(self.current_player.mochihai)
            self.current_player.mochihai = None
            self.board_gui(False,True)
            #sutehai func here
            self.current_player.sutehai()

        else:
            self.current_player.kawa.append(self.current_player.mochihai)
            emit('gameupdate',{'msg':f'{self.current_player.name}が{self.current_player.mochihai}を川に捨てました！'},room=session['room'])
            self.current_player.mochihai = None
            self.board_gui(clear_mochihai=True)
            #set key to 'cycle' before pon kan chi check, will be changed to other key if player action is necesary
            room_dict[session['room']][1] = 'cycle'
            sutehai = self.current_player.kawa[-1]
            self.kanchipon_with_player_change(sutehai)

        self.turn_count += 1

    def after_player_sutehai(self):
        self.current_player.tenpai_check()
        sutehai = self.current_player.kawa[-1]
        #set key to 'cycle' before pon kan chi check, will be changed to other key if player action is necesary
        if room_dict[session['room']][1] != 'riichi_yesno':
            room_dict[session['room']][1] = 'cycle'
            self.kanchipon_with_player_change(sutehai)

    def after_tenpai_check(self):
        sutehai = self.current_player.kawa[-1]
        #set key to 'cycle' before pon kan chi check, will be changed to other key if player action is necesary
        room_dict[session['room']][1] = 'cycle'
        self.kanchipon_with_player_change(sutehai)







    ########################################################
    ##########Pon Kan Chi Checker##########################
    # I split the pon kan chi check up into different parts so it can be resumed after user input is gathered
    ##########################################################

    #wraps pon_kan_chi_check to reset iteration value first time only
    def start_pon_kan_chi(self,sutehai):


        self.pon_kan_chi_check_sutehai = sutehai
        #use int function to deep copy turn count
        if self.turn == 0:
            self.ponkanchi_start_player = self.player4
        else:
            self.ponkanchi_start_player = self.player_dict[(self.turn-1)]
        #iteration count for pon kan chi check
        room_dict[session['room']][2] = 0

        return self.pon_kan_chi_check()


    def pon_kan_chi_check(self):
        #add key 'cycle' check to stop pon_kan_chi_check when user input is necessary
        #variable to stop change turn after
        while room_dict[session['room']][2] < 3 and room_dict[session['room']][1] == 'cycle':
            self.next_player()
            #add 1 to iteration key
            room_dict[session['room']][2] +=1
            if self.pon_kan_chi_check_sutehai in self.current_player.machihai:
                if self.current_player.ron(self.pon_kan_chi_check_sutehai,True):
                    break


            #check if the next player can chi previous player's sutehai
            if room_dict[session['room']][2] == 1:
                if self.pon_kan_chi_check_sutehai in self.current_player.can_chi_hai and self.current_player.is_riichi == False:
                    if self.current_player.chi(self.pon_kan_chi_check_sutehai):
                        #break if current user is not a computer to wait for input
                        if self.current_player.is_computer == False:
                            break
                        else:
                            room_dict[session['room']][1] = 'cycle'
                            return True

            #check for possible kan
            if self.pon_kan_chi_check_sutehai in self.current_player.can_kan_hai and self.current_player.is_riichi == False:
                if self.current_player.kan(self.pon_kan_chi_check_sutehai):
                    if self.current_player.is_computer == False:
                        break
                    else:
                        self.new_dora()
                        self.current_player.is_monzen = False
                        self.current_player.mochihai = self.wanpai[0].pop(0)
                        room_dict[session['room']][1] = 'kan_cycle'
                        self.kan_turn()
                        room_dict[session['room']][1] = 'cycle'
                        #use this variable to check for chankan in ron check following kan
                        self.possible_chankan = True
                        return True

                    #Will figure out an implementation of chankan check later
                    # n = 0 #chankan check
                    # while n<3:
                    #     self.next_player()
                    #     n += 1
                    #     if sutehai in self.current_player.machihai:
                    #         if self.current_player.ron(sutehai,True):
                    #             self.current_player.is_chankan = True
            #check for possible pon
            if self.pon_kan_chi_check_sutehai in self.current_player.can_pon_hai and self.current_player.is_riichi == False:
                if self.current_player.pon(self.pon_kan_chi_check_sutehai):
                    room_dict[session['room']][1] = 'cycle'
                    return True
                #break if current user is not a computer to wait for input
                if self.current_player.is_computer == False:
                    break


    def kan_turn(self):
        self.current_player.tenpai_check(not_turn=True)
        if self.current_player.is_computer == False:
            self.board_gui(player_turn=True)
            if self.current_player.mochihai in self.current_player.machihai:
                self.current_player.ron(self.current_player.mochihai)
            elif self.current_player.mochihai in self.current_player.can_kan_hai:
                self.current_player.kan(self.current_player.mochihai)

            elif self.current_player.is_riichi == True:
                self.current_player.is_ippatu = False
                self.current_player.kawa.append(self.current_player.mochihai)
                sutehai = self.current_player.kawa[-1]
                self.current_player.mochihai = None
                self.current_player.kawa_pic_gen()
                self.board_gui(clear_mochihai=True)

            else:
                emit('gameupdate',{'msg':f'{self.current_player.name}持ち牌を手牌に入れますか？（YもしくはN)'},room=session['room'])
                #set room dict index1 value to type of next input
                room_dict[session['room']][1] = 'kyoku_yesno'


        elif self.current_player.is_computer == True:
            if self.current_player.mochihai in self.current_player.machihai:
                if self.current_player.ron(self.current_player.mochihai):
                    self.is_monzen = True
                else:
                    pass
            elif self.current_player.is_riichi == True:
                self.current_player.kawa.append(self.current_player.mochihai)
                self.board_gui()
                sutehai = self.current_player.kawa[-1]
                self.current_player.mochihai = None

            else:
                self.current_player.swap_hai()
                self.current_player.tenpai_check()
                self.board_gui()
                sutehai = self.current_player.kawa[-1]


        self.turn_count += 1
