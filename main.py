from myFile import myFile
from myParsLine import getCandleFrom
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
###########

f = myFile('AUDUSD') #инициация файлов экспорта мт4
f_predict = open("redict.txt",'w') #файл с предсказаниями сети
f_predict.write(str(time.ctime(time.time())) + '\n')
f_predict.write(str(f.source['pretext']) + '\n')
f_predict.close()
print("get source:")
for i in f.candles:
    print(f.QfilePath[i])
br = blurRules() #правила сглаживания
lf = learnFiles() #логика обучающих файлов
f.learnInit(br, 'config.txt', 'AUDUSD') #инициализация обучающих файлов по конкретной валютной паре
mytime = {}#время старта обучения по каждой модели свеч
learnCount = {'minFile':5,'min5File':5,'min15File':10,'min30File':10,'hourFile':10,'hour4File':10,'dayFile':10,'weekFile':10,'monthFile':20} #количество циклов обучения в пачке данных lines для каждой свечки 

print("start creating rows and learning")
######## надо будет это форкать по всем типам свечей
for i in f.candles: 
    print (i)
    if(f.QfilePath[i] != ''): #если есть исходный файл нужной нам свечки
        f_predict = open("redict.txt",'a')
        mytime[i] = time.time()
        f1 = candlecreate(f.Qfiles[i], f.TmpFiles[i], int(f.candles_enc[i])) #делаем свечки без пробелов в данных
        f.TmpFiles[i].seek(0)
        lf.doLearnlogic(f.TmpFiles[i], br, i, f.Learniles[i], f.InputFiles[i])#делаем обучающие файлы
        f.Learniles[i].seek(0)
        f.getData(f.InputFiles[i]) #не забыть забрать отсбюда нафиг       
        f.getData(f.Learniles[i])
        print("---rows created at %s seconds ---" % (time.time() - mytime[i])) 
        print("learn")
        #f_predict.write(str(i) + '\n')
        ######---------start learn
        startpos = 0
        startpos = br.createLearnArray(br.IOcandles['in'][i] * 4, br.IOcandles['out'][i] * 4, f.CurFileData, startpos, 3)#three means [0]->upshadow, [1] -> boady, [2] -> downshadow
        f.LearnLogF.write(str(i) + '\n')
        syn0 = 2*np.random.random((br.IOcandles['in'][i], lf.encodeSize * br.IOcandles['in'][i])) - 1 #in
        syn1 = 2*np.random.random((lf.encodeSize * br.IOcandles['in'][i], br.IOcandles['out'][i])) - 1 #out
        print(syn0)
        print(syn1)        
        output = np.array(br.learnArrayOut)
        print(np.array(br.learnArrayIn))
        print(output)
        for mainLearnCycle in range(learnCount[i] * 350): # цикл, в котором идём по всему файлу обучения пачками по 1 строк
            for learncycle in range(learnCount[i]):
                if (len(br.learnArrayIn)>0):
                    layer0 = np.array(br.learnArrayIn)
                    layer1 = nonlin(np.dot(layer0,syn0))
                    layer2 = nonlin(np.dot(layer1,syn1))
                    layer2_error = np.array(br.learnArrayOut) - layer2 #common output ERR
                    if ((mainLearnCycle % 500 == 0) and (learncycle% 10) == 0):
                        print ("ANN predict forex error:" + str(np.mean(np.abs(layer2_error))))
                    layer2_delta = layer2_error*nonlin(layer2,deriv=True)
                    layer1_error = layer2_delta.dot(syn1.T)
                    layer1_delta = layer1_error * nonlin(layer1,deriv=True)
                    syn1 += layer1.T.dot(layer2_delta)
                    syn0 += layer0.T.dot(layer1_delta)
            #######
            while (startpos != -1): #этот кусок необходим, если в обучающем файле больше строк, нежели 1. обучение проходит пачками на тех же синапсах. ВАЖНО: шейпы синапсов зависят от linesCount[i]
                for j in range(len(br.learnArrayIn)):
                    br.learnArrayIn.pop()# input ANN array cleaning
                    br.learnArrayOut.pop()# output ANN array cleaning
                startpos = br.createLearnArray(br.IOcandles['in'][i] * 4, br.IOcandles['out'][i] * 4, f.CurFileData, startpos, 3)
                if(startpos == -1): break #get it out
                for learncycle in range(learnCount[i]):
                    if (len(br.learnArrayIn)>0):
                        layer0 = np.array(br.learnArrayIn)
                        layer1 = nonlin(np.dot(layer0,syn0))
                        layer2 = nonlin(np.dot(layer1,syn1))
                        layer2_error = np.array(br.learnArrayOut) - layer2 #common output ERR
                        if ((mainLearnCycle % 1000 == 0) and (startpos% 100 == 0) and (learncycle == 0)):
                            print("mainLearnCycle: " + str(mainLearnCycle) + ", position: " + str(startpos) + ", learncycle: " + str(learncycle) + " --> ANN predict forex error:" + str(np.mean(np.abs(layer2_error))))
                            print(layer2)
                            print(br.learnArrayOut)
                        layer2_delta = layer2_error*nonlin(layer2,deriv=True)
                        layer1_error = layer2_delta.dot(syn1.T)
                        layer1_delta = layer1_error * nonlin(layer1,deriv=True)
                        syn1 += layer1.T.dot(layer2_delta)
                        syn0 += layer0.T.dot(layer1_delta)
            startpos = 0
        ######----------end learn
        f.InputFiles[i].seek(0)
        for k in range(len(br.arrayIn)): #cleaning
            br.arrayIn.pop()
        f.getData(f.InputFiles[i])        
        br.createInputArray(br.IOcandles['in'][i] * 4,f.CurFileData, len(br.learnArrayIn))#количество свечей в одной цепочке, файл с цепочками, размер входа(нужное количество цеопчек)
        layer0 = np.array(br.arrayIn)
        print(layer0)
        layer1 = nonlin(np.dot(layer0,syn0))
        layer2 = nonlin(np.dot(layer1,syn1))
        print("-------------PREDICT-------------")
        print(layer2)
        print("---------------END---------------")
        print("---learning time %s seconds ---" % (time.time() - mytime[i]))
        f_predict.write(str(i) + '\n')
        np.savetxt(f_predict,layer2)
        f_predict.write("---learning time in seconds ---" + str(time.time() - mytime[i]) + '\n')
        f_predict.write('---------------------------------\n')
        f_predict.close()
        for k in range (len(br.learnArrayIn)): #cleaning
            br.learnArrayIn.pop()
        for k in range (len(br.learnArrayOut)):
            br.learnArrayOut.pop()
    else:
        f.TmpFilePath = f.QfilePath[i]
########

f.myShutdowm()
