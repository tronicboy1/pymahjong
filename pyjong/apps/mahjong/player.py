from pyjong.apps.mahjong.yama import Hai
from pyjong.apps.socketioapps.mahjongsocketio import room_dict
from PIL import Image,ImageDraw,ImageFont
from flask import session
from flask_socketio import emit
import copy
import os
import random
import io


class Player():

    def __init__(self,name,is_computer=True):
        self.name = name
        self.balance = 30000
        self.is_computer = is_computer
        self.tehai = []
        self.can_sutehai = []
        self.mochihai = None
        self.kawa = []
        self.chi_hai = []
        self.pon_hai = []
        self.kan_hai = []
        self.mentuhai = []
        self.is_tenpatteru = False
        self.is_riichi = False
        self.machihai = []
        self.can_kan_hai = []
        self.can_chi_hai = []
        self.can_pon_hai = []
        self.atama_hai = []
        self.non_mentu_hai = []
        self.is_tumo_agari = False
        self.is_rinshan = False
        self.double_riichi = False
        self.is_chankan = False
        self.is_monzen = True
        self.is_ippatu = True #to be set to false if player riichi and goes around one turn
        self.can_ron = False
        self.is_ron = False
        self.ron_hai = None
        self.possible_rinshan = False

    def clear(self):
        self.tehai.clear()
        self.can_sutehai.clear()
        self.mochihai = None
        self.kawa.clear()
        self.chi_hai.clear()
        self.pon_hai.clear()
        self.kan_hai.clear()
        self.mentuhai.clear()
        self.is_tenpatteru = False
        self.is_riichi = False
        self.machihai.clear()
        self.can_kan_hai.clear()
        self.can_chi_hai.clear()
        self.can_pon_hai.clear()
        self.atama_hai.clear()
        self.non_mentu_hai.clear()
        self.is_tumo_agari = False
        self.is_rinshan = False
        self.double_riichi = False
        self.is_chankan = False
        self.is_monzen = True
        self.is_ippatu = True
        self.can_ron = False
        self.is_ron = False
        self.ron_hai = None

    def sort_tehai(self):
        self.tehai.sort()

    def add_funds(self,amount):
        self.balance += amount
        emit('gameupdate',{'msg':f'{self.name}が{amount}ポイントを懐に入れました！\nポイント合計：{self.balance}'})
        print(f'{self.name}が{amount}ポイントを懐に入れました！\nポイント合計：{self.balance}')

    def remove_funds(self,amount):
        self.balance -= amount
        emit('gameupdate',{'msg':f'{self.name}の懐から{amount}ポイントがなくなった！\nポイント合計：{self.balance}'})
        print(f'{self.name}の懐から{amount}ポイントがなくなった！\nポイント合計：{self.balance}')

    def can_sutehai_pic_gen(self):
        self.refresh_can_sutehai_list()
        #adjust size to be same as hai pic
        can_sutehai_pic = Image.new('RGB',(850,130),(31,61,12)) #make green BG
        draw = ImageDraw.Draw(can_sutehai_pic) #create editable
        basedir = os.path.abspath(os.path.dirname(__file__))
        font = ImageFont.truetype(basedir+'/static/'+'Arial.ttf',20) #create font for list marking
        for n,x in enumerate([x*60 for x in range(0,14)]): #length of 14 at max
            draw.text((x+20,106),'{}'.format(n),(255,255,255),font=font)#text at bottom of image
        i = 0
        for x in [x*60 for x in range(0,14)]:#paste all the hai that are not pon chi kan
            if i > len(self.can_sutehai)-1:
                break
            else:
                can_sutehai_pic.paste(self.can_sutehai[i].pic,(x+5,5))
                i += 1

        return can_sutehai_pic.resize((int(can_sutehai_pic.size[0]*.75),int(can_sutehai_pic.size[1]*.75))) #display kawa

    def kanchipon_list_gen(self):
        kanchipon_list = []
        for hai in self.kan_hai:
            kanchipon_list.append(hai)
            kanchipon_list.append(hai)
            kanchipon_list.append(hai)
            kanchipon_list.append(hai)
        for hai in self.chi_hai:
            kanchipon_list.append(hai)
        for hai in self.pon_hai:
            kanchipon_list.append(hai)
        return kanchipon_list

    def kanchipon_pic_gen(self):
        kanchipon_list = self.kanchipon_list_gen()
        if len(kanchipon_list) > 0:

            im = Image.new('RGB',(len(kanchipon_list*30),50),(31,61,12))
            i=0
            for x in (x*30 for x in range(0,len(kanchipon_list))):
                if i > len(kanchipon_list)-1:
                    break
                else:
                    im.paste(kanchipon_list[i].pic.resize((30,50)),(x,0))
                    i += 1
            return im.resize((int(im.size[0]*.75),int(im.size[1]*.75)))

        else:
            pass

    def kawa_pic_gen(self):
        #make blank white backgroudn
        kawa_pic = Image.new('RGB',(180,200),(31,61,12))
        i = 0
        for y in (0,50,100,150): #4 rows in kawa
            for x in (0,30,60,90,120,150): #6 hai per row
                if i > (len(self.kawa)-1): #stop printing hai when at end of kawa length
                    break
                else:
                    paste_pic = self.kawa[i].pic
                    paste_pic = paste_pic.resize((30,50))
                    kawa_pic.paste(paste_pic,(x,y))
                    i += 1
        return kawa_pic

    def swap_hai(self):
        self.sutehai()
        self.tehai.append(self.mochihai)
        self.mochihai = None


    def draw_hai(self,new_hai):
        if type(new_hai) == list:
            self.tehai.extend(new_hai)
        else:
            self.tehai.append(new_hai)
        self.sort_tehai()

    def refresh_can_sutehai_list(self):
        self.can_sutehai = []
        for hai in self.tehai:
            if hai not in self.chi_hai and hai not in self.kan_hai and hai not in self.pon_hai:
                self.can_sutehai.append(hai)
        self.can_sutehai.sort()

    def sutehai(self,choice=None):
        #refresh can sutehai list
        self.refresh_can_sutehai_list()
        if self.is_computer == False:
            self.can_sutehai_pic_gen()
            input_range = ['{}'.format(x) for x in range(0,len(self.can_sutehai))]
            #ask user for sutehai no and pass off to sutehai_user_input
            emit('gameupdate',{'msg':f'{self.name}、捨て牌を入力してください。'})
            room_dict[session['room']][1] = 'sutehai'

        else:
            #to be used in func below to set pairs
            sutehai = None
            #try to have the computer be smart about only throwing non mentu hai into the kawa
            non_mentu_hai_count = {hai:self.non_mentu_hai.count(hai) for hai in self.non_mentu_hai}
            if 1 in non_mentu_hai_count.values():
                for hai,count in non_mentu_hai_count.items():
                    if count == 1 and hai in self.can_sutehai:
                        sutehai = hai
                        break
                if sutehai == None: #set sutehai if no single hai available
                    sutehai = self.can_sutehai[0]
            else:
                sutehai = self.can_sutehai[0]
            self.kawa.append(sutehai)
            self.tehai.remove(sutehai)
            self.kawa_pic_gen()
            emit('gameupdate',{'msg':f'{self.name}が{sutehai}を川に捨てました！'})
            print(f'{self.name} threw {sutehai} to kawa')

    def sutehai_user_input(self,choice):
        sutehai_location = (int(choice))
        sutehai = self.can_sutehai[sutehai_location]
        self.kawa.append(sutehai)
        self.tehai.remove(sutehai)
        self.kawa_pic_gen()
        emit('gameupdate',{'msg':f'{self.name}が{sutehai}を川に捨てました！'})
        print(f'{sutehai} thrown into kawa')





    def ron(self,ron_hai,is_ron=False):
        if self.is_ron == False:
            text = ('ツモりますか','をツモった！')
        else:
            text = ('ロンしますか','をロンした！')
        #must add differences for ron and tumo
        self.can_ron = False
        self.is_ron = is_ron
        self.ron_hai = ron_hai

        if len(self.kanchipon_list_gen()) == 0 and self.is_riichi:
            self.can_ron = True
        elif room_dict[session['room']][0].kyoku.hai_remaining == 0:
            self.can_ron = True
        else:
            self.can_ron = self.can_ron_check(ron_hai)

        if self.can_ron:
            if self.is_computer == False:
                print('ron check')
                emit('gameupdate',{'msg':f'{ron_hai}{text[0]}\nYもしくはNを入力してください。'})
                room_dict[session['room']][1] = 'roncheck'
                ### BReak to ron_input to continue

            else:
                self.tehai.append(ron_hai)
                emit('gameupdate',{'msg':f'{self.name}が{ron_hai}{text[1]}'})
                print(f'{self.name}が{ron_hai}{text[1]}')
                if is_ron == False:
                    self.is_tumo_agari = True
                room_dict[session['room']][0].kyoku.winner = room_dict[session['room']][0].kyoku.current_player
                room_dict[session['room']][0].kyoku.kyoku_on = False
                self.mentu_check()
                return True

    def ron_input(self,choice):
        if self.is_ron == False:
            text = ('ツモりますか','をツモった！')
        else:
            text = ('ロンしますか','をロンした！')
        if choice == 'Y':
            emit('gameupdate',{'msg':f'{self.ron_hai}{text[1]}'})
            print(f'{self.ron_hai} ron')
            self.tehai.append(self.ron_hai)
            if self.is_ron == False:
                self.is_tumo_agari = True
            if self.possible_rinshan:
                self.is_rinshan = True
            room_dict[session['room']][0].kyoku.winner = room_dict[session['room']][0].kyoku.current_player
            room_dict[session['room']][0].kyoku.kyoku_on = False
            self.mentu_check()
            return True #return true for use with monzen check
        else:
            self.can_ron = False
            self.is_ron = False
            self.ron_hai = None


    def pon(self,pon_hai):
        if self.is_computer == False:
            #save possible pon hai
            self.possible_pon_hai = pon_hai
            #ask user if they will pon, pass to pon_user_input
            print('pon check')
            emit('gameupdate',{'msg':f'{self.name}、{pon_hai}をポンしますか？\nYもしくはNを入力してください。'})
            room_dict[session['room']][1] = 'pon_yesno'


        else:
            if self.is_tenpatteru == True:
                pass
            elif random.randint(0,7) == 0:
                self.tehai.append(pon_hai)
                #remove hai from other players kawa
                room_dict[session['room']][0].kyoku.ponkanchi_start_player.kawa.pop(-1)
                self.is_monzen = False
                emit('gameupdate',{'msg':f'{self.name}が{pon_hai}をポンしました！'})
                print(f'{self.name}が{pon_hai}をポンしました！')
                self.tenpai_check(not_turn=True)
                self.sutehai()

    #only executed when player inputs yes
    def pon_user_input(self,choice):
        self.sutehai_user_input(choice)





    def chi(self,chi_hai):
        if self.is_riichi:
            pass
        elif self.is_computer == False:
            print('chi check')
            emit('gameupdate',{'msg':f'{self.name}、{chi_hai}をチーしますか？\nYもしくはNを入力してください。'})
            room_dict[session['room']][1] = 'chi_yesno'


        else:
            if self.is_tenpatteru == True:
                pass
            elif random.randint(0,7) == 0:
                self.tehai.append(chi_hai)
                #remove hai from other players kawa
                room_dict[session['room']][0].kyoku.ponkanchi_start_player.kawa.pop(-1)
                self.is_monzen = False
                self.tenpai_check(not_turn=True)
                for mentu in self.mentuhai: #add chi mentu into chi hai
                    if chi_hai in mentu:
                        self.chi_hai.extend(mentu)
                emit('gameupdate',{'msg':f'{self.name}が{chi_hai}をチーしました！'})
                print(f'{self.name}{chi_hai} riichi')
                self.sutehai()

    #only executed when player inputs yes
    def chi_user_input(self,choice):
        self.sutehai_user_input(choice)
        self.is_monzen = False
        self.tenpai_check(not_turn=True)
        #adding chi hai to chi hai list is done in socketio app
        # for mentu in self.mentuhai: #add chi mentu into chi hai
        #     if room_dict[session['room']][0].kyoku.pon_kan_chi_check_sutehai in mentu:
        #         self.chi_hai.extend(mentu)


    def kan(self,kan_hai):
        if kan_hai in self.pon_hai:
            return False
        if self.is_computer == False:
            self.temp_kan_hai = kan_hai
            emit('gameupdate',{'msg':f'{kan_hai}をカンしますか？\nYもしくはNを入力してください。'})
            room_dict[session['room']][1] = 'kan_yesno'

        else:
            self.kan_hai.append(kan_hai)
            emit('gameupdate',{'msg':f'{self.name}が{kan_hai}をカンしました！'})
            print(f'{self.name} kan {kan_hai}')
            self.tenpai_check(not_turn=True)
            return True

    def kan_user_input(self):
        emit('gameupdate',{'msg':f'{self.temp_kan_hai}をカンしました！'})
        print(f'{self.temp_kan_hai} user kan')
        self.kan_hai.append(self.temp_kan_hai)
        #remove hai from other players kawa
        room_dict[session['room']][0].kyoku.ponkanchi_start_player.kawa.pop(-1)
        self.tenpai_check(not_turn=True)
        #add new dora
        room_dict[session['room']][0].kyoku.new_dora()
        self.is_monzen = False
        self.mochihai = room_dict[session['room']][0].kyoku.wanpai[0].pop(0)
        self.tenpai_check(not_turn=True)
        room_dict[session['room']][0].kyoku.player_turn()


    def mochihai_kan(self,mochihai):
        user_input = ''
        while user_input not in ('Y','N'):
            user_input = input(f'持ち牌の{mochihai}をカンしますか？\nYもしくはNを入力してください。').upper()
        if user_input == 'Y':
            emit('gameupdate',{'msg':f'{mochihai}をカンしました！'})
            print(f'{mochihai}をカンしました！')
            self.kan_hai.append(mochihai)
            self.tenpai_check(not_turn=True)
            return True
        else:
            return False

    def mochihai_kan_user_input(self):
        pass

    def first_round_kan(self):
        hai_count = {hai:self.tehai.count(hai) for hai in self.tehai}
        for hai,count in hai_count.items():
            if count == 4 and hai not in self.can_kan:
                if self.kan(hai):
                    self.tehai.remove(hai)
                    return True
        return False



    def ascending_mentu_finder(self,hai_list):
        sequence_hai = []
        a = (9,9)
        b = (10,10)
        i = 0
        while i < 8:
            for item in hai_list:
                #check if jihai or not
                if item[0] != 0:
                    if item[0] == a[0] and item[1] == a[1]+1 and item[0] == b[0] and item[1] == b[1]+2:
                        sequence_hai.append((b,a,item))
                        hai_list.remove(item)
                        hai_list.remove(a)
                        hai_list.remove(b)
                        a = (9,9)
                        b = (10,10)
                    elif item[0] == a[0] and item[1] == a[1]+1:
                        b = a
                        a = item
                    else:
                        a = item
                #do nothing for jihai
                else:
                    pass
            i += 1

        #give back list of ascending mentu found for atama(yes/no) check in mentu_check
        return sequence_hai

    def mentu_check(self):
        def find_most_shuntu(non_mentu): #this func will go through all possible atamas and check to see which atama grouping leaves the most mentu
            #check for mentu in sequence without removing atama from check list
            atama_in_list = non_mentu.copy()
            sequence_hai_no_atama = self.ascending_mentu_finder(atama_in_list)
            atama_hai = []
            non_mentu_same_count = {hai:non_mentu.count(hai) for hai in non_mentu}
            for hai,count in non_mentu_same_count.items():
                if count == 2 and hai not in atama_hai:
                    atama_hai.append(hai)
            #try removing all sets of 2 hai
            all_atama_removed = [hai for hai in non_mentu if hai not in atama_hai]
            all_atama_removed_mentu = self.ascending_mentu_finder(all_atama_removed)
            if len(all_atama_removed_mentu) >= len(sequence_hai_no_atama):
                    return all_atama_removed_mentu
            #try removing one set of 2 hai at a time
            for atama_hai_to_remove in atama_hai:
                one_atama_removed = [hai for hai in non_mentu if hai != atama_hai_to_remove]
                one_atama_removed_mentu = self.ascending_mentu_finder(one_atama_removed)
                if len(one_atama_removed_mentu) >= len(sequence_hai_no_atama):
                    return one_atama_removed_mentu
            return  sequence_hai_no_atama

        def kootu_finder(hai_list):
            kootu_found = []
            #check to see if there are same hai mentu
            samehai_count = {hai:hai_list.count(hai) for hai in hai_list}
            #remove hai that are in sets of 3 and add them to mentu list
            for item,value in samehai_count.items():
                if value == 3 and (item,item,item) not in kootu_found:
                    kootu_found.append((item,item,item))
                    #while item in self.non_mentu_hai:
                        #self.non_mentu_hai.remove(item)
            return kootu_found
        def simple_atama_counter(non_mentu):
            #self.has_atama = False
            atama_hai = []
            non_mentu_same_count = {hai:non_mentu.count(hai) for hai in non_mentu}
            for hai,count in non_mentu_same_count.items():
                if count == 2 and hai not in atama_hai:
                    atama_hai.append(hai)

            return len(atama_hai)
        def non_mentu_hai_list_gen(tehai,mentuhai):
            non_mentu_hai_list = tehai
            hai_in_mentu = []
            for mentu in mentuhai:
                for hai in mentu:
                    if hai in non_mentu_hai_list:
                        non_mentu_hai_list.remove(hai)
            return non_mentu_hai_list

        #sort tehai to avoid missing ascending hai
        self.sort_tehai()
        #clear self.mentuhai and self.can_kan_hai to avoid duplicates
        kootu_shuntu_mentuhai = []
        kootu_shuntu_can_kan_hai = []
        #create list of tehai to be deleted when mentu found
        kootu_shuntu_non_mentu_hai = self.tehai.copy()


        #remove hai that are in sets of 3 and add them to mentu list
        kootu = kootu_finder(kootu_shuntu_non_mentu_hai)
        for mentu in kootu:
            kootu_shuntu_mentuhai.append(mentu)
            kootu_shuntu_can_kan_hai.append(mentu[0])
            for hai in mentu:
                while hai in kootu_shuntu_non_mentu_hai:
                    kootu_shuntu_non_mentu_hai.remove(hai)

        #compare length of atama removed mentu and non removed, adding atama removed if longer
        kootu_shuntu_best = find_most_shuntu(kootu_shuntu_non_mentu_hai)
        for mentu in kootu_shuntu_best:
            kootu_shuntu_mentuhai.append(mentu)

        kootu_shuntu_atama_count = simple_atama_counter(kootu_shuntu_non_mentu_hai)

        #remove shuntu first before removing kootu
        shuntu_kootu_mentuhai = []
        shuntu_kootu_can_kan_hai = []
        shuntu_kootu_non_mentu_hai = self.tehai.copy()
        shuntu_kootu_mentuhai = find_most_shuntu(shuntu_kootu_non_mentu_hai)
        for mentu in shuntu_kootu_mentuhai:
            for hai in mentu:
                shuntu_kootu_non_mentu_hai.remove(hai)
        kootu2 = kootu_finder(shuntu_kootu_non_mentu_hai)
        for mentu in kootu2:
            shuntu_kootu_mentuhai.append(mentu)
            shuntu_kootu_can_kan_hai.append(mentu[0])

        shuntu_kootu_atama_count = simple_atama_counter(shuntu_kootu_non_mentu_hai)

        tehai_copy = self.tehai.copy() #make copy of tehai so not deleted in non mentu hai list creation
        #compare shuntu and kootu
        if len(shuntu_kootu_mentuhai) == len(kootu_shuntu_mentuhai):
            if shuntu_kootu_atama_count > kootu_shuntu_atama_count:
                self.mentuhai = shuntu_kootu_mentuhai
                self.non_mentu_hai =  non_mentu_hai_list_gen(tehai_copy,shuntu_kootu_mentuhai)
                self.can_kan_hai = shuntu_kootu_can_kan_hai
            elif kootu_shuntu_atama_count >= shuntu_kootu_atama_count:
                self.mentuhai = kootu_shuntu_mentuhai
                self.non_mentu_hai = non_mentu_hai_list_gen(tehai_copy,kootu_shuntu_mentuhai)
                self.can_kan_hai = kootu_shuntu_can_kan_hai
        else:
            self.mentuhai = kootu_shuntu_mentuhai
            self.non_mentu_hai = non_mentu_hai_list_gen(tehai_copy,kootu_shuntu_mentuhai)
            self.can_kan_hai = kootu_shuntu_can_kan_hai
        #print(len(self.mentuhai))
        #print(len(self.non_mentu_hai))
        #print(len(self.can_kan_hai))



    def tenpai_check(self,not_turn=False):
        self.machihai.clear()
        self.is_tenpatteru = False

        self.atama_check(self.tehai) #check to see if possible atama in non_mentu_hai

        self.mentu_check() #check for mentu in tehai

        self.atama_check(self.non_mentu_hai) #check again for atama

        if len(self.non_mentu_hai) > 2:
            for hai in self.atama_hai:
                self.non_mentu_hai.remove(hai)

        self.is_mentu_tenpai()

        self.is_chitoitu_tenpai()

        self.is_kokushimusou()

        self.can_chi_pon_check()

        if self.is_tenpatteru == True and not_turn == False and self.is_riichi == False:
            if self.is_computer == False and self.balance > 1000 and len(self.chi_hai) == 0 and len(self.pon_hai) == 0:
                emit('gameupdate',{'msg':f'{self.name}、リーチしますか？'})
                room_dict[session['room']][1] = 'riichi_yesno'

            elif self.is_computer == True and self.balance > 1000 and len(self.chi_hai) == 0 and len(self.pon_hai) == 0:
                self.is_riichi = True
                if room_dict[session['room']][0].kyoku.turn_count <= 4:
                        self.double_riichi = True
                emit('gameupdate',{'msg':f'{self.name}はリーチしました！'})
                print(f'{self.name}はリーチしました！')

    def player_riichi_input(self):
        self.is_riichi = True
        if room_dict[session['room']][0].kyoku.turn_count <= 4:
            self.double_riichi = True
        emit('gameupdate',{'msg':f'{self.name}はリーチしました！'})
        print(f'{self.name} riichi')


    def atama_check(self,hai_list):
        #self.has_atama = False
        self.atama_hai.clear()
        non_mentu_same_count = {hai:hai_list.count(hai) for hai in hai_list}
        for hai,count in non_mentu_same_count.items():
            if count == 2 and hai not in self.atama_hai:
                self.atama_hai.append(hai)
                self.atama_hai.append(hai)

    def is_mentu_tenpai(self):
        #check if length of mentu list is 4, no atama tenpai
        if len(self.mentuhai) == 4:
            self.is_tenpatteru = True
            self.machihai = [self.non_mentu_hai[0]]
        #has 3 mentu complete and one or more atama
        elif len(self.mentuhai) == 3 and len(self.atama_hai) >= 2:
            #check if waiting for one or more hai of same value
            if len(self.atama_hai) == 4:
                self.is_tenpatteru = True
                self.machihai = [self.atama_hai[0],self.atama_hai[2]]

            #check to see if ascending mentu ryomen/tanki machi
            elif self.non_mentu_hai[0][0] != 0 and self.non_mentu_hai[0][0] == self.non_mentu_hai[1][0] and self.non_mentu_hai[0][1] + 1 == self.non_mentu_hai[1][1]:
                self.is_tenpatteru = True
                #check to see what machihai are
                if self.non_mentu_hai[0][1] != 0 and self.non_mentu_hai[1][1] != 8:
                    self.machihai = [Hai(self.non_mentu_hai[0][0],(self.non_mentu_hai[0][1]-1)),Hai(self.non_mentu_hai[0][0],(self.non_mentu_hai[1][1]+1))]
                elif self.non_mentu_hai[0][1] == 0:
                    self.machihai = [Hai(self.non_mentu_hai[0][0],(self.non_mentu_hai[1][1]+1))]
                elif self.non_mentu_hai[1][1] == 8:
                    self.machihai = [Hai(self.non_mentu_hai[0][0],(self.non_mentu_hai[0][1]-1))]
            #check to see if ascending mentu with gap in between
            elif self.non_mentu_hai[0][0] != 0 and self.non_mentu_hai[0][0] == self.non_mentu_hai[1][0] and self.non_mentu_hai[0][1] + 2 == self.non_mentu_hai[1][1]:
                self.is_tenpatteru = True
                self.machihai = [Hai(self.non_mentu_hai[0][0],(self.non_mentu_hai[0][1]+1))]


    def is_chitoitu_tenpai(self):
        #check if holding 2 of each hai
        samehai_count = {hai:self.tehai.count(hai) for hai in self.tehai}

        #add 2 if in set of 2
        double_hai_count = 0
        for hai,count in samehai_count.items():
            if count == 2:
                double_hai_count += 1
        if double_hai_count == 12:
            self.is_tenpatteru = True
            #declare what hai the player is waiting for
            for hai,count in samehai_count.items():
                if count == 1:
                    self.machihai.append(hai)
                    break

    def is_kokushimusou(self):

        #check if kokushimusou (has 1 and 9 hai of pinzu,souzu,wanzu and all jihai)
        kokushimusou_jihai = [Hai(0,0),Hai(0,1),Hai(0,2),Hai(0,3),Hai(0,4),Hai(0,5),Hai(0,6)]
        kokushimusou_suuhai = [Hai(1,0),Hai(1,8),Hai(2,0),Hai(2,8),Hai(3,0),Hai(3,8)]
        #check if one of each zoku in hand
        suuhai_count = 0
        for hai in self.tehai:
            if hai[0] == 1 and hai in kokushimusou_suuhai:
                if hai[1] == 0 or hai[1] == 8:
                    kokushimusou_suuhai.remove(hai)
                    suuhai_count += 1
        for hai in self.tehai:
            if hai[0] == 2 and hai in kokushimusou_suuhai:
                if hai[1] == 0 or hai[1] == 8:
                    kokushimusou_suuhai.remove(hai)
                    suuhai_count += 1
        for hai in self.tehai:
            if hai[0] == 3 and hai in kokushimusou_suuhai:
                if hai[1] == 0 or hai[1] == 8:
                    kokushimusou_suuhai.remove(hai)
                    suuhai_count += 1

        #check how many unique jihai are in tehai
        jihai_count = 0
        counted_hai = []
        for hai in self.tehai:
            if hai in kokushimusou_jihai and hai not in counted_hai:
                jihai_count += 1
                counted_hai.append(hai)
                kokushimusou_jihai.remove(hai)

        #check if kokushimusou tenpai or not
        if suuhai_count == 6 and jihai_count == 6:
            self.is_tenpatteru = True
            #should be all number hai
            self.machihai = [kokushimusou_jihai[0]]
        elif suuhai_count == 5 and jihai_count == 7:
            self.is_tenpatteru = True
            self.machihai = [kokushimusou_suuhai[0]]

    def can_chi_pon_check(self):
        #reset all lists to avoid doubles
        self.can_chi_hai.clear()
        self.can_pon_hai.clear()
        a = (9,9)
        #add chi-able hai to can chi list
        for hai in self.tehai:
            #add chi-able hai if a is not a 1 hai and hai is not a 9 hai
            if hai[0] != 0 and hai[1] != 8 and hai[0] == a[0] and hai[1] == (a[1]+1) and a[1] != 0:
                self.can_chi_hai.append(Hai(hai[0],(hai[1]+1)))
                self.can_chi_hai.append(Hai(hai[0],(hai[1]-2)))
            #add only bottom hai if hai is a 9 hai
            elif hai[0] != 0 and hai[1] == 8 and hai[0] == a[0] and hai[1] == (a[1]+1):
                self.can_chi_hai.append(Hai(hai[0],(hai[1]-2)))
            #add only top hai if a is a 1 hai
            elif hai[0] != 0 and hai[0] == a[0] and hai[1] == (a[1]+1) and a[1] == 0:
                self.can_chi_hai.append(Hai(hai[0],(hai[1]+1)))
            else:
                a = hai
        #add pon-able hai to can pon list
        tehai_hai_count = {hai:self.tehai.count(hai) for hai in self.tehai}
        for hai,count in tehai_hai_count.items():
            if count == 2 and hai not in self.can_pon_hai:
                self.can_pon_hai.append(hai)

    def can_ron_check(self,ron_pai):
        def sanshokudoujun_check(mentuhai):
            memory1 = ((9,9),(9,9),(9,9))
            memory2 = ((9,9),(9,9),(9,9))
            for mentu in mentuhai:
                if mentu[0][1] == memory1[0][1] and mentu[2][1] == memory1[2][1] and mentu[2][1] == memory2[2][1]:
                    return True
                elif mentu[0][1] == memory1[0][1] and mentu[2][1] == memory1[2][1]:
                    memory2 = memory1
                    memory1 = mentu
                elif mentu[0][0] != 0 and mentu[0][1]+2 == mentu[2][1]:
                    memory1 = mentu
                else:
                    pass
            return False
        def sanshokudoukou_check(mentuhai):
            memory1 = ((9,9),(9,9),(9,9))
            memory2 = ((9,9),(9,9),(9,9))
            for mentu in mentuhai:
                if mentu[0][1] == memory1[0][1] and mentu[2][1] == memory1[2][1] and mentu[2][1] == memory2[2][1]:
                    return True
                elif mentu[0][1] == memory1[0][1] and mentu[2][1] == memory1[2][1]:
                    memory2 = memory1
                    memory1 = mentu
                elif mentu[0][0] != 0:
                    memory1 = mentu
                else:
                    pass
            return False
        def is_ikkituukan(ron_tehai):
            a = [9,9]
            b = [9,9]
            c = False
            for hai in ron_tehai:
                if hai[0] == a[0] and hai[1] == 8 and a[1]+1 == hai[1] and b[1]+2 == hai[1] and c:
                    return True
                elif hai[0] == a[0] and a[1] == 0 and hai[0] == self.tehai[2][0]:
                    c = True
                    b = a
                    a = hai
                elif hai[0] == a[0] and hai[1] == a[1]+1 and hai[0] == self.tehai[2][0]:
                    b = a
                    a = hai
                else:
                    a = hai
                    b = None
                    c = False
            return False

        monzen = False
        ron_tehai = [hai for hai in self.tehai]
        ron_tehai.append(ron_pai)
        #copied mentu check for ron check
        ron_tehai.sort()
        ron_mentuhai = []
        ron_new_mentu = [hai for hai in ron_tehai]
        samehai_count = {hai:self.tehai.count(hai) for hai in self.tehai}
        for mentu in self.mentuhai:
            if mentu not in ron_mentuhai:
                ron_mentuhai.append(mentu)
                for hai in mentu:
                    ron_new_mentu.remove(hai)
        ron_atama_hai = []
        non_mentu_same_count = {hai:ron_new_mentu.count(hai) for hai in ron_new_mentu}
        for hai,count in non_mentu_same_count.items():
            if count == 2:
                ron_atama_hai.append(hai)
                ron_atama_hai.append(hai)
                while hai in ron_new_mentu:
                    ron_new_mentu.remove(hai)
        ron_mentuhai.append(ron_new_mentu)

        for yaku_hai in (Hai(0,room_dict[session['room']][0].kazamuki),Hai(0,4),Hai(0,5),Hai(0,6)): #yakuhai check
            for mentu in ron_mentuhai:
                if yaku_hai in mentu:
                    return True
        if len([x for x in ron_tehai if x[0] != 0 and x[1] in (0,8)]) == 0: #tanyao
            return True

        if is_ikkituukan(ron_tehai):
            return True
        ###############
        if sanshokudoujun_check(ron_mentuhai):
            return True
        if sanshokudoukou_check(ron_mentuhai):
            return True



        ###############
        sanankou_set = set() # sanankou check
        for mentu in ron_mentuhai:
            if mentu[0] == mentu[2]:
                sanankou_set.add(mentu[0][0])
        if len(sanankou_set) == 3:
            return True
        del sanankou_set
        toitoi_list_count = 0 # toitoi check
        for mentu in ron_mentuhai:
            if mentu[0][0] != 0 and mentu[0] == mentu[2]:
                toitoi_list_count += 1
        if toitoi_list_count == 4:
            return True
        del toitoi_list_count
        chanta_count = 0 #chanta check
        for mentu in ron_mentuhai:
            if mentu[0][1] == 0 or mentu[0][1] == 8 or mentu[0][0] == 0:
                chanta_count += 1
        if chanta_count == 4:
            if ron_atama_hai[0][0] == 0 or ron_atama_hai[0][1] == 0 or ron_atama_hai[0][1] == 8:
                return True
        del chanta_count
        if len(self.kan_hai) >= 3:
            return True
        junchan_count = 0 #junchan check
        for hai in ron_tehai:
            if hai[0] != 0 and hai[1] in (0,8):
                junchan_count += 1
        if junchan_count == 14:
                return True
        del junchan_count
        honitu = True
        for hai in winner.tehai:
            if hai[0] == 0:
                pass
            elif hai[0] != winner.tehai[-1][0]:
                honitu = False
                break
        if honitu:
            return True
        del honitu

        if ron_atama_hai[0][0] == 0 and ron_atama_hai[0][1] in (4,5,6): #shousangen check
            sangenhai_count = 0
            for mentu in ron_mentu_hai:
                if mentu[0][0] == 0 and mentu[0][1] in (4,5,6):
                    sangenhai_count += 1
            if sangenhai_count == 2:
                return True
            del sangenhai_count
        is_honroutou = False #honroutou check
        for hai in ron_tehai:
            if hai[0] == 0 or hai[1] in (0,8):
                is_honroutou = True
            else:
                is_honroutou = False
                break
        if is_honroutou:
            return True
        del is_honroutou
        is_chinitu = True #chinitucheck
        for hai in ron_tehai:
            if hai[0] == ron_tehai[0][0]:
                is_chinitu = True
            else:
                is_chinitu = False
                break
        if is_chinitu:
            return True
        del is_chinitu
        sangenmentu_count = 0 #daisangen check
        for mentu in ron_mentu_hai:
            if mentu[0][0] == 0 and mentu[0][1] in (4,5,6):
                sangenmentu_count += 1
        if sangenmentu_count == 3:
            return True
        del sangenmentu_count
        shousuushii_hai_count = 0 #shousuushii check/daisuushii check
        for hai in ron_tehai:
            if hai[0] == 0 and hai[1] in (0,1,2,3):
                shousuushii_hai_count += 1
        if shousuushii_hai_count >= 11:
            return True
        del shousuushii_hai_count

        is_ryuuiisou = False #is ryuuissou check
        for hai in ron_tehai:
            if hai[0] == 1 or hai == Hai(0,5):
                is_ryuuiisou = True
            else:
                is_ryuuiisou = False
                break
        if is_ryuuiisou and Hai(0,5) in winner.tehai:
            return True
        del is_ryuuiisou
        is_tuuiisou = False #tuuiisou check
        for hai in ron_tehai:
            if hai[0] == 0:
                is_tuuiisou = True
            else:
                is_tuuiisou = False
                break
        if is_tuuiisou:
            return True
        del is_tuuiisou
        is_chinroutou = False #chinroutou check
        for hai in ron_tehai:
            if hai[0] != 0 and hai[1] in (0,8):
                is_chinroutou = True
            else:
                is_chinroutou = False
                break
        if is_chinroutou:
            return True

        return False
