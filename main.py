from myFile import myFile
from blurRules import blurRules
from learnFiles import learnFiles
from candlecreate import candlecreate
import time

import numpy as np

############ ANN turing machine part ;)
def nonlin(x,deriv=False):
    if(deriv==True):
        return x*(1-x)
    return 1/(1+np.exp(-x))

def learn(br, syn0, syn1):
    output = {}
    layer0 = np.array(br.learnArrayIn)
    layer1 = nonlin(np.dot(layer0,syn0))
    layer2 = nonlin(np.dot(layer1,syn1))
    layer2_error = np.array(br.learnArrayOut) - layer2 #common output ERR
    layer2_delta = layer2_error*nonlin(layer2,deriv=True)
    layer1_error = layer2_delta.dot(syn1.T)
    layer1_delta = layer1_error * nonlin(layer1,deriv=True)
    syn1 += layer1.T.dot(layer2_delta)
    syn0 += layer0.T.dot(layer1_delta)
    output['syn0'] = syn0 #для продолжения обучения
    output['syn1'] = syn1 #для продолжения обучения
    output['layer2'] = layer2 #для понимания хода обучения
    output['err'] = np.mean(np.abs(layer2_error)) #для понимания хода обучения
    return output

def getpredict(br, syn0, syn1,s1 = '',s2 = ''):
        layer0 = np.array(br.arrayIn)
        #print(layer0)
        layer1 = nonlin(np.dot(layer0,syn0))
        layer2 = nonlin(np.dot(layer1,syn1))
        print(s1)
        print(layer2)
        print(s2)
        return layer2
    
###########

f = myFile('AUDUSD') #инициация файлов экспорта мт4
f_predict = open("redict.txt",'w') #файл с предсказаниями сети
f_predict.write(str(time.ctime(time.time())) + '\n')
f_predict.write(str(f.source['pretext']) + '\n')
f_predict.close()
print("get source:")
for i in f.candles: print(f.QfilePath[i])
br = blurRules() #правила сглаживания
lf = learnFiles() #логика обучающих файлов
f.learnInit(br, 'config.txt', 'AUDUSD') #инициализация обучающих файлов по конкретной валютной паре
mytime = {}#время старта обучения по каждой модели свеч
learnCount = {'minFile':5,'min5File':5,'min15File':10,'min30File':10,'hourFile':10,'hour4File':10,'dayFile':10,'weekFile':10,'monthFile':10} #количество циклов обучения в пачке данных lines для каждой свечки 
ANN = {} #ANN params

print("start creating rows and learning")
f_predict = open("predict.txt",'a')
######## надо будет это форкать по всем типам свечей
for i in f.candles: 
    print (i)
    if(f.QfilePath[i] != ''): #если есть исходный файл нужной нам свечки
        mytime[i] = time.time()
        f1 = candlecreate(f.Qfiles[i], f.TmpFiles[i], int(f.candles_enc[i])) #делаем свечки без пробелов в данных
        f.TmpFiles[i].seek(0)
        lf.doLearnlogic(f.TmpFiles[i], br, i, f.Learniles[i], f.InputFiles[i])#делаем обучающие файлы
        f.Learniles[i].seek(0)
        #f.getData(f.InputFiles[i]) #не забыть забрать отсбюда нафиг       
        f.getData(f.Learniles[i])
        print("---rows created at %s seconds ---" % (time.time() - mytime[i])) 
        print("learn")
        try: #пытаемся взять из файла готовые синапсы с прошлого обучения
            syns = np.load(f.SynFilePatn[i])
            ANN['syn0'] = syns['syn0']
            ANN['syn1'] = syns['syn1']
            syns.close()
            #print(syn0)
            #print(syn1)
            print("got synapses from file")
        except Exception:
            ANN['syn0'] = 2*np.random.random((br.IOcandles['in'][i]*3, lf.encodeSize * br.IOcandles['in'][i])) - 1 #in
            ANN['syn1'] = 2*np.random.random((lf.encodeSize * br.IOcandles['in'][i], br.IOcandles['out'][i])) - 1 #out
            print("synapse file reading error. new synapses created")
        #f_predict.write(str(i) + '\n')
        ######---------start learn
        ANN['err'] = maxErr = 1 #максимальная ошибка в ходе обучения за данный цикл
        startpos = 0
        startpos = br.createLearnArray( f.CurFileData, startpos)#three means [0]->upshadow, [1] -> boady, [2] -> downshadow
        f.LearnLogF.write(str(i) + '\n')
        #print(syn0)
        #print(syn1)        
        output = np.array(br.learnArrayOut)
        #print(np.array(br.learnArrayIn))
        #print(output)
        for mainLearnCycle in range(learnCount[i] * 1500): # цикл, в котором идём по всему файлу обучения пачками по 1 строк
            for learncycle in range(learnCount[i]):
                if (len(br.learnArrayIn)>0):
                    ANN = learn(br, ANN['syn0'], ANN['syn1'])
                    if ((mainLearnCycle % 500 == 0) and (learncycle% 10) == 0):
                        print ("ANN predict forex error:" + str(ANN['err']))
            #######
            while (startpos != -1): #этот кусок необходим, если в обучающем файле больше строк, нежели 1. обучение проходит пачками на тех же синапсах. ВАЖНО: шейпы синапсов зависят от linesCount[i]

                startpos = br.createLearnArray(f.CurFileData, startpos)
                if(startpos == -1): break #get it out
                for learncycle in range(learnCount[i]):
                    if (len(br.learnArrayIn)>0):
                        ANN = learn(br, ANN['syn0'], ANN['syn1'])
                        if ((mainLearnCycle % 1000 == 0) and (startpos% 100 == 0) and (learncycle == 0)):
                            print("mainLearnCycle: " + str(mainLearnCycle) + ", position: " + str(startpos) + ", learncycle: " + str(learncycle) + " --> ANN predict forex error:" + str(ANN['err']))
                            print(ANN['layer2'])
                            print(br.learnArrayOut)
            startpos = 0
        np.savez(f.SynFilePatn[i], syn0 = ANN['syn0'], syn1 = ANN['syn1']) #сохраняем синапсы в файл с синапсами
        ######----------end learn
        f.InputFiles[i].seek(0)
        f.getData(f.InputFiles[i])        
        br.createInputArray(f.CurFileData)# get input row 4 predict
        predict = getpredict(br, ANN['syn0'], ANN['syn1'], "-------------PREDICT-------------")
        f_predict.write("\npredict:\n")
        np.savetxt(f_predict,predict) #сохраняем предсказание в файл предсказаний
        f_predict.write("\nlearning time: " + str(int((time.time() - mytime[i]) / 60) + 1) + ' min\n---------------------------------\n')
        br.updInputArray(predict) #
        predict = getpredict(br, ANN['syn0'], ANN['syn1'], "-------------next one-----------", "---------------END---------------\n---learning time "  + str(int((time.time() - mytime[i]) / 60) + 1) +  " min ---")
    else:
        f.TmpFilePath = f.QfilePath[i]
########
f_predict.close()
f.myShutdowm()
