import math
import random
from flask_socketio import emit
from pyjong.apps.mahjong.player import Player
from pyjong.apps.mahjong.kyoku import Kyoku
from pyjong.apps.mahjong.hai import Hai
from pyjong.apps.socketioapps.mahjongsocketio import room_dict
from flask import session

class Game():

    def __init__(self):
        self.oya = 0
        self.kazamuki = 0
        self.game_on = True
        self.kyoku_suu = 0
        self.kyoku = None
        #variable for kyoku win count to be used to update database
        self.player1_kyokuwin_count = 0
        self.player3_kyokuwin_count = 0
        #variable for game win count to be used with database
        self.player1_gamewin_count = 0
        self.player3_gamewin_count = 0


        emit('gameupdate',{'msg':'ようこそ、Pyjongへ'},room=session['room'])
        #players_input = ''
        #while players_input not in ('1','2'):
            #players_input = input('プレーヤー数を入力してください。\n（"1"もしくは"2"）:')


    def create_players(self,players,player1_name,player3_name=None):
        if players == 1:
            self.player1 = Player(player1_name,is_computer=False)
            self.player2 = Player('Computer 1')
            self.player3 = Player('Computer 2')
            self.player4 = Player('Computer 3')
        elif players == 2:
            self.player1 = Player(player1_name,is_computer=False)
            self.player2 = Player('Computer 1')
            self.player3 = Player(player3_name,is_computer=False)
            self.player4 = Player('Computer 2')



        self.player_dict = {0:self.player1,1:self.player2,2:self.player3,3:self.player4}

        self.oya_gime()

        self.kyoku = Kyoku(self.player1,self.player2,self.player3,self.player4,bakaze=self.kazamuki,oya=self.oya)



    def end_kyoku_check(self):
        #set key to end to avoid cycle
        room_dict[session['room']][1] = 'end'
        #link kyoku back to room_dict kyoku
        self.kyoku = room_dict[session['room']][0].kyoku
        if self.kyoku.winner == None:
            emit('gameupdate',{'msg':'流局！'},room=session['room'])
            tenpatteru_list = []
            for player in self.player_dict.values(): #add players who are tenpatteru into tenpatteru list
                if player.is_tenpatteru:
                    tenpatteru_list.append(player)
                else:
                    pass
            if len(tenpatteru_list) == 0:
                emit('gameupdate',{'msg':'ノーテン！'},room=session['room'])
            elif len(tenpatteru_list) == 1:
                tenpatteru_list[0].add_funds(3000)
                for player in self.player_dict.values():
                    if player not in tenpatteru_list:
                        player.remove_funds(1000)
            elif len(tenpatteru_list) == 2:
                for player in tenpatteru_list:
                    player.add_funds(1500)
                for player in self.player_dict.values():
                    if player not in tenpatteru_list:
                        player.remove_funds(1500)
            elif len(tenpatteru_list) == 3:
                for player in tenpatteru_list:
                    player.add_funds(1000)
                for player in self.player_dict.values():
                    if player not in tenpatteru_list:
                        player.remove_funds(3000)

            if self.player_dict[self.oya].is_tenpatteru == False:
                self.oya_koutai()
        else: #if there is a winner, must calculate score here
            tensuu = self.tensuu_calc(self.kyoku.winner,self.kazamuki,self.oya,self.kyoku.dora,self.kyoku.uradora,self.kyoku.hai_remaining,self.kyoku.turn_count)

            #give score to winner
            if self.kyoku.winner.is_tumo_agari:
                if self.kyoku.winner == self.oya:
                    self.kyoku.winner.add_funds(tensuu)
                    for player in self.player_dict.values():
                        if player == self.kyoku.winner:
                            pass
                        else:
                            remove = int(math.ceil(tensuu/300))*100
                            player.remove_funds(remove)
                else:
                    self.kyoku.winner.add_funds(tensuu)
                    for player in self.player_dict.values():
                        if player == self.kyoku.winner:
                            pass
                        elif player == self.oya:
                            remove = int(math.ceil(tensuu/200))*100
                            player.remove_funds(remove)
                        else:
                            remove = int(math.ceil(tensuu/400))*100
                            player.remove_funds(remove)
            else:
                self.kyoku.winner.add_funds(tensuu)
                self.kyoku.current_player.remove_funds(tensuu)



    def change_kazamuki(self):
        if self.kazamuki == 3:
            self.game_on = False #end game if 16kyoku played through
        else:
            self.kazamuki += 1

    def oya_gime(self):
        self.oya = 0
        saikoro_result = random.randint(1,6)
        emit('gameupdate',{'msg':f'{saikoro_result}が出ました！'},room=session['room'])
        for n in range(0,saikoro_result):
            if self.oya == 3:
                self.oya = 0
            else:
                self.oya += 1
        emit('gameupdate',{'msg':f'{self.player_dict[self.oya].name}が親になりました！'},room=session['room'])

    def oya_koutai(self):
        if self.oya == 3:
            self.oya = 0
        else:
            self.oya += 1
        emit('gameupdate',{'msg':f'{self.player_dict[self.oya].name}が新しい親！'},room=session['room'])

    def tensuu_calc(self,winner,bakaze,oya,dora,uradora,hai_remaining,round_count):

        def is_kokushimusou(winner):
            #check if kokushimusou (has 1 and 9 hai of pinzu,souzu,wanzu and all jihai)
            kokushimusou_jihai = [Hai(0,0),Hai(0,1),Hai(0,2),Hai(0,3),Hai(0,4),Hai(0,5),Hai(0,6)]
            kokushimusou_suuhai = [Hai(1,0),Hai(1,8),Hai(2,0),Hai(2,8),Hai(3,0),Hai(3,8)]
            #check if one of each zoku in hand
            suuhai_count = 0
            for hai in winner.tehai:
                if hai[0] == 1 and hai in kokushimusou_suuhai:
                    if hai[1] == 0 or hai[1] == 8:
                        kokushimusou_suuhai.remove(hai)
                        suuhai_count += 1
            for hai in winner.tehai:
                if hai[0] == 2 and hai in kokushimusou_suuhai:
                    if hai[1] == 0 or hai[1] == 8:
                        kokushimusou_suuhai.remove(hai)
                        suuhai_count += 1
            for hai in winner.tehai:
                if hai[0] == 3 and hai in kokushimusou_suuhai:
                    if hai[1] == 0 or hai[1] == 8:
                        kokushimusou_suuhai.remove(hai)
                        suuhai_count += 1

            #check how many unique jihai are in tehai
            jihai_count = 0
            counted_hai = []
            for hai in winner.tehai:
                if hai in kokushimusou_jihai and hai not in counted_hai:
                    jihai_count += 1
                    counted_hai.append(hai)
                    kokushimusou_jihai.remove(hai)

            #check if kokushimusou tenpai or not
            if suuhai_count == 6 and jihai_count == 7:
                return True
            else:
                return False

        def is_ikkituukan(winner):
            winner.tehai.sort()
            a = [9,9]
            b = [9,9]
            c = False
            for hai in winner.tehai:
                if hai[0] == a[0] and hai[1] == 8 and a[1]+1 == hai[1] and b[1]+2 == hai[1] and c:
                    return True
                elif hai[0] == a[0] and a[1] == 0:
                    c = True
                    b = a
                    a = hai
                elif hai[0] == a[0] and hai[1] == a[1]+1 and hai[0] == winner.tehai[2][0]:
                    b = a
                    a = hai
                else:
                    a = hai
                    b = [9,9]
                    c = False
            return False

        def is_chitoitu_agari(winner):
            #check if holding 2 of each hai
            samehai_count = {hai:winner.tehai.count(hai) for hai in winner.tehai}

            #add 2 if in set of 2
            double_hai_count = 0
            for hai,count in samehai_count.items():
                if count == 2:
                    double_hai_count += 1
            if double_hai_count == 14:
                return True
            else:
                return False
        def sanshokudoujun_check(winner):
            memory1 = ((9,9),(9,9),(9,9))
            memory2 = ((9,9),(9,9),(9,9))
            for mentu in winner.mentuhai:
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
        def sanshokudoukou_check(winner):
            memory1 = ((9,9),(9,9),(9,9))
            memory2 = ((9,9),(9,9),(9,9))
            for mentu in winner.mentuhai:
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
        #fukeisan
        monzen = winner.is_monzen
        winner.atama_check(winner.non_mentu_hai)

        fu = 20

        if monzen:
            fu += 10
        if winner.is_tumo_agari:
            fu += 2
        for mentu in winner.mentuhai:
            if mentu[0][1] == mentu[2][1]:
                if mentu[0][1] != 0 and mentu[0][1] != 8:
                    if mentu[0] in winner.pon_hai:
                        fu += 2
                    if mentu[0] in winner.kan_hai:
                        fu += 8
                    else:
                        fu += 4
                elif mentu[0][1] == 0 or mentu[0][1] == 8:
                    if mentu[0] in winner.pon_hai:
                        fu += 4
                    if mentu[0] in winner.kan_hai:
                        fu += 16
                    else:
                        fu += 8
        if winner.atama_hai[0] in (Hai(0,4),Hai(0,5),Hai(0,6)):
            fu += 2
        if len(winner.machihai) == 1:
            fu += 2
        if winner.is_tumo_agari == False:
            fu += 10
        else:
            fu += 2

        if is_chitoitu_agari(winner):
            fu = 25
        elif len(winner.machihai) >= 2:
            if winner.machihai[0][1]+2 == winner.machihai[1][1] and monzen: #pinfu check
                if winner.is_tumo_agari:
                    fu = 20
                else:
                    fu = 30

        #hankeisan
        han = 0
        dora_plus_one = []
        for hai in dora:
            if hai.id == (0,6):
                dora_plus_one.append(Hai(0,4))
            elif hai.id == (0,3):
                dora_plus_one.append(Hai(0,0))
            elif hai[1] == 8:
                dora_plus_one.append(Hai(hai[0],0))
            else:
                dora_plus_one.append(Hai(hai[0],hai[1]+1))
        for hai in winner.tehai: #dora check
            if hai in dora_plus_one:
                han += 1
                emit('gameupdate',{'msg':'ドラ！'},room=session['room'])
        if winner.is_riichi:
            han += 1
            emit('gameupdate',{'msg':'リーチ！'},room=session['room'])
            ura_plus_one = []
            for hai in uradora:
                if hai.id == (0,6):
                    ura_plus_one.append(Hai(0,4))
                elif hai.id == (0,3):
                    ura_plus_one.append(Hai(0,0))
                elif hai[1] == 8:
                    ura_plus_one.append(Hai(hai[0],0))
                else:
                    ura_plus_one.append(Hai(hai[0],hai[1]+1))
            for hai in winner.tehai: #uradora check
                if hai in ura_plus_one:
                    han += 1
                    emit('gameupdate',{'msg':'裏ドラ！'},room=session['room'])
            if winner.is_ippatu and monzen: #riichi ippatu check
                han += 1
                emit('gameupdate',{'msg':'リーチ一発！'},room=session['room'])
        if winner.is_tumo_agari and monzen: #monzen tumo check
            han += 1
            emit('gameupdate',{'msg':'門前ツモ！'},room=session['room'])
        for yaku_hai in (Hai(0,bakaze),Hai(0,4),Hai(0,5),Hai(0,6)): #yakuhai check
            for mentu in winner.mentuhai:
                if yaku_hai in mentu:
                    han += 1
                    emit('gameupdate',{'msg':'役牌！'},room=session['room'])
        if len([x for x in winner.tehai if x[0] != 0 and x[1] in (0,8)]) == 0: #tanyao
            han += 1
            emit('gameupdate',{'msg':'タンヤオ！'},room=session['room'])
        if len(winner.machihai) >= 2:
            if winner.machihai[0][1]+2 == winner.machihai[1][1] and monzen: #pinfu check
                han += 1
                emit('gameupdate',{'msg':'ピンフ！'},room=session['room'])


        if hai_remaining == 0 and winner.is_tumo_agari: #haitei check
            han += 1
            emit('gameupdate',{'msg':'ハイテイアガリ！'},room=session['room'])
        if hai_remaining == 0 and winner.is_tumo_agari == False:
            han += 1
            emit('gameupdate',{'msg':'ホウテイロンアガリ！'},room=session['room'])
        if winner.is_rinshan:
            han += 1
            emit('gameupdate',{'msg':'リンシャンカイホウ！'},room=session['room'])
        if winner.is_chankan:
            han += 1
            emit('gameupdate',{'msg':'チャンカン！'},room=session['room'])
        if winner.double_riichi:
            han += 1
            emit('gameupdate',{'msg':'ダブルリーチ！'},room=session['room'])
        if is_chitoitu_agari(winner):
            han += 2
            emit('gameupdate',{'msg':'チートイツ！'},room=session['room'])
        if is_ikkituukan(winner):
            if monzen:
                han += 2
            else:
                han += 1
            emit('gameupdate',{'msg':'一気通貫！'},room=session['room'])
        if sanshokudoujun_check(winner):
            emit('gameupdate',{'msg':'三色同順！'},room=session['room'])
            if monzen:
                han += 2
            else:
                han += 1
        if sanshokudoukou_check(winner):
            if monzen:
                emit('gameupdate',{'msg':'三色同刻！'},room=session['room'])
                han += 2
        sanankou_set = set() # sanankou check
        for mentu in winner.mentuhai:
            if mentu[0] == mentu [2]:
                sanankou_set.add(mentu[0][0])
        if len(sanankou_set) == 3:
            han += 2
            emit('gameupdate',{'msg':'三暗刻！'},room=session['room'])
        toitoi_list_count = 0 # toitoi check
        for mentu in winner.mentuhai:
            if mentu[0][0] != 0 and mentu[0] == mentu [2]:
                toitoi_list_count += 1
        if toitoi_list_count == 4:
            han += 2
            emit('gameupdate',{'msg':'三色同刻！'},room=session['room'])
        del toitoi_list_count
        chanta_count = 0 #chanta check
        for mentu in winner.mentuhai:
            if mentu[0][1] == 0 or mentu[0][1] == 8 or mentu[0][0] == 0:
                chanta_count += 1
        if chanta_count == 4:
            if winner.atama_hai[0][0] == 0 or winner.atama_hai[0][1] == 0 or winner.atama_hai[0][1] == 8:
                if monzen:
                    han += 2
                else:
                    han += 1
                emit('gameupdate',{'msg':'混全帯么九！'},room=session['room'])
        del chanta_count
        if len(winner.kan_hai) == 3:
            han += 2
            emit('gameupdate',{'msg':'三槓子！'},room=session['room'])

        #ipeko ryanpeikou check
        ryanpeikou_count = 0
        counted_mentu = []
        shuntu_mentu = [mentu for mentu in winner.mentuhai if mentu[0][1]+2 == mentu[2][1]]
        for mentu in shuntu_mentu:
            if winner.mentuhai.count(mentu) == 2 and mentu not in counted_mentu:
                #add mentu here to make sure not counted twice
                counted_mentu.append(mentu)
                ryanpeikou_count += 1
                emit('gameupdate',{'msg':'一盃口！'},room=session['room'])

        if ryanpeikou_count == 2:
            han += 2 #add two because
            emit('gameupdate',{'msg':'二盃口！'},room=session['room'])
        elif ryanpeikou_count == 1:
            han += 1
            emit('gameupdate',{'msg':'一盃口！'},room=session['room'])

        del ryanpeikou_count
        junchan_count = 0 #junchan check
        for hai in winner.tehai:
            if hai[0] != 0 and hai[1] in (0,8):
                junchan_count += 1
        if junchan_count == 14:
            if monzen:
                han += 3
            else:
                han += 2
            emit('gameupdate',{'msg':'ジュンチャン'},room=session['room'])
        del junchan_count
        #honitu check
        honitu = True
        for hai in winner.tehai:
            if hai[0] == 0:
                pass
            elif hai[0] != winner.tehai[-1][0]:
                honitu = False
                break
        if honitu:
            if monzen:
                han += 3
            else:
                han += 2
            emit('gameupdate',{'msg':'混一色！'},room=session['room'])
        del honitu

        if winner.atama_hai[0][0] == 0 and winner.atama_hai[0][1] in (4,5,6): #shousangen check
            sangenhai_count = 0
            for mentu in winner.mentuhai:
                if mentu[0][0] == 0 and mentu[0][1] in (4,5,6):
                    sangenhai_count += 1
            if sangenhai_count == 2:
                han += 4
                emit('gameupdate',{'msg':'小三元！'},room=session['room'])
            del sangenhai_count
        is_honroutou = False #honroutou check
        for hai in winner.tehai:
            if hai[0] == 0 or hai[1] in (0,8):
                is_honroutou = True
            else:
                is_honroutou = False
                break
        if is_honroutou:
            han += 4
            emit('gameupdate',{'msg':'混老頭！'},room=session['room'])
        del is_honroutou
        is_chinitu = True #chinitucheck
        for hai in winner.tehai:
            if hai[0] == winner.tehai[0][0]:
                is_chinitu = True
            else:
                is_chinitu = False
                break
        if is_chinitu:
            if monzen:
                han += 6
            else:
                han += 5
            emit('gameupdate',{'msg':'清一色！'},room=session['room'])
        del is_chinitu
        is_suuankou = False #suuankou check
        for mentu in winner.mentuhai:
            if mentu[0][1] == mentu[2][1]:
                is_suuankou = True
            else:
                is_suuankou = False
        if is_suuankou and monzen:
            han = 13
            emit('gameupdate',{'msg':'四暗刻！！'},room=session['room'])
        del is_suuankou
        sangenmentu_count = 0 #daisangen check
        for mentu in winner.mentuhai:
            if mentu[0][0] == 0 and mentu[0][1] in (4,5,6):
                sangenmentu_count += 1
        if sangenmentu_count == 3:
            han = 13
            emit('gameupdate',{'msg':'大三元！！'},room=session['room'])
        del sangenmentu_count
        if is_kokushimusou(winner) and monzen: #kokushimusou check
            han = 13
            emit('gameupdate',{'msg':'国士無双！！'},room=session['room'])
        shousuushii_hai_count = 0 #shousuushii check/daisuushii check
        for hai in winner.tehai:
            if hai[0] == 0 and hai[1] in (0,1,2,3):
                shousuushii_hai_count += 1
        if shousuushii_hai_count == 11:
            han = 13
            emit('gameupdate',{'msg':'小四喜！！'},room=session['room'])
        elif shousuushii_hai_count == 12:
            han = 13
            emit('gameupdate',{'msg':'大四喜！！'},room=session['room'])
        del shousuushii_hai_count
        is_ryuuiisou = False #is ryuuissou check
        for hai in winner.tehai:
            if hai[0] == 1 or hai == Hai(0,5):
                is_ryuuiisou = True
            else:
                is_ryuuiisou = False
                break
        if is_ryuuiisou and Hai(0,5) in winner.tehai:
            han = 13
            emit('gameupdate',{'緑一色！！'},room=session['room'])
        del is_ryuuiisou
        is_tuuiisou = False #tuuiisou check
        for hai in winner.tehai:
            if hai[0] == 0:
                is_tuuiisou = True
            else:
                is_tuuiisou = False
                break
        if is_tuuiisou:
            han = 13
            emit('gameupdate',{'msg':'字一色！！'},room=session['room'])
        del is_tuuiisou
        is_chinroutou = False #chinroutou check
        for hai in winner.tehai:
            if hai[0] != 0 and hai[1] in (0,8):
                is_chinroutou = True
            else:
                is_chinroutou = False
                break
        if is_chinroutou:
            han = 13
            emit('gameupdate',{'msg':'清老頭！！'},room=session['room'])
        del is_chinroutou
        if len(winner.kan_hai) == 4: #suukantu check
            han = 13
            emit('gameupdate',{'msg':'四槓子！！'},room=session['room'])
        chuurenpoutou_hai = [Hai(3,0),Hai(3,0),Hai(3,0),Hai(3,1),Hai(3,2),Hai(3,3),Hai(3,4),Hai(3,5),Hai(3,6),Hai(3,7),Hai(3,8),Hai(3,8),Hai(3,8)]
        for hai in winner.tehai:
            if hai in chuurenpoutou_hai:
                chuurenpoutou_hai.remove(hai)
            elif len(chuurenpoutou_hai) == 0:
                if hai[0] == 3:
                    han = 13
                    emit('gameupdate',{'msg':'九蓮宝燈'},room=session['room'])
        del chuurenpoutou_hai
        if round_count < 4 and monzen:
            no_kanchipon = False
            for player in (self.player1,self.player2,self.player3,self.player4):
                if len(player.kanchipon_list_gen()) == 0:
                    no_kanchipon = True
                else:
                    no_kanchipon = False
                    break
            if oya == winner:
                han = 13
                emit('gameupdate',{'msg':'天和！！'},room=session['room'])
            elif no_kanchipon:
                han = 13
                emit('gameupdate',{'msg':'地和！！'},room=session['room'])
        #set han to 13 if over 13
        emit('gameupdate',{'msg':f'{fu}符の{han}翻！'},room=session['room'])

        if han > 13:
            han = 13
            emit('gameupdate',{'msg':'数え役満！'},room=session['room'])
        elif han >= 11:
            emit('gameupdate',{'msg':'三倍満！'},room=session['room'])
        elif han >= 8:
            emit('gameupdate',{'msg':'倍満！'},room=session['room'])
        elif han >= 6:
            emit('gameupdate',{'msg':'跳満！'},room=session['room'])
        elif han >= 3:
            emit('gameupdate',{'msg':'満願！'},room=session['room'])

        #calculate score
        if winner == oya:
            score = fu*8*(2**(han+2))
        else:
            score = fu*4*(2**(han+2))

        score = int(math.ceil(score/100))*100

        return score

    def kyoku_suu_change(self):
        if self.kyoku_suu == 3:
            self.change_kazamuki()
            self.kyoku_suu = 0
        else:
            self.kyoku_suu += 1

    def kyoku_summary(self):
        emit('gameupdate',{'msg':f'{self.player1.name}:{self.player1.balance}点'},room=session['room'])
        emit('gameupdate',{'msg':f'{self.player2.name}:{self.player2.balance}点'},room=session['room'])
        emit('gameupdate',{'msg':f'{self.player3.name}:{self.player3.balance}点'},room=session['room'])
        emit('gameupdate',{'msg':f'{self.player4.name}:{self.player4.balance}点'},room=session['room'])

        if self.game_on:
            emit('gameupdate',{'msg':'続けて新しい局に進みますか？(YもしくはN)'},room=session['room'])
            room_dict[session['room']][1] = 'newkyoku_yesno'

    def kyoku_summary_choice(self,choice):
        choice = choice.upper()
        if choice == 'N':
            self.game_on = False
        else:
            self.clear_players()

    def clear_players(self):
        for player in self.player_dict.values():
            player.clear()
        #reset kyoku here
        self.oya_gime()
        self.kyoku = Kyoku(self.player1,self.player2,self.player3,self.player4,bakaze=self.kazamuki,oya=self.oya)
