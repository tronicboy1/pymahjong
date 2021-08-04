import random
from PIL import Image,ImageDraw,ImageFont
import time
import os
from pyjong.apps.mahjong.yama import Yama
from pyjong.apps.socketioapps.mahjongsocketio import room_dict
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
        self.senbou = Image.open(basedir+'senbou.jpeg').reduce(3)
        self.riichi_turn_count = 0
        self.turn_count = 0
        self.ponkanchi_start_player = 0

        self.board_pic.paste(self.bakaze.resize((30,50)),(485,275))

    def next_player(self):
        if self.turn == 3:
            self.turn = 0
            self.current_player = self.player_dict[3]
        else:
            self.current_player = self.player_dict[self.turn]
            self.turn += 1
        print('next player executed',self.current_player.name)

    def board_gui(self,player_turn=False,clear_mochihai=False): #add feature to rotate pic for player2 in future
        def send_tehai():
            self.current_player.refresh_can_sutehai_list()
            byte_arr = io.BytesIO()
            self.current_player.can_sutehai_pic_gen().save(byte_arr,format='jpeg')
            byte_arr = byte_arr.getvalue()
            emit('tehaiimg',{'img':byte_arr},broadcast=True,namespace='/main/game')

        if player_turn: #only paste can sutehai if player turn
            ########FOR DEBUGGING
            # print('hai in tehai:',len(self.current_player.tehai))
            # self.current_player.refresh_can_sutehai_list()
            # for i,hai in enumerate(self.current_player.can_sutehai):
            #     print(i,hai)
            #     emit('gameupdate',{'msg':f'{i}:{hai}'})
            #
            # emit('gameupdate',{'msg':f"もち牌：{self.current_player.mochihai}"})
            ###################################
            #send image to tehai
            send_tehai()

            try:
                #send mochihai if mochihai object is not None
                self.board_pic.paste(self.current_player.mochihai.pic,(800,480))
            except:
                #send white slate if mochihai object is None
                pass

            #update kawa pics

         #paste new kawa after players finish
        if self.current_player == self.player1:

            self.board_pic.paste(self.current_player.kawa_pic_gen().resize((180,200)),(420,390))
            try:
                self.board_pic.paste(self.current_player.kanchipon_pic_gen(),(10,540))
            except:
                pass
            if self.current_player.is_riichi:
                self.board_pic.paste(self.senbou,(450,350))
        elif self.current_player == self.player2:
            self.board_pic.paste(self.current_player.kawa_pic_gen().resize((180,200)).rotate(90,expand=True),(790,200))
            try:
                self.board_pic.paste(self.current_player.kanchipon_pic_gen().rotate(90,expand=True),(890,450))
            except:
                pass
            if self.current_player.is_riichi:
                self.board_pic.paste(self.senbou.rotate(90,expand=True),(750,270))
        elif self.current_player == self.player3:

            self.board_pic.paste(self.current_player.kawa_pic_gen().resize((180,200)).rotate(180,expand=True),(420,10))
            try:
                self.board_pic.paste(self.current_player.kanchipon_pic_gen().rotate(180,expand=True),(900,10))
            except:
                pass
            if self.current_player.is_riichi:
                self.board_pic.paste(self.senbou.rotate(180,expand=True),(450,270))
        elif self.current_player == self.player4:

            self.board_pic.paste(self.current_player.kawa_pic_gen().resize((180,200)).rotate(270,expand=True),(10,200))
            try:
                self.board_pic.paste(self.current_player.kanchipon_pic_gen().rotate(270,expand=True),(10,65))
            except:
                pass
            if self.current_player.is_riichi:
                self.board_pic.paste(self.senbou.rotate(270,expand=True),(340,270))

        if clear_mochihai:
            self.board_pic.paste(Image.new('RGB',(60,100),(31,61,12)),(800,480))
            send_tehai()

        ####################################
        ####Emit board gui
        ##################################

        # file_name = os.path.join(os.path.abspath(os.path.dirname(__file__)),'static','gui',(session['room']+'.jpg'))
        # self.board_pic.resize((600,600))
        # self.board_pic.save(file_name)
        # with open(file_name,'rb') as f:
        #     gui_binary = f.read()
        #     emit('board_gui',{'img':gui_binary},broadcast=True,namespace='/main/game')
        #     f.close()
        byte_arr = io.BytesIO()
        self.board_pic.save(byte_arr,format='jpeg')
        byte_arr = byte_arr.getvalue()
        emit('board_gui',{'img':byte_arr},broadcast=True,namespace='/main/game')

        ##############################


    def simple_hai_displayer(self):
        emit('gameupdate',{'msg':f'{self.current_player.name}の手牌：'})
        self.current_player.can_sutehai_pic_gen()
        emit('gameupdate',{'msg':'持ち牌：'})
        return self.current_player.mochihai.pic.resize((300,300))

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
        emit('gameupdate',{'msg':f'親の{self.current_player.name}がサイコロを振りました。\n{saikoro_result}が出ました！'})
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
        self.dora.append(self.wanpai[0].pop(2))
        self.uradora.append(self.wanpai[1].pop(2))
        self.board_pic.paste(self.dora[len(self.dora)-1].pic,(((len(self.dora)-1)*30),0))

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
                emit('gameupdate',{'msg':'持ち牌をカンしますか？（YもしくはN)'})
                #set room dict index1 value to type of next input
                room_dict[session['room']][1] = 'mochihai_kan_yesno'

            if self.current_player.mochihai in self.current_player.machihai:
                self.current_player.ron(self.current_player.mochihai)
            if self.kyoku_on == True:
                #break here to wait for user input
                emit('gameupdate',{'msg':'持ち牌を手牌に入れますか？（YもしくはN)'})
                #set room dict index1 value to type of next input
                room_dict[session['room']][1] = 'kyokustart_yesno'

        elif self.current_player.is_computer == True:
            self.current_player.swap_hai()
            self.current_player.tenpai_check()
            self.board_gui()
            sutehai = self.current_player.kawa[-1]
            #set key to 'cycle' before pon kan chi check, will be changed to other key if player action is necesary
            room_dict[session['room']][1] = 'cycle'
            self.start_pon_kan_chi(sutehai)
            #do not go to next player unless in 'cycle', stop for user input
            if room_dict[session['room']][1] == 'cycle':
                self.next_player()

            self.turn_count += 1

        #start kyoku loop:
        # while self.kyoku_on == True and self.hai_remaining > 0:
        #     self.player_turn()
    def after_mochihai_kan(self):
        emit('gameupdate',{'msg':f'{self.current_player.mochihai}をカンしました！'})
        print(f'{self.current_player.mochihai}をカンしました！')
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



    def kyoku_start_non_computer(self,choice):
        if choice == 'Y':
            self.current_player.tehai.append(self.current_player.mochihai)
            self.current_player.mochihai = None
            self.current_player.tehai.sort()
            self.board_gui(True,clear_mochihai=True)
            ####Sutehai func here
            self.current_player.sutehai()
        else:
            # print('kyoku start N')
            self.current_player.kawa.append(self.current_player.mochihai)
            self.current_player.mochihai = None
            self.board_gui(clear_mochihai=True)
            sutehai = self.current_player.kawa[-1]
            self.start_pon_kan_chi(sutehai)
            #set key to 'cycle' before pon kan chi check, will be changed to other key if player action is necesary
            room_dict[session['room']][1] = 'cycle'
            #do not go to next player unless in 'cycle', stop for user input
            if room_dict[session['room']][1] == 'cycle':
                self.next_player()
        self.turn_count += 1



    def player_turn(self):
        print('player:',self.current_player.name)
        print('kawa len',len(self.current_player.kawa))
        if self.turn_count < 4:
            if self.current_player.first_round_kan():
                self.player_turn()
        self.current_player.mochihai = self.yama_manager()
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
                self.start_pon_kan_chi(sutehai)
                self.board_gui(clear_mochihai=True)
                #do not go to next player unless in 'cycle', stop for user input
                if room_dict[session['room']][1] == 'cycle':
                    self.next_player()
            else:
                emit('gameupdate',{'msg':'持ち牌を手牌に入れますか？（YもしくはN)'})
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
                #set key to 'cycle' before pon kan chi check, will be changed to other key if player action is necesary
                room_dict[session['room']][1] = 'cycle'
                self.start_pon_kan_chi(sutehai)
                #do not go to next player unless in 'cycle', stop for user input
                if room_dict[session['room']][1] == 'cycle':
                    self.next_player()
            else:
                self.current_player.swap_hai()
                self.current_player.tenpai_check()
                self.board_gui()
                sutehai = self.current_player.kawa[-1]
                #set key to 'cycle' before pon kan chi check, will be changed to other key if player action is necesary
                room_dict[session['room']][1] = 'cycle'
                self.start_pon_kan_chi(sutehai)
                #do not go to next player unless in 'cycle', stop for user input
                if room_dict[session['room']][1] == 'cycle':
                    self.next_player()

            self.turn_count += 1

    def player_turn_input(self,choice):
        if choice == 'Y':
            self.current_player.tehai.append(self.current_player.mochihai)
            self.current_player.mochihai = None
            self.board_gui(False,True)
            #sutehai func here
            self.current_player.sutehai()

        else:
            self.current_player.kawa.append(self.current_player.mochihai)
            emit('gameupdate',{'msg':f'{self.current_player.name}が{self.current_player.mochihai}を川に捨てました！'})
            self.current_player.mochihai = None
            self.board_gui(clear_mochihai=True)
            #set key to 'cycle' before pon kan chi check, will be changed to other key if player action is necesary
            room_dict[session['room']][1] = 'cycle'
            #do not go to next player unless in 'cycle', stop for user input
            if room_dict[session['room']][1] == 'cycle':
                self.next_player()

        self.turn_count += 1

    def after_player_sutehai(self):
        self.current_player.tenpai_check()
        sutehai = self.current_player.kawa[-1]
        #set key to 'cycle' before pon kan chi check, will be changed to other key if player action is necesary
        if room_dict[session['room']][1] != 'riichi_yesno':
            room_dict[session['room']][1] = 'cycle'
            self.start_pon_kan_chi(sutehai)
        #do not go to next player unless in 'cycle', stop for user input
        if room_dict[session['room']][1] == 'cycle':
            self.next_player()

    def after_tenpai_check(self):
        sutehai = self.current_player.kawa[-1]
        #set key to 'cycle' before pon kan chi check, will be changed to other key if player action is necesary
        room_dict[session['room']][1] = 'cycle'
        self.start_pon_kan_chi(sutehai)
        #do not go to next player unless in 'cycle', stop for user input
        if room_dict[session['room']][1] == 'cycle':
            self.next_player()







    ########################################################
    ##########Pon Kan Chi Checker##########################
    # I split the pon kan chi check up into different parts so it can be resumed after user input is gathered
    ##########################################################

    #wraps pon_kan_chi_check to reset iteration value first time only
    def start_pon_kan_chi(self,sutehai):
        print('start_pon_kan_chi')
        self.pon_kan_chi_check_sutehai = sutehai
        self.ponkanchi_start_player = int(self.turn)
        room_dict[session['room']][2] = 0
        self.pon_kan_chi_check()


    def pon_kan_chi_check(self):
        #add key 'cycle' check to stop pon_kan_chi_check when user input is necessary
        while room_dict[session['room']][2]<3 and room_dict[session['room']][1] == 'cycle':
            self.next_player()
            print('cycling pon kan chi check. player:',self.current_player.name)
            if self.pon_kan_chi_check_sutehai in self.current_player.machihai:
                if self.current_player.ron(self.pon_kan_chi_check_sutehai,True):
                    self.current_player = self.player_dict[start_player]
            #check if the next player can chi previous player's sutehai
            print('chi check')
            if room_dict[session['room']][2] == 0:
                if self.pon_kan_chi_check_sutehai in self.current_player.can_chi_hai and self.current_player.is_riichi == False:
                    self.current_player.chi(self.pon_kan_chi_check_sutehai)
                    #break if current user is not a computer to wait for input
                    if self.current_player.is_computer == False:
                        break
            #check for possible kan
            print('kan check')
            if self.pon_kan_chi_check_sutehai in self.current_player.can_kan_hai and self.current_player.is_riichi == False:
                if self.current_player.kan(self.pon_kan_chi_check_sutehai):
                    self.new_dora()
                    self.current_player.is_monzen = False
                    self.current_player.mochihai = self.wanpai[0].pop(0)
                    self.current_player.tenpai_check(not_turn=True)
                    self.player_turn()
                    break
                    #Will figure out an implementation of chankan check later
                    # n = 0 #chankan check
                    # while n<3:
                    #     self.next_player()
                    #     n += 1
                    #     if sutehai in self.current_player.machihai:
                    #         if self.current_player.ron(sutehai,True):
                    #             self.current_player.is_chankan = True
            #check for possible pon
            print('pon check')
            if self.pon_kan_chi_check_sutehai in self.current_player.can_pon_hai and self.current_player.is_riichi == False:
                self.current_player.pon(self.pon_kan_chi_check_sutehai)
                #break if current user is not a computer to wait for input
                if self.current_player.is_computer == False:
                    break

            #add 1 to iteration key
            room_dict[session['room']][2] +=1

        #set next player to go back to start
        # check if key was changed before changing player
        if room_dict[session['room']][1] == 'cycle':
            self.next_player()

    def after_player_chi(self):
        #check for possible kan
        if self.pon_kan_chi_check_sutehai in self.current_player.can_kan_hai and self.current_player.is_riichi == False:
            if self.current_player.kan(self.pon_kan_chi_check_sutehai):
                self.new_dora()
                self.current_player.is_monzen = False
                self.current_player.mochihai = self.wanpai[0].pop(0)
                self.current_player.tenpai_check(not_turn=True)
                self.player_turn()
                if self.current_player.is_computer == False:
                    self.board_gui(player_turn=True)
                    if self.current_player.mochihai in self.current_player.machihai:
                        if self.current_player.ron(self.current_player.mochihai):
                            self.current_player = self.player_dict[start_player]
                    else:
                        emit('gameupdate',{'msg':'持ち牌を手牌に入れますか？（YもしくはN)'})
                        #set room dict index1 value to type of next input
                        room_dict[session['room']][1] = 'kan_yesno'

                #Will figure out an implementation of chankan check later
                # n = 0 #chankan check
                # while n<3:
                #     self.next_player()
                #     n += 1
                #     if sutehai in self.current_player.machihai:
                #         if self.current_player.ron(sutehai,True):
                #             self.current_player.is_chankan = True
        #check for possible pon
        elif self.pon_kan_chi_check_sutehai in self.current_player.can_pon_hai and self.current_player.is_riichi == False:
            self.current_player.pon(self.pon_kan_chi_check_sutehai)
        room_dict[session['room']][2] +=1
        self.pon_kan_chi_check()

    def after_player_pon(self):
        room_dict[session['room']][2] +=1
        self.pon_kan_chi_check()

    def after_player_kan(self):
        if self.pon_kan_chi_check_sutehai in self.current_player.can_pon_hai and self.current_player.is_riichi == False:
            self.current_player.pon(self.pon_kan_chi_check_sutehai)
        room_dict[session['room']][2] +=1
        #run pon_kan_chi_check to finish check
        self.pon_kan_chi_check()

    def after_player_ron_check(self):
        if room_dict[session['room']][2] == 0: #check if the next player can chi previous player's sutehai
            if self.pon_kan_chi_check_sutehai in self.current_player.can_chi_hai and self.current_player.is_riichi == False:
                self.current_player.chi(self.pon_kan_chi_check_sutehai)
        #check for possible kan
        if self.pon_kan_chi_check_sutehai in self.current_player.can_kan_hai and self.current_player.is_riichi == False:
            if self.current_player.kan(self.pon_kan_chi_check_sutehai):
                self.new_dora()
                self.current_player.is_monzen = False
                self.current_player.mochihai = self.wanpai[0].pop(0)
                self.current_player.tenpai_check(not_turn=True)
                self.player_turn()
                if self.current_player.is_computer == False:
                    self.board_gui(player_turn=True)
                    if self.current_player.mochihai in self.current_player.machihai:
                        if self.current_player.ron(self.current_player.mochihai):
                            self.current_player = self.player_dict[start_player]
                    else:
                        emit('gameupdate',{'msg':'持ち牌を手牌に入れますか？（YもしくはN)'})
                        #set room dict index1 value to type of next input
                        room_dict[session['room']][1] = 'kan_yesno'


            #Will figure out an implementation of chankan check later
            # n = 0 #chankan check
            # while n<3:
            #     self.next_player()
            #     n += 1
            #     if sutehai in self.current_player.machihai:
            #         if self.current_player.ron(sutehai,True):
            #             self.current_player.is_chankan = True
            #check for possible pon
        elif sutehai in self.current_player.can_pon_hai and self.current_player.is_riichi == False:
            self.current_player.pon(sutehai)
        room_dict[session['room']][2] +=1
        #run pon_kan_chi_check to finish check
        self.pon_kan_chi_check()
