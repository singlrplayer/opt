
class lineVal:
    auth = 0 #аутентичность = 0, если в исходных данных (минутных) небыло дыр. в противном случае значение равно количеству меньших свеч (у нас одна свеча делается из другой, а не все из минутных), в которых были дыры
    freq = 0 #количество неаутентичных _минутных_ свеч в составе текущей
    #TODO: переписать candlecreate с учетом использования в\у параметров
    cur = '' #валютная пара
    date = '' #дата
    time = '' #время
    openVal = 0.0 #начало свечки
    hightVal = 0.0 #верхняя тень свечки
    closeVal = 0.0 #конец свечки
    lowVal = 0.0 #нижняя тень свечки
    lineEnd = '' #херня какая-то
    candleVal = ['open','close','hight','low', 'auth'] #ключи. не трогать. для некоторых других мест. переделать. последний параметр характеризирует подлинность свечки (0 значит подлинный)
    candle = {} #попытка все сделать красиво
    olddata = {'olddate':'','oldtime':'','olDopenVal':0,'olDhightVal':0,'olDlowVal':0,'olDcloseVal':0} #костыль с рюшечками
    
    def rememberOldDatatime(self, val):
        self.olddata['olddate'] = val.d
        self.olddata['oldtime'] = val.t

    def rememberOldCandle(self):
       self.olddata['olDopenVal'] = lineVal.candle['open']
       self.olddata['olDlowVal'] = lineVal.candle['low']
       self.olddata['olDhightVal'] = lineVal.candle['hight']
       self.olddata['olDcloseVal'] = lineVal.candle['close'] 

def getCandleFromSource(s): #извлекаем свечу из строки файла МТ4 пример "2019.09.26,09:38,0.8860,0.8861,0.8859,0.8861,5"
    try:
        tmp = s.split(',')
        lineVal.date = str(tmp[0])
        lineVal.time = str(tmp[1])
        lineVal.candle['open'] = lineVal.openVal = float(tmp[2])
        lineVal.candle['hight'] = lineVal.hightVal = float(tmp[3])
        lineVal.candle['low'] = lineVal.lowVal = float(tmp[4])
        lineVal.candle['close'] = lineVal.closeVal = float(tmp[5])
        lineVal.candle['auth'] = 0
        return lineVal
    except Exception:
        print ("ошибка формата полученной строки: \n " + str(s) + "\nожидается формат: <DTYYYYMMDD>,<TIME>,<OPEN>,<HIGH>,<LOW>,<CLOSE>,<VOL>")
        return -1


        
    """try:
        i = s.index(",",0,len(s))
        lineVal.cur = s[0:i]
        s = s[i+1:len(s)]
        i = s.index(",",0,len(s))
        lineVal.date = s[0:i]
        s = s[i+1:len(s)]
        i = s.index(",",0,len(s))
        lineVal.time = s[0:i]
        s = s[i+1:len(s)]
        i = s.index(",",0,len(s))
        lineVal.candle['open'] = lineVal.openVal = Decimal(s[0:i])
        s = s[i+1:len(s)]
        i = s.index(",",0,len(s))
        lineVal.candle['hight'] = lineVal.hightVal = Decimal(s[0:i])
        s = s[i+1:len(s)]
        i = s.index(",",0,len(s))
        lineVal.candle['low'] = lineVal.lowVal = Decimal(s[0:i])
        s = s[i+1:len(s)]
        i = s.index(",",0,len(s))
        lineVal.candle['close'] = lineVal.closeVal = Decimal(s[0:i])
        lineVal.lineEnd = s[i+1:len(s)]
        lineVal.candle['auth'] = 0
        return lineVal
    except Exception:
        print ("ошибка формата полученной строки: \n " + str(s) + "\nожидается формат: <TICKER>,<DTYYYYMMDD>,<TIME>,<OPEN>,<HIGH>,<LOW>,<CLOSE>,<VOL>")"""

def getCandleFrom(s):
    try:
        i = s.index(" ",0,len(s))
        lineVal.auth = int(s[0:i])
        s = s[i+1:len(s)]
        try:
            i = s.index(" ",0,len(s))
            lineVal.freq = int(s[0:i])
            getCandleFromSource(s)
            return lineVal
        except Exception:
            getCandleFromSource(s)
            lineVal.auth = 1
            lineVal.freq = 1
            return lineVal
    except Exception:
        getCandleFromSource(s)
        lineVal.auth = 0
        lineVal.freq = 0
        return lineVal
        

