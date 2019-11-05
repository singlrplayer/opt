
class blurRules:
    candleVal = [] #candle types. taken by class Files from config
    bodyRules = {} #bodyRules[candleVal[i]] = {} -> we'd have few bodyRules for every candle type. ihope
    shadowRules = {}#the same as body rules
    IOcandles = {'in':{},'out':{}} #input & ouput ANN candles. num
    learnArrayIn = [] #среднекрасивое решение для входов обучающей матрицы  : upShadow, body, DownShadow
    learnArrayOut = [] #среднекрасивое решение для выходов обучающей матрицы : upShadow, body, DownShadow
    arrayIn = [] #то, что мы подадим на вход после завершения обучения


    def getCandleRuleFromString(self, s):
        try:
            i = s.index(" ",0,len(s))
            candleType = s[0:i]
            s = s[i+1:len(s)]
            self.candleVal.append(candleType) #раз уж нашелся очередной свечей, то создаются все необходимые для правил словари
            self.IOcandles['in'][candleType] = {}
            self.IOcandles['out'][candleType] = {}
            self.bodyRules[candleType] = {}
            self.shadowRules[candleType] = {}
            try:
                i = s.index(" ",0,len(s))
                self.IOcandles['in'][candleType] = int(s[0:i])
                s = s[i+1:len(s)]
                try:
                    i = s.index(" ",0,len(s))
                    self.IOcandles['out'][candleType] = int(s[0:i])
                    s = s[i+1:len(s)]
                    try:
                        i = s.index("body",0,len(s))
                        j = s.index("{",0,len(s))
                        j1 = s.index("}",0,len(s))
                        bodyrules = s[j+1:j1]
                        self.parceRules(self.bodyRules[candleType],bodyrules)
                        s = s[j1 + 1:len(s)]
                        try:
                            i = s.index("shadow",0,len(s))
                            j = s.index("{",0,len(s))
                            j1 = s.index("}",0,len(s))
                            shadowrules = s[j+1:j1]
                            self.parceRules(self.shadowRules[candleType],shadowrules)
                        except Exception:
                            print ("ошибка чтения конфига. не найдены правила теней свечи в валютной паре  " + candleType)
                            return
                    except Exception:
                        print ("ошибка чтения конфига. не найдены правила тела свечи в валютной паре  " + candleType)
                        return 
                except Exception:
                    print ("ошибка чтения конфига. не найдено число выходных свечей для ANN в валютной паре (либо не отделено пробелом)  " + candleType)
                    return 
            except Exception:
                print ("ошибка чтения конфига. не найдено число входных свечей для ANN в валютной паре (либо не отделено пробелом) " + candleType)
                return 
        except Exception:
            print ("ошибка чтения конфига. не найден тип свечей (либо не отделен пробелом)" + s)
            return

    def parceRules(self, mydict, rulesSTR):
        tmp = rulesSTR.split(';')
        i = 0
        while i < len(tmp): #TODO разобраться почему работает только так
            try:
                j = tmp[i].index(':',0,len(tmp[i]))
                key = tmp[i][j + 1:len(tmp[i])]
                mydict[key] = []
                tmp[i] = tmp[i][0:j]
                if (',' in tmp[i]):
                    j = tmp[i].index(',',0,len(tmp[i]))
                    mydict[key].append(float(tmp[i][1:j]))
                    mydict[key].append(float(tmp[i][j + 1:len(tmp[i]) - 1]))
                else:
                    mydict[key].append(float(tmp[i][1:len(tmp[i]) - 1]))
            except Exception:
                print("ошибка синтатксиса праввил свечей")
            i = i + 1

    def createInputArray(self, sizeIn, data, count, Pos = -1):
        s = data[-1]
        try:
                s_in = s[2:len(s) - 1]
                self.arrayIn = self.getvalsFromLine(s_in)
        except Exception:
                print("blurRules.py (createInputArray): wrong string format " + s)
            
    def createLearnArray(self, sizeIn, sizeOut, data, startPos, count):
        if (startPos == -1): return -1 # we got end of file (костыль. TODO: разобраться, и сделать всё по-людски)
        if(startPos == len(data)):return -1# end of data
        s = data[startPos]
        startPos = startPos + 1 #c++ is crying
        try:
                tmp = s.split('][')
                s_in = tmp[0][2:len(tmp[0]) - 1] #at first in row
                self.learnArrayIn = self.getvalsFromLine(s_in)
                s_out = tmp[1].strip(']\n')  ##at secont out row
                self.learnArrayOut = self.getvalsFromLine(s_out)
        except Exception:
                print("blurRules.py (createLearnArray): wrong string format: " + s)
        if(startPos == len(data)):return -1# end of data
        return (startPos)

    def getvalsFromLine(self, s):
        tmp = s.split('], [')
        tmpCandle = '' #candle string temporary (shadow,body,shadow)
        tmpArr = [[],[],[],[]]
        for i in range(len(tmp)):
            tmpCandle = tmp[i].strip('\'')
            tmpCandle = tmpCandle.strip('[')
            tmpCandle = tmpCandle.strip(']')
            tmp1 = tmpCandle.split(',')
            for j in range(len(tmp1)):
                tmpArr[j].append(float(tmp1[j]))
        return tmpArr

        

