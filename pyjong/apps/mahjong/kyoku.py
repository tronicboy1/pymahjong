import random
from PIL import Image,ImageDraw,ImageFont
import time
import os
from pyjong.apps.mahjong.yama import Yama

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
        self.board_pic = Image.new('RGB',(600,600),(31,61,12))
        self.senbou = Image.open(basedir+'senbou.jpeg').reduce(3)
        self.riichi_turn_count = 0
        self.turn_count = 0

        self.board_pic.paste(self.bakaze.resize((30,30)),(285,285))

    def next_player(self):
        if self.turn == 3:
            self.turn = 0
            self.current_player = self.player_dict[3]
        else:
            self.current_player = self.player_dict[self.turn]
            self.turn += 1

    def board_gui(self,player_turn=False,clear_mochihai=False): #add feature to rotate pic for player2 in future
        clear_output() #clear previous output
        if player_turn: #only paste can sutehai if player turn
            try:
                self.board_pic.paste(self.current_player.can_sutehai_pic_gen(),(50,520))
            except:
                pass
            try:
                self.board_pic.paste(self.current_player.mochihai.pic,(500,520))
            except:
                pass

         #paste new kawa after players finish
        if self.current_player == self.player1:
            self.board_pic.paste(self.current_player.kawa_pic_gen().resize((135,150)),(233,360))
            try:
                self.board_pic.paste(self.current_player.kanchipon_pic_gen(),(10,470))
            except:
                pass
            if self.current_player.is_riichi:
                self.board_pic.paste(self.senbou,(250,340))
        elif self.current_player == self.player2:
            self.board_pic.paste(self.current_player.kawa_pic_gen().resize((135,150)).rotate(90,expand=True),(420,233))
            try:
                self.board_pic.paste(self.current_player.kanchipon_pic_gen().rotate(90,expand=True),(550,450))
            except:
                pass
            if self.current_player.is_riichi:
                self.board_pic.paste(self.senbou.rotate(90,expand=True),(400,250))
        elif self.current_player == self.player3:
            self.board_pic.paste(self.current_player.kawa_pic_gen().resize((135,150)).rotate(180,expand=True),(233,0))
            try:
                self.board_pic.paste(self.current_player.kanchipon_pic_gen().rotate(180,expand=True),(500,10))
            except:
                pass
            if self.current_player.is_riichi:
                self.board_pic.paste(self.senbou.rotate(180,expand=True),(250,170))
        elif self.current_player == self.player4:
            self.board_pic.paste(self.current_player.kawa_pic_gen().resize((135,150)).rotate(270,expand=True),(0,233))
            try:
                self.board_pic.paste(self.current_player.kanchipon_pic_gen().rotate(270,expand=True),(10,40))
            except:
                pass
            if self.current_player.is_riichi:
                self.board_pic.paste(self.senbou.rotate(270,expand=True),(170,250))

        if clear_mochihai:
            self.board_pic.paste(Image.new('RGB',(30,50),(31,61,12)),(500,520))
            self.current_player.refresh_can_sutehai_list()
            self.board_pic.paste(self.current_player.can_sutehai_pic_gen(),(50,520))

        self.board_pic.resize((300,300)).show()

    def simple_hai_displayer(self):
        print(f'{self.current_player.name}の手牌：')
        self.current_player.can_sutehai_pic_gen()
        print(f'持ち牌：')
        self.current_player.mochihai.pic.resize((300,300)).show()

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
        if self.current_player.is_computer == True:
            print(f'親の{self.current_player.name}がサイコロを振ります。')
            saikoro_result = random.randint(1,6)
            time.sleep(1)
            print(f'{saikoro_result}が出ました！')
            return saikoro_result
        else:
            input(f'親の{self.current_player.name}がサイコロを振ります。\nEnterキーを押して振ってください。')
            saikoro_result = random.randint(1,6)
            time.sleep(1)
            print(f'{saikoro_result}が出ました！')
            return saikoro_result

    def tehai_tori(self):
        saikoro_result = self.saikoro_furi()
        time.sleep(1)

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
                if self.current_player.mochihai_kan(self.current_player.mochihai):
                    self.current_player.mochihai = self.yama_manager()
                    self.current_player.tenpai_check(not_turn=True)
                    if self.current_player.mochihai in self.current_player.machihai:
                        if self.current_player.ron(self.current_player.mochihai,is_ron=False):
                            self.current_player.is_rinshan = True
            if self.current_player.mochihai in self.current_player.machihai:
                self.current_player.ron(self.current_player.mochihai)
            if self.kyoku_on == True:
                player_input = ''
                while player_input not in ('Y','N'):
                    player_input = input('持ち牌を手牌に入れますか？（YもしくはN)').upper()
                if player_input == 'Y':
                    self.current_player.swap_hai()
                    self.current_player.tehai.sort()
                    self.board_gui(True,clear_mochihai=True)
                    self.current_player.tenpai_check()
                    sutehai = self.current_player.kawa[-1]
                    self.pon_kan_chi_check(sutehai)
                    self.next_player()
                else:
                    self.current_player.kawa.append(self.current_player.mochihai)
                    self.current_player.mochihai = None
                    self.board_gui(clear_mochihai=True)
                    sutehai = self.current_player.kawa[-1]
                    self.pon_kan_chi_check(sutehai)
                    self.next_player()
        elif self.current_player.is_computer == True:
            self.current_player.swap_hai()
            self.current_player.tenpai_check()
            sutehai = self.current_player.kawa[-1]
            self.pon_kan_chi_check(sutehai)
            self.next_player()

        self.turn_count += 1

        #start kyoku loop:
        while self.kyoku_on == True and self.hai_remaining > 0:
            self.player_turn()

    def player_turn(self):
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
                if self.current_player.kan(self.current_player.mochihai):
                    self.player_turn()
            elif self.current_player.is_riichi == True:
                self.current_player.is_ippatu = False
                self.current_player.kawa.append(self.current_player.mochihai)
                sutehai = self.current_player.kawa[-1]
                self.current_player.mochihai = None
                self.current_player.kawa_pic_gen()
                self.pon_kan_chi_check(sutehai)
                self.board_gui(clear_mochihai=True)
                self.next_player()
            else:
                player_input = ''
                while player_input not in ('Y','N'):
                    player_input = input('持ち牌を手牌に入れますか？（YもしくはN)').upper()
                if player_input == 'Y':
                    self.current_player.swap_hai()
                    self.board_gui(False,True)
                    self.current_player.tenpai_check()
                    sutehai = self.current_player.kawa[-1]
                    self.pon_kan_chi_check(sutehai)
                    self.next_player()
                else:
                    self.current_player.kawa.append(self.current_player.mochihai)
                    self.current_player.mochihai = None
                    self.board_gui(clear_mochihai=True)
                    self.current_player.tenpai_check()
                    sutehai = self.current_player.kawa[-1]
                    self.pon_kan_chi_check(sutehai)
                    self.next_player()
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
                self.pon_kan_chi_check(sutehai)
                self.next_player()
            else:
                self.current_player.swap_hai()
                self.current_player.tenpai_check()
                sutehai = self.current_player.kawa[-1]
                self.pon_kan_chi_check(sutehai)
                self.next_player()

        self.turn_count += 1


    def pon_kan_chi_check(self,sutehai):
        i = 0
        start_player = int(self.turn)
        while i<3:
            self.next_player()
            if sutehai in self.current_player.machihai:
                if self.current_player.ron(sutehai,True):
                    self.current_player = self.player_dict[start_player]

            if i == 0: #check if the next player can chi previous player's sutehai
                if sutehai in self.current_player.can_chi_hai and self.current_player.is_riichi == False:
                    self.current_player.chi(sutehai)
            #check for possible kan
            if sutehai in self.current_player.can_kan_hai and self.current_player.is_riichi == False:
                if self.current_player.kan(sutehai):
                    self.new_dora()
                    self.current_player.is_monzen = False
                    self.current_player.mochihai = self.wanpai[0].pop(0)
                    self.current_player.tenpai_check(not_turn=True)
                    if self.current_player.is_computer == False:
                        self.board_gui(player_turn=True)
                        if self.current_player.mochihai in self.current_player.machihai:
                            if self.current_player.ron(self.current_player.mochihai):
                                self.current_player = self.player_dict[start_player]
                        player_input = ''
                        while player_input not in ('Y','N'):
                            player_input = input('持ち牌を手牌に入れますか？（YもしくはN)').upper()
                        if player_input == 'Y':
                            self.current_player.swap_hai()
                            self.board_gui(False,True)
                        else:
                            self.current_player.kawa.append(self.current_player.mochihai)
                            self.current_player.mochihai = None
                            self.board_gui(clear_mochihai=True)
                    self.current_player.tenpai_check()
                    sutehai = self.current_player.kawa[-1]
                    n = 0 #chankan check
                    while n<3:
                        self.next_player()
                        n += 1
                        if sutehai in self.current_player.machihai:
                            if self.current_player.ron(sutehai,True):
                                self.current_player.is_chankan = True
            #check for possible pon
            elif sutehai in self.current_player.can_pon_hai and self.current_player.is_riichi == False:
                self.current_player.pon(sutehai)
            i +=1
        #set next player to go back to start
        self.next_player()
