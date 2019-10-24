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
            for k in range(len(self.learnLine['in'])): self.learnLine['in'].pop()
            for k in range(len(self.learnLine['out'])): self.learnLine['out'].pop()
            for k in range(len(self.inputLine)): self.inputLine.pop()
            if(i in rules.candleVal): #if we got rules for current candle type
                    tmp = [next(files) for x in range(rules.IOcandles['in'][i] + rules.IOcandles['out'][i])]#читаем сразу и вход, и выход
                    for j in range(rules.IOcandles['in'][i]): #записываем вход на вход
                        y = getCandleFrom(tmp[j]) #get one candle
                        self.getCandleVal(y,rules, i) 
                        self.learnLine['in'].append(self.blurCandle(y,rules, i, True))
                        if((j - rules.IOcandles['out'][i]) >= 0):
                            self.inputLine.append(self.blurCandle(y,rules, i, True))
                    for j in range(rules.IOcandles['out'][i]): #записываем выход в выход
                        tmpLine = tmp.pop()
                        self.candleTmp.append(tmpLine)
                        y = getCandleFrom(tmpLine)
                        tmp1 = self.blurCandle(y,rules, i, True)
                        self.learnLine['out'].append(tmp1)
                        self.inputLine.append(tmp1)
                    learnfile.write(str(self.learnLine['in']) + str(self.learnLine['out']))
                    learnfile.write('\n')
                    inputFile.write(str(self.inputLine))
                    inputFile.write('\n')
                    lineN = rules.IOcandles['in'][i] + rules.IOcandles['out'][i] #счетчик текущей линии. TODO: разобраться почему встроенные методы не хотят рабоать
                    for line in files: #теперь читаем остаток файла, и реализуем FIFO
                        lineN +=1
                        y = getCandleFrom(self.candleTmp[0]) #на вход берем из темпарей сверху, потому как прочитан и вход, и выход. лень скакать туда-сода по файлу, та и долго это
                        del self.candleTmp[0] #удаляем за ненадобностью
                        self.candleTmp.append(line) #засовываем свежепрочитанную (сначала она пойдёт на выход, а потом (спустя итераций range(rules.IOcandles['out'][i]) -- на вход))
                        del self.learnLine['in'][0] #вход тоже передвигаем по истории на одну свечу (для справки: степень достоверности на этом этапе уже не имеет значения)
                        self.getCandleVal(y,rules, i)
                        self.learnLine['in'].append(self.blurCandle(y,rules, i, True))
                        y = getCandleFrom(line) #берем следующую свечу, и кидаем её заблуренную на віход обучающей чепочки, и на вход того, что скормим по завершению обучения
                        del self.learnLine['out'][0] #выход тоже передвигаем по истории на одну свечу (для справки: степень достоверности на этом этапе уже не имеет значения)
                        tmp1 = self.blurCandle(y,rules, i, True)
                        self.learnLine['out'].append(tmp1)
                        del self.inputLine[0]
                        self.inputLine.append(tmp1)
                        learnfile.write(str(self.learnLine['in']) + str(self.learnLine['out']))
                        inputFile.write(str(self.inputLine))
                        inputFile.write('\n')
                        learnfile.write('\n')
            else:
                print("нет правил для свечей типа " +i)
                self.success[i] = False


    def blurCandle(self,y,rules, canletype, mode):
        #ipdb.set_trace()
        s = []
        self.getCandleVal(y,rules, canletype) #
        if (mode): #хуевый костыль для необходимости (либо ее отсутсвия перевода в двоичную систему)
            s.append(self.encodeVal(self.doBlur(self.candle[1], rules.bodyRules[canletype])))
        else: 
            s.append(self.doBlur(self.candle[1], rules.bodyRules[canletype]))
        return s

    def getCandleVal(self,y,rules, canletype):
        self.candle[1] = round((float(y.closeVal) - float(y.openVal)), self.roundVal)
        if(self.candle[1] > 0): #if bull candle
            self.candle[0] = round((float(y.hightVal) - float(y.closeVal)), self.roundVal)
            self.candle[2] = round((float(y.openVal) - float(y.lowVal)),self.roundVal)
        else: #if bear candle
            self.candle[0] = round((float(y.hightVal) - float(y.openVal)),self.roundVal)
            self.candle[2] = round((float(y.closeVal) - float(y.lowVal)),self.roundVal)

    def doBlur(self, v, rule):
        val = round(v, self.roundVal)
        for i in rule:
            if (len(rule[i]) > 1): #если у нас предел из двух значений
                if (val >= rule[i][0] and val <= rule[i][1]):
                    return i
            else: # если у нас одно значение, то оно крайнее
                if (val > 0 and rule[i][0] > 0): return i #if bull candle or we have shadow
                if (val > 0 and rule[i][0] == 0): return i #костыль для детекта самой мелкой тени минутки. TODO: переделать
                if (val < 0 and rule[i][0] < 0): return i
        print("значение не смогло закодироваться " + str(val))
        print (rule)

    def encodeVal(self, v): #кодируем в двоичной системе значения до +/-7 включительно, первое место под знак
        val = (int(v) - 10) # [-10..10] -> [0..20] ==> 0 -> 10, step: 2
        if (val == 0): return [0,0,0,0]
        if (val > 0):
            if (val == 1): return([0,0,0,1])
            if (val == 2): return([0,0,1,0])
            if (val == 3): return([0,0,1,1])
            if (val == 4): return([0,1,0,0])
            if (val == 5): return([0,1,0,1])
            if (val == 6): return([0,1,1,0])
            return([0,1,1,1])
        else :  #if (val > 0):
            if (val == -1): return([1,0,0,1])
            if (val == -2): return([1,0,1,0])
            if (val == -3): return([1,0,1,1])
            if (val == -4): return([1,1,0,0])
            if (val == -5): return([1,1,0,1])
            if (val == -6): return([1,1,1,0])
            return([1,1,1,1])
        

