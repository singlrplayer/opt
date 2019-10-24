import os

class candleValues:
    openVal = {}
    closeVal = {}
    hightVal = {}
    lowVal = {}
    candles = ['min','5min', '15min', '30min', 'hour', '4hour', 'day', 'week', 'month'] #типы свечей. не трогать. TODO: переделать их так, чтоб брать из конфига. переделать во всех местах 
    candleVal = ['open','close','hight','low','auth'] #первые четыре параметра, характеризирующие одну (каждую) свечку. не трогать. последний параметр характеризирует подлинность свечки (0 значит подлинный)
    candle_tmp = {} #структура следующая: для каждой свечи (типы свечей две строчки выше) записываем временно значения более мелких(читать "быстрых") свечек, чтоб потом из полученного подобия массива взять минимум\максимум для теней, и открытие\закрытие с первой\послейней мелкой свечки. значения пишем по всем четырем параметрам (см строчку выше)


    def myInit (self, y):
        for i in self.candles:
            self.openVal[i] = y.openVal
            self.closeVal[i] = y.closeVal
            self.hightVal[i] = y.hightVal
            self.lowVal[i] = y.lowVal
            self.candle_tmp[i] = {}
            for j in self.candleVal:
                self.candle_tmp[i][j] = []
        return self

    def updVal(self,a,b,c,d,i):
        try:
            self.openVal[self.candles[i]] = a
            self.closeVal[self.candles[i]] = b
            self.hightVal[self.candles[i]] = c
            self.lowVal[self.candles[i]] = d
            
        except Exception:
            print ("свечи бывают такие: ['min','5min', '15min', '30min', 'hour', '4hour', 'day', 'week', 'month'], а ты просишь такую: "+ str(self.candles[i]))
            print (Exception)

    def updateTMP(self,j): #тут свежеполученную свечку добавляем в темпари (из которых потом делаем следующую), и очищаем значения текущей
                auth = len(self.candle_tmp[self.candles[j]]['auth']) - self.candle_tmp[self.candles[j]]['auth'].count(0) #количество меньших свечей с ошибками (отымается количество аутентичных от количества общего)
                countAuth = 0
                for k in range(len(self.candle_tmp[self.candles[j]]['auth'])):
                    if (j == 1): #исключение для пятиминутных свечей: в минутных аутентификация равна если не нулю, то текущему номеру в последовательности минутой свечи, заполняющей пробел в исходных данных
                        if(self.candle_tmp[self.candles[j]]['auth'][k] > 0 ): countAuth =  countAuth + 1 #TODO: переделать нафиг
                    else:
                        countAuth =  countAuth + self.candle_tmp[self.candles[j]]['auth'][k]
                self.candle_tmp[self.candles[j+1]]['open'].append(self.openVal[self.candles[j]]) #TODO переделать всё к черту в едином стиле пока сама еще понимаю
                self.candle_tmp[self.candles[j+1]]['close'].append(self.closeVal[self.candles[j]]) #TODO переделать всё к черту в едином стиле пока сама еще понимаю
                self.candle_tmp[self.candles[j+1]]['hight'].append(self.hightVal[self.candles[j]]) #TODO переделать всё к черту в едином стиле пока сама еще понимаю
                self.candle_tmp[self.candles[j+1]]['low'].append(self.lowVal[self.candles[j]]) #TODO переделать всё к черту в едином стиле пока сама еще понимаю
                for k in self.candleVal:
                    self.candle_tmp[self.candles[j]][k] = []
                self.candle_tmp[self.candles[j+1]]['auth'].append(countAuth)
                if(auth == 0):pr = '' #синяя изолента, помогающая парсить получаемый файл глазками: порядка overk10 лямов гребанных строк
                else: pr = str(auth) + ' ' + str(countAuth) + ' '
                return pr # '' if candle original :)

    def updatePrefix(self, s, j): #синяя изолента, помогающая парсить получаемый файл глазками: порядка 6 лямов гребанных строк
        try:
            i = s.index(" ",0,len(s))
            if (i == -1): return s
            s = s[i+1:len(s)]
            s = str(j) + ' ' + s
            return s
        except Exception:
            print("prefix exception " +s)
            return s


    def updateMe(self, y, ind, files, flag): #TODO: убедиться в работоспособности и переписать всё правильно. помумать на счет красивого решения месячных и годовых свечей
        #try: #ВАЖНО: во всех свечах, за исключением минутных пишется дата\время ёё закрытия, а не открытия
            pr = ' '
            """if(flag): # flag == False, если свеча подлинная, и flag == True, если на этом месте есть дыра в исходных минутніх данных
                files.Logfiles['minFile'].write("incerted time " + str (y.olddata['oldtime'])+" at " + str(y.olddata['olDopenVal']) + ",   line " + str(ind) + "\n")
                if(y.candle['auth'] == 1) : pr = str(y.candle['auth']) + ' '
                else : pr = self.updatePrefix(pr, y.candle['auth'])"""
            self.updVal(y.openVal, y.closeVal, y.hightVal, y.lowVal,0) #5-й аргумент является индексом вот этой штуки ['min','5min', '15min', '30min', 'hour', '4hour', 'day', 'week' 'month']
            #print(files)
            files.write(str(pr) + str(y.olddata['olddate'])+','+ str(y.olddata['oldtime'])+','+str(y.olddata['olDopenVal'])+','+str(y.olddata['olDhightVal'])+','+str(y.olddata['olDlowVal'])+','+str(y.olddata['olDcloseVal'])+'\n') #последовательность записи значений в файл важна!!!!!!!!!
            """for j in self.candleVal:
                self.candle_tmp['5min'][j].append(y.candle[j]) #добавляем значений во все свечи
            #if (ind < 1): return
            if (not ind%5):# пришло время делать пятиминутную свечку из пяти штук минутных
                self.updVal(self.candle_tmp['5min']['open'][0],self.candle_tmp['5min']['close'][4],max(self.candle_tmp['5min']['hight']), min(self.candle_tmp['5min']['low']),1)
                pr = self.updateTMP(1) # 1 means '5min'
                files.Qfiles['min5File'].write(pr + y.cur+','+str(y.olddata['olddate'])+','+ str(y.olddata['oldtime'])+','+str(self.openVal['5min'])+','+str(self.hightVal['5min'])+','+str(self.lowVal['5min'])+','+str(self.closeVal['5min'])+','+str(y.lineEnd)) #последовательность записи значений в файл важна!!!!!!!!!
            if (not ind%15): # пришло время делать четвертную свечку из трех штук пятиминутных
                self.updVal(self.candle_tmp['15min']['open'][0],self.candle_tmp['15min']['close'][2],max(self.candle_tmp['15min']['hight']), min(self.candle_tmp['15min']['low']),2)
                pr = self.updateTMP(2) # 2 means '15min'
                files.Qfiles['min15File'].write(pr + y.cur+','+str(y.olddata['olddate'])+','+ str(y.olddata['oldtime'])+','+str(self.openVal['15min'])+','+str(self.hightVal['15min'])+','+str(self.lowVal['15min'])+','+str(self.closeVal['15min'])+','+str(y.lineEnd)) #последовательность записи значений в файл важна!!!!!!!!!
            if (not ind%30): # пришло время делать получасовую свечку из двух штук чертветных
                self.updVal(self.candle_tmp['30min']['open'][0],self.candle_tmp['30min']['close'][1],max(self.candle_tmp['30min']['hight']), min(self.candle_tmp['30min']['low']),3)
                pr = self.updateTMP(3) # 3 means '30min'
                files.Qfiles['min30File'].write(pr + y.cur+','+str(y.olddata['olddate'])+','+ str(y.olddata['oldtime'])+','+str(self.openVal['30min'])+','+str(self.hightVal['30min'])+','+str(self.lowVal['30min'])+','+str(self.closeVal['30min'])+','+str(y.lineEnd)) #последовательность записи значений в файл важна!!!!!!!!!
            if(not ind%60): # пришло время делать часовую свечку из двух штук получасовых
                self.updVal(self.candle_tmp['hour']['open'][0],self.candle_tmp['hour']['close'][1],max(self.candle_tmp['hour']['hight']), min(self.candle_tmp['hour']['low']),4)
                pr = self.updateTMP(4) # 4 means 'hour'
                files.Qfiles['hourFile'].write(pr + y.cur+','+str(y.olddata['olddate'])+','+ str(y.olddata['oldtime'])+','+str(self.openVal['hour'])+','+str(self.hightVal['hour'])+','+str(self.lowVal['hour'])+','+str(self.closeVal['hour'])+','+str(y.lineEnd)) #последовательность записи значений в файл важна!!!!!!!!!
            if(not ind%240):# пришло время делать четырехчасовую свечку из четырех штук часовых
                self.updVal(self.candle_tmp['4hour']['open'][0],self.candle_tmp['4hour']['close'][3],max(self.candle_tmp['4hour']['hight']), min(self.candle_tmp['4hour']['low']),5)
                pr = self.updateTMP(5) # 5 means '4hour'
                files.Qfiles['hour4File'].write(pr + y.cur+','+str(y.olddata['olddate'])+','+ str(y.olddata['oldtime'])+','+str(self.openVal['4hour'])+','+str(self.hightVal['4hour'])+','+str(self.lowVal['4hour'])+','+str(self.closeVal['4hour'])+','+str(y.lineEnd)) #последовательность записи значений в файл важна!!!!!!!!!
            if(not ind%1440):# пришло время делать дневную свечку из шести штук четырехчасовых
                self.updVal(self.candle_tmp['day']['open'][0],self.candle_tmp['day']['close'][5],max(self.candle_tmp['day']['hight']), min(self.candle_tmp['day']['low']),6)
                pr = self.updateTMP(6) # 6 means 'day'
                files.Qfiles['dayFile'].write(pr + y.cur+','+str(y.olddata['olddate'])+','+ str(y.olddata['oldtime'])+','+str(self.openVal['day'])+','+str(self.hightVal['day'])+','+str(self.lowVal['day'])+','+str(self.closeVal['day'])+','+str(y.lineEnd)) #последовательность записи значений в файл важна!!!!!!!!!
            if(not ind%10080):# пришло время делать недельную свечку из семи штук дневных
                self.updVal(self.candle_tmp['week']['open'][0],self.candle_tmp['week']['close'][6],max(self.candle_tmp['week']['hight']), min(self.candle_tmp['week']['low']),7)
                pr = self.updateTMP(7) # 7 means 'week'
                files.Qfiles['weekFile'].write(pr + y.cur+','+str(y.olddata['olddate'])+','+ str(y.olddata['oldtime'])+','+str(self.openVal['week'])+','+str(self.hightVal['week'])+','+str(self.lowVal['week'])+','+str(self.closeVal['week'])+','+str(y.lineEnd)) #последовательность записи значений в файл важна!!!!!!!!!"""
            
       # except Exception:
        #    if (ind == 0): return #TODO придумать что-то другое
         #   print ("непонятная ошибка в обновлении свечей в строке почучаемого минутного файла " + str(ind))
          #  print (Exception)
    
                
