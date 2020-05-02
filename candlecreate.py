import itertools
from updMytime import *
from myParsLine import getCandleFromSource
#from myFile import myFile
from candleValues import candleValues

def candlecreate(filein, fileout,count):
    dt = [] # тут будет жить первая и последняя свеча / ВАЖНО: последняя не попадает в файл обучения!!!!
    #files = myFile()
    #files.myInit()
    #files.Qfiles['minFile'].write(files.source['f'].readline()) #первую строку переписываем, но только в минутный файл. мне надо, чтобы его понимал форексовый терминал
    y = getCandleFromSource(filein.readline()) #вторую парсим чтоб задать стартовые значения (надо будет сделать это как-то изящнее)
    dt.append(encodeDataTime(y.date, y.time))#первая свеча (та, что первой подаётся на вход) 
    val = updMytime('00:00','2001.01.01') #TODO: убрать нахер отсюда, и сделать нормально
    val.d = date = olddate = y.date; val.t = time = oldtime = y.time
    candle = candleValues()
    candle.myInit(y)
    y.rememberOldDatatime(y, val)
    y.rememberOldCandle(y)
    j = j_min = 0
    for line in filein:
        y = getCandleFromSource(line)
        candle.updateMe(y,j_min, fileout, False) #update means file data update
        date = y.date
        time = y.time
        openVal = y.openVal
        hightVal = y.hightVal
        lowVal = y.lowVal
        closeVal = y.closeVal
        j = j +1; j_min = j_min +1 #c++ is crying
        val = updMytime(oldtime, olddate)
        y.rememberOldDatatime(y, val)
        oldtime = y.olddata['oldtime']
        olddate = y.olddata['olddate']
        rowTmp = 0 #длина (ширина\ продолжательность, если угодно) поддельного ряда 
        while ((time > oldtime or date > olddate)): #таким вот образом обнаруживается дыра в исходных минутных данных, которая заполняется предыдущими свечками
            #ВНИМАНИЕ, блядь, ЭКСПЕРЕМЕНТАЛЬНАЯ синяя изолента
            if (rowTmp > 30): break #ограничиваем количество поддельных свечей в 30 штук
            # конец изоленты
            timetmp = minsBetween(date,time,olddate,oldtime)
            if (timetmp == count):
                y.candle['auth'] = y.candle['auth'] + 1
                candle.updateMe(y,j_min, fileout, True)
                j_min = j_min +1
            #else: break #если прошло менньше времени, чем длится свеча
            #print(oldtime)
            #print(olddate)
            val = updMytime(oldtime, olddate)
            y.rememberOldDatatime(y, val)
            oldtime = y.olddata['oldtime']
            olddate = y.olddata['olddate']
            #ВНИМАНИЕ, блядь, ЭКСПЕРЕМЕНТАЛЬНАЯ синяя изолента
            rowTmp = rowTmp + 1
            # конец изоленты
       #основная мысль: дыры в котировках появились за счет того, что в данный отрезок времени сделок небыло, следовательно мы их заполняем идентичными свечками, потому как ничего не менялось
       #возможны 100500 иных причин дырам в котировках, да ;) выходные и всяческие bank holydays например
       #возможно, апроксимация сработает лучше, но это будет видно уже при обучении
        y.rememberOldCandle(y)
        olDopenVal = openVal
        olDhightVal = hightVal
        olDlowVal = lowVal
        olDcloseVal = closeVal
        oldtime = time
        olddate = date
    dt.append(encodeDataTime(y.date, y.time)) #последняя (она же -- предсказуемая. на ней не учимся)
    return dt
    #files.myShutdowm()
    #return files
    #print ("old " + str(j) + '\nnew ' + str(j_min))

def candlecreateASIS(filein, fileout, count): #потом разберемся. пока пробуе так
    dt = [] # тут будет жить первая и последняя свеча / ВАЖНО: последняя не попадает в файл обучения!!!!
    y = getCandleFromSource(filein.readline()) #первую строку читаем отдельно, потому как надло запомнить первую свечу
    dt.append(encodeDataTime(y.date, y.time))
    for line in filein:
        fileout.write(str(y.date) + ','+ str(y.time)+','+str(y.openVal)+','+str(y.hightVal)+','+str(y.lowVal)+','+str(y.closeVal)+'\n') #последовательность записи значений в файл важна!!!!!!!!!
        y = getCandleFromSource(line)
    fileout.seek(0) #дальше нам надо будет читать его с начала
    dt.append(encodeDataTime(y.date, y.time))
    return dt
