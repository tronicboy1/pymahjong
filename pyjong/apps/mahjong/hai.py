from PIL import Image,ImageDraw,ImageFont
import os



class Hai:

    def __init__(self,zoku,value):

        basedir = os.path.abspath(os.path.dirname(__file__))

        self.japanese_zoku = {0:'字牌',1:'索子',2:'筒子',3:'萬子'}
        self.japanese_jihai_value = {0:'トン',1:'ナン',2:'シャー',3:'ペー',4:'ハク',5:'ハツ',6:'チュン'}
        self.japanese_value = {0:'イー',1:'リャン',2:'サン',3:'スー',4:'ウー',5:'ロー',6:'チー',7:'バー',8:'キュー'}
        self.japanese_zoku_yomi = {0:'',1:'ソウ',2:'ピン',3:'ワン'}
        self.pic = Image.open(basedir + '/static/'+'{},{}.jpg'.format(zoku,value))
        self.pic = self.pic.resize((60,100))

        self.zoku = zoku

        #only accept up to 7 for jihai
        if self.zoku == 0:
            if value > 6:
                raise ValueError('Jihai value cannot be greater than 7')
            else:
                self.value = value
        #only accept value up to 8 for non jihai
        elif self.zoku != 0:
            if value > 8:
                raise ValueError('Non-jihai value cannot exceed 9')
            self.value = value

        self.id = (self.zoku,self.value)

    def __str__(self):
        #check if jihai or not
        if self.zoku == 0:
            return f'{self.japanese_zoku[self.zoku]}の{self.japanese_jihai_value[self.value]}'
        else:
            return f'{self.japanese_zoku[self.zoku]}の{self.value + 1}'

    def __getitem__(self,item):
        return self.id[item]

    def __lt__(self,other):
        return self.id < other.id

    def __gt__(self,other):
        return self.id > other.id

    def __eq__(self,other):
        if other == None:
            return False
        elif self.id == other.id:
            return True
        else:
            return False

    def __hash__(self):
        return id(self)

    def __iter__(self):
        yield from self.__values
