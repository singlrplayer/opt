from myParsLine import getCandleFrom
import itertools
#import ipdb


class learnFiles:
    success = {} # фальшь в случае неудачи сотворения обучающих рядов по конкретному типу свечей (записей в исходном файле свечей мало, память потекла, еще хз шо). в идеале -- все значения в словаре -- правда
    learnLine = {'in':[],'out':[]} #текущий ряд обучения. сотворили, записали в файл, сотворили новый
    candleTmp = [] #это для хранения оригиналов выхода (в структуре строчкой выше он хранится в уже размытом виде)
    candle = [0.0, 0.0, 0.0] #тени и тело свечи. пригодится при заблуривании
    roundVal = 4 #костыль для округления до нужного количества знаков после запятой. надо разобраться в чем дело
    inputLine = [] #то, что мы будем подавать на вход по завершению обучения. размерность должна совпадать с self.learnLine['in']
    encodeSize = 4 #количество символов для кодирования выходного сигнала.см def encodeVal
    

    def doLearnlogic(self,files,rules,i,learnfile,inputFile):
        #for i in files.candles: #TODO: форкать это
            self.success[i] = True
            self.cleanArrs()
            if(i in rules.candleVal): #if we got rules for current candle type
                #try: #первую пачку обучающего ряда читаем отдельно (надо будет сделать это все красивее)
                    tmp = [next(files) for x in range(rules.IOcandles['in'][i] + rules.IOcandles['out'][i])]#читаем сразу и вход, и выход
                    for j in range(rules.IOcandles['in'][i]): #записываем вход на вход
                        y = getCandleFrom(tmp[j])
                        tmp1 = self.blurCandle(y,rules, i, True) #encode IN
                        self.appVal(self.learnLine['in'], tmp1)
                        if((j - rules.IOcandles['out'][i]) >= 0): #ВАЖНО: решение исключительно для 1шт свечи на выходе 
                            self.appVal(self.inputLine, tmp1)
                    for j in range(rules.IOcandles['out'][i]): #записываем выход в выход
                        y = getCandleFrom(tmp[j + rules.IOcandles['in'][i]])
                        tmp1 = self.blurCandle(y,rules, i, False) #encode OUT
                        tmp2 = self.blurCandle(y,rules, i, True) #encode IN //проблема этого подхода в том, что будет жопа, если мы захотим предсказывать сразу несколько свечей (т.е. больше одной). в это случае следует возвратиться к мастеру(либо другим более ранним веткам)
                        self.appVal(self.inputLine, tmp2)
                        self.learnLine['out'].append(tmp1)
                    learnfile.write(str(self.learnLine['in']) + str(self.learnLine['out']) + '\n')
                    inputFile.write(str(self.inputLine) + '\n')
                #except Exception:
                    #print("слишком короткий исходный файл для свечей " + i)
                    for line in files: #теперь читаем остаток файла
                        self.delFirst(self.learnLine['in'])
                        self.updInFromInline()
                        y = getCandleFrom(line) #берем следующую свечу, и кидаем её заблуренную на віход обучающей чепочки, и на вход того, что скормим по завершению обучения
                        tmp1 = self.blurCandle(y,rules, i, False) #encode OUT
                        #self.appVal(self.learnLine['out'], tmp1)
                        self.learnLine['out'].pop(0)
                        self.learnLine['out'].append(tmp1)
                        tmp2 = self.blurCandle(y,rules, i, True) #encode IN
                        self.appVal(self.inputLine, tmp2)
                        learnfile.write(str(self.learnLine['in']) + str(self.learnLine['out']) + '\n')
                        inputFile.write(str(self.inputLine) + '\n')
                    files.seek(0) #и возвращаем(ся) к началу
            else:
                print("нет правил для свечей типа " +i)
                self.success[i] = False


    def blurCandle(self,y,rules, canletype, mode):
        #ipdb.set_trace()
        s = []
        if (mode): #хуевый костыль для необходимости (либо ее отсутсвия перевода в двоичную систему)
            self.getCandleVal(y,rules, canletype) #
            s.append(self.encodeVal(self.doBlur(self.candle[0], rules.shadowRules[canletype])))
            s.append(self.encodeVal(self.doBlur(self.candle[1], rules.bodyRules[canletype])))
            s.append(self.encodeVal(self.doBlur(self.candle[2], rules.shadowRules[canletype])))
        else: #иначе нам надо закодировать ВЫХОД () 
            #s = self.encodeOutVal(self.doBlur(self.candle[1], rules.bodyRules[canletype]))
            s = self.encodeVal(self.doBlur((round(float(y.closeVal), self.roundVal) - round(float(y.openVal),self.roundVal)), rules.bodyRules[canletype]))
        return s #format: [upahadow, body, downshadow]

    def getCandleVal(self,y,rules, canletype):
        self.candle[1] = round(float(y.closeVal),self.roundVal) - round(float(y.openVal), self.roundVal)
        if(self.candle[1] > 0): #if bull candle
            self.candle[0] = round(float(y.hightVal), self.roundVal) - round(float(y.closeVal), self.roundVal)
            #self.candle[2] = round((float(y.openVal) - float(y.lowVal)),self.roundVal)
            self.candle[2] = round(float(y.lowVal), self.roundVal) - round(float(y.openVal),self.roundVal) # попробуем так. это же, все-таки, нижняя тень
        else: #if bear candle
            self.candle[0] = round(float(y.hightVal), self.roundVal) - round(float(y.openVal),self.roundVal)
            #self.candle[2] = round((float(y.closeVal) - float(y.lowVal)),self.roundVal)
            self.candle[2] = round(float(y.lowVal), self.roundVal) - round(float(y.closeVal),self.roundVal) # аналогияно

    def doBlur(self, v, rule):
        val = round(v, self.roundVal)
        #print(val)
        for i in rule:
            if (len(rule[i]) > 1): #если у нас предел из двух значений
                if (val >= rule[i][0] and val <= rule[i][1]):
                    return i
            else: # если у нас одно значение, то оно крайнее
                if (val > 0 and rule[i][0] > 0): return i #if bull candle or we have shadow
                if (val > 0 and rule[i][0] == 0): return i #костыль для детекта самой мелкой тени минутки. TODO: переделать
                if (val < 0 and rule[i][0] < 0): return i
        print("learnFiles (doBlur): значение не смогло закодироваться " + str(val))
        print (rule)

    def encodeVal(self, v): #кодируем в двоичной системе значения до +/-7 включительно, первое место под знак
        val = (int(v) - 10) # [-10..10] -> [0..20] ==> 0 -> 10, step 2
        if (val == 0): return [0,0,0,0]
        if (val > 0):
            if (val == 1): return([0,0,0,1])
            if (val == 2): return([0,0,1,1])
            #if (val == 3): return([0,1,1,1])
            #if (val == 4): return([0,1,0,0])
            #if (val == 5): return([0,1,0,1])
            #if (val == 6): return([0,1,1,0])
            return([0,0,1,1])
        else :  #if (val > 0):
            if (val == -1): return([1,0,0,0])
            #if (val == -2): return([1,1,0,0])
            #if (val == -3): return([1,0,1,1])
            #if (val == -4): return([1,1,0,0])
            #if (val == -5): return([1,1,0,1])
            #if (val == -6): return([1,1,1,0])
            return([1,1,0,0])

    """def encodeOutVal(self, v): #кодируем в троичной системе значения выхода (10, 00, 01)
        val = (int(v) - 10) # 
        if (val == 0): return [0,0,0,0]
        if (val > 0): 
            if(val == 1): return [0,0,0,1]
            return [0,0,1,1]
        else: 
            if (val == -1): return([1,0,0,0])
            return [1,1,0,0]"""

    def cleanArrs(self):
            for k in range(len(self.learnLine['in'])): self.learnLine['in'].pop()
            for k in range(len(self.learnLine['out'])): self.learnLine['out'].pop()
            for k in range(len(self.inputLine)): self.inputLine.pop()

    def appVal(self, array, val):
        for k in range(3): #upshadow, body,downshadow
            array.append((val[k]))
            """for k in range(self.encodeSize): #self.encodeSize == len(val[0])
                array.append(str(val[0][k]) + ':' + str(val[1][k]) + ':' + str(val[2][k])) #val[0] -> upshadow, val[1] -> body, val[2] -> downshadow (binnary encoded)"""


    def delFirst(self,array):
        for k in range(3): 
            array.pop(0)
        """for k in range(self.encodeSize):
            array.pop(0)"""

    def updInFromInline(self):
        for k in range(3):
            self.learnLine['in'].append(self.inputLine.pop(0))
        """for k in range(self.encodeSize):
            self.learnLine['in'].append(self.inputLine.pop(0))"""
