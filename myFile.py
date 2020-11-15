import itertools
import os
import random

class myFile:
    source = {'candlepath':'', 'logpath':'', 'pretext':'','f':False} #путь, название, и переменная исходного файла (здесь и везде: название исходного файла идентично с аббревиатурой валютной пары)
    QfilePath = {} #файлы со свечками
    Qfiles = {} #переменные файлов со свечками
    InputFilePath = {} # ANN input 4 predict
    InputFiles = {} #ANN input 4 predict
    SynFilePatn = {} #пути файлов с синапсами
    SynFiles = {} #переменные файлов с синапсами
    LearnfilePath = {} #файлы с обучающими цепочками
    Learniles = {} #переменные файлов с обучающими цепочками
    CurFileData = {} #данные текущего файла (попробуем читать всё в память)
    #StatFilePath = {} #файлы статистики
    #StatFiles = {} # переменные файлов статистики
    TmpFilePath = {} #временные файлы, куда мы заполняем пробелы
    TmpFiles = {} # переменные этих временных файлов
    candles = ['minFile','min5File','min15File','min30File','hourFile','hour4File','dayFile','weekFile','monthFile'] #названия свечек. добавляется к названию файла
    candles_enc = {'minFile':1,'min5File':5,'min15File':15,'min30File':30,'hourFile':60,'hour4File':240,'dayFile':1440,'weekFile':10080,'monthFile':43200} #названия файлов свечей, получаемых из мт4
    LearnLogF = open("log", "w")#логи обучения


    def __init__(self, currency = 'USDJPY'):
        path = os.getcwd()
        os.chdir(currency + '_MT4')
        self.source['pretext'] = currency
        for i in self.candles:
            self.QfilePath[i] = currency + str(self.candles_enc[i]) + ".txt"
            self.TmpFilePath[i] = self.fileCreate(currency + '_' + i + ".txt")
            try:
                if(self.QfilePath[i] != ''):
                    self.Qfiles[i] = open(self.QfilePath[i], 'r')
                    self.TmpFiles[i] = open(self.TmpFilePath[i], 'a+')
                else:
                    self.TmpFilePath[i] = ''
            except Exception:
                print("ошибка отрывания файла " + self.QfilePath[i])
                self.QfilePath[i] = '' #таким образом мы знаем которых файлов нету
                #os.chdir(path)
        os.chdir(path)



   
    def learnInit(self, br, cfg = 'config.txt', currency = 'USDJPY'):
        self.source['candlepath'] = self.source['pretext'] = currency
        #path = os.getcwd()
        #print (path)
        try:
            self.LearnLogF.close()
            self.LearnLogF = open(currency + '_learn_log','w')
        except Exception:
            print("не удалось создать файл логов обучения")
        try:
            f = open(cfg,'r')
            z = f.readline()
            z = z[0:len(z)-1] #некрасивое удаление знака конца строки. переделать
            self.source['candlepath'] = self.source['pretext'] = str(z)
            #self.getSourceCandles(self.source['candlepath'])
            self.dircreate(self.source['candlepath'] + 'learning', 'candlepath') #сюда складываем всё, что нужно для обучения и прогнозирования
            #self.dircreate(self.source['candlepath'] + 'learning' + 'synapse', 'candlepath') #сюда складываем всё, что нужно для обучения и прогнозирования
            self.makeLearnFiles(self.source['candlepath'])
            itertools.islice(f,1)
            for line in f:
                br.getCandleRuleFromString(line)
        except Exception:
            print ("ошибка конфига. убедитесь, что файл %s существует (и желательно не пуст).", cfg)
            self.myShutdowm()
        

    def makeLearnFiles(self,currency):
        path = os.getcwd()
        os.chdir(currency)
        for i in self.candles:
            self.LearnfilePath[i] = self.fileCreate(self.source['pretext'] + "_learn_" + i + ".txt")
            self.InputFilePath[i] = self.fileCreate(self.source['pretext'] + '_input_' + i + ".txt")
            self.SynFilePatn[i] = self.source['pretext'] + '_syn_' + i + ".npz"
            try:
                self.Learniles[i] = open(self.LearnfilePath[i], 'a+')
                self.InputFiles[i] = open(self.InputFilePath[i], 'a+')
            except Exception:
                print ("ошибка открытия файл " + self.LearnfilePath[i])
                self.myShutdowm()
        os.chdir(path)

    def myShutdowm(self):
        for i in self.candles:
            if(i in self.Qfiles): self.Qfiles[i].close()
            if(i in self.InputFiles): self.InputFiles[i].close()
            #if(i in self.StatFiles): self.StatFiles[i].close()
            if(i in self.Learniles): self.Learniles[i].close()
        self.source['pretext'] = ''
        self.LearnLogF.close()

    def dircreate(self, s,ind):
        path = os.getcwd()
        path = path + "\\" + s
        try:
            self.source[ind] = path
            os.makedirs(path)
        except OSError:
            if(os.path.isdir(path)):return
            print ("Создать директорию %s не удалось" % path)
        
    def takeFromCfg(self):
        try:
            f = open('config.txt','r')
            z = f.readline()
            z = z[0:len(z)-1] #некрасивое удаление знака конца строки. переделать
            self.source['candlepath'] = self.source['pretext'] = str(z)
            self.dircreate(self.source['candlepath'], 'candlepath')
            return self
        except Exception:
            print ("ошибка конфига. убедитесь, что файл 'config.txt' существует (и желательно не пуст).")
            self.myShutdowm()
    
    def fileCreate(self, s):
        try:
            f = open(s,'w')
            f.close()
            return s
        except Exception:
            print ("ошибка попытки создания\перезаписи файла " + s)
            #self.myShutdowm()
            return ''

    def getStatFiles(self, candlefiles):
        for i in self.candles:
            try:
                self.Qfiles[i] = open(candlefiles.QfilePath[i], 'r') #теперь, когда уже все сделано, мы открываем файлы на чтение для сбора статистики значений свечей за весь период
            except Exception:
                print ("ошибка открытия файл " + candlefiles.QfilePath[i])
                self.myShutdowm()
                candlefiles.myShutdowm()
            try:
                self.StatFilePath[i] = self.fileCreate(candlefiles.source['pretext'] + "_stat_" + i + ".txt") #сюда складывать будем статистику значений
            except Exception:
                print ("создания файла статистики " + candlefiles.QfilePath[i])
                self.myShutdowm()
                candlefiles.myShutdowm()
            try:
                self.StatFiles[i] = open(self.StatFilePath[i], 'a') #и открываем на дозапись
            except Exception:
                print ("ошибка открытия файл " + self.StatFilePath[i])
                self.myShutdowm()
                candlefiles.myShutdowm()
        return self

    def getData(self, f,  outnorm = 0):
        f.seek(0)
        self.CurFileData = f.readlines()
        f.seek(0) #на всякий случай. мало ли кто еще захочет его прочесть 
        if(outnorm == 0): return # mission: complete
        #TODO: всё нижеследующее пристроить куда-нить в более подобающее место
        norm = len(self.CurFileData) / outnorm #эталон количества штук одного выхода
        random.shuffle(self.CurFileData) #добавим немного рандома
        out = {} #все наши имеющиеся возможные выходы будут здесь пока мы их считаем и нормализируем
        const = float(0.341) #константа из задачи трёх сигм -- отклонение от середины, самая вероятная зона. NOTE: тут может быть любое другое значение, если я получу на то достаточно обоснования
        for line in self.CurFileData: #сначала соберем статистику что у нас есть
            tmp = line.split('][')
            if(tmp[1] in out): out[tmp[1]] = out[tmp[1]] + 1
            else: out[tmp[1]] = 1        
        #if(outnorm > (len(out))): print("WARING: learn data has " + str(len(out)) + " candles of " + str(outnorm)) # значит данные для обучения не полные. нужно непременно об этом сообщить
        tmp1 = [] #здесь будут временно жить нормализированные данные для обучения
        for line in self.CurFileData: # теперь уберём всё лишнее
            tmp = line.split('][')
            if((out[tmp[1]] + out[tmp[1]] * const) < norm): tmp1.append(line) #если выход лежит ниже верхней границы отклонения -- просто добавим его в обучающую цепочку
            else: 
                tmp2 = random.randint(0,out[tmp[1]]) # добавим ещё немного рандома: если данных выходов слишком много, то будем брать только те, у которых есть удача ;) 
                if(tmp2 < norm): 
                    tmp1.append(line)
                    #print('happy')
        random.shuffle(tmp1) #добавим ещё немного рандома
        tmp3 = []
        for line in tmp1: #теперь прибавим тех, кого слишком мало
            tmp = line.split('][')
            if((out[tmp[1]] - out[tmp[1]] * const) > norm): continue # если количество выходов выцше нижней границы -- не надо ничего делать
            #но если таких выходов слишком мало, то надо будет их добавить 
            tmp2 = int(norm - out[tmp[1]]) #очень просто посчитать сколько еще таких надо добавить 
            out[tmp[1]] = out[tmp[1]] + tmp2 #и сразу же меняем счетчик, чтобы избежать повторного добавления"""
            while (tmp2 > 0): #пока мы не добавили всё, что надо
                    random.shuffle(tmp1) #добавим немного рандома перед каждым прохождением обучающего массива
                    for line1 in tmp1: #мы идём по всему массиву обучения
                        if (tmp2 == 0): break
                        tmptmp = line1.split('][')
                        if (tmptmp[1] == tmp[1]):  #находим, и добавляем из него примеры по подному
                            tmp3.append(line1)
                            tmp2 = tmp2 - 1 # и уменьшаем количество тех, что нужно ещё добавить
        #print('rows: ' + str(len(self.CurFileData)) + ' -> ' + str(len(tmp1)) + ' + ' +  str(len(tmp3)) + ' = ' + str(len(tmp1) + len(tmp3)))
        random.shuffle(tmp3) #добавим ещё немного рандома
        for line in tmp3: 
            tmp1.append(line) #просто дописываем в конец
        random.shuffle(tmp1) #и перемешиваем
        self.CurFileData = tmp1 #в конце получаем чудесные нормализированные(от слова "Гаусс", а не от от слова "нормаль") данные для обучения
        del out
        del tmp1
        del tmp3
                

                
        

