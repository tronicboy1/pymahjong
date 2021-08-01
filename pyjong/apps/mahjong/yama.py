from random import shuffle
from pyjong.apps.mahjong.hai import Hai

class Yama():

    def __init__(self):
        self.all_yama = []
        pot = []

        #generate list of all the hais
        while len(pot) < 136:
            for zoku in range(0,4):
                if zoku == 0:
                    for value in range(0,7):
                        pot.append(Hai(zoku,value))
                else:
                    for value in range(0,9):
                        pot.append(Hai(zoku,value))

        #shuffle hai in pot
        shuffle(pot)

        #assign hai to four yama with hai on bottom and top
        ton_top = []
        ton_bottom = []
        nan_top = []
        nan_bottom = []
        sha_top = []
        sha_bottom = []
        pe_top = []
        pe_bottom = []


        while len(pot) != 0:
            if len(ton_top) != 17:
                ton_top.append(pot.pop(0))
            elif len(ton_bottom) != 17:
                ton_bottom.append(pot.pop(0))
            elif len(nan_top) != 17:
                nan_top.append(pot.pop(0))
            elif len(nan_bottom) != 17:
                nan_bottom.append(pot.pop(0))
            elif len(sha_top) != 17:
                sha_top.append(pot.pop(0))
            elif len(sha_bottom) != 17:
                sha_bottom.append(pot.pop(0))
            elif len(pe_top) != 17:
                pe_top.append(pot.pop(0))
            elif len(pe_bottom) != 17:
                pe_bottom.append(pot.pop(0))
        #combine all hai into one list
        self.all_yama = ((ton_top,ton_bottom),(nan_top,nan_bottom),(sha_top,sha_bottom),(pe_top,pe_bottom))

    def yama_hai_count(self):
        count = 0
        for yama in self.all_yama:
            for bottop in yama:
                for hai in bottop:
                    count +=1
        return count
