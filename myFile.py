import itertools
import os

class myFile:
    source = {'candlepath':'', 'logpath':'', 'pretext':'','f':False} #путь, название, и переменная исходного файла (здесь и везде: название исходного файла идентично с аббревиатурой валютной пары)
    QfilePath = {} #файлы со свечками
    Qfiles = {} #переменные файлов со свечками
    InputFilePath = {} # ANN input 4 predict
    InputFiles = {} #ANN input 4 predict
    LearnfilePath = {} #файлы с обучающими цепочками
    Learniles = {} #переменные файлов с обучающими цепочками
    CurFileData = {} #данные текущего файла (попробуем читать всё в память)
    #StatFilePath = {} #файлы статистики
    #StatFiles = {} # переменные файлов статистики
    TmpFilePath = {} #временные файлы, куда мы заполняем пробелы
    TmpFiles = {} # переменные этих временных файлов
    candles = ['minFile','min5File','min15File','min30File','hourFile','hour4File','dayFile','weekFile','monthFile'] #названия свечек. добавляется к названию файла
    candles_enc = {'minFile':1,'min5File':5,'min15File':15,'min30File':30,'hourFile':60,'hour4File':240,'dayFile':1440,'weekFile':10080,'monthFile':43200} #названия файлов свечей, получаемых из мт4
    LearnLogF = '' #логи обучения


    def __init__(self, currency = 'USDJPY'):
        path = os.getcwd()
        os.chdir(currency + '_MT4')
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
            self.LearnLogF = open(currency + '_learn_log','w')
        except Exception:
            print("не удалось создать файл логов обучения")
        try:
            f = open(cfg,'r')
            z = f.readline()
            z = z[0:len(z)-1] #некрасивое удаление знака конца строки. переделать
            self.source['candlepath'] = self.source['pretext'] = str(z)
            #self.getSourceCandles(self.source['candlepath'])
            self.dircreate(self.source['candlepath'] + 'learning', 'candlepath')
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
            self.InputFilePath[i] = self.fileCreate(currency + '_input_' + i + ".txt")
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
            #self.QfilePath[i] = ''
            #self.LogfilePath[i] = ''
        #self.source['f'].close()
        self.source['pretext'] = ''

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

    def getData(self, file):
        self.CurFileData = file.readlines()
                
        

