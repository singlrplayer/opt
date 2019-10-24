import time
import datetime 

def endMonth (d, m, y):
    if (d < 31 and (m == 1 or m == 3 or m == 5 or m == 7 or m == 8 or m == 10 or m == 12)): return False
    if (d < 30 and (m == 4 or m == 6 or m == 9 or m == 11)): return False
    if (m == 2 and d == 28 and (y%4 != 0 or y%100 == 0)): return True
    if (m == 2 and d == 29 and (y%4 == 0 and y%100 != 0)): return True
    return True

def makeMyString (a):
    if (len (str(a)) < 2): s = '0' + str(a)
    else: s = str(a)
    return s

class s:
    d = ''
    t = ''
   
def updMytime (st, sd):
    #try :
        d = time.strptime(str(sd) , "%Y.%m.%d")
        day = int(d.tm_mday)
        month = int(d.tm_mon)
        year = int(d.tm_year)        
        if (st == 0): st = '00:00'
        t = time.strptime(str(st) , "%H:%M")
        h = int(t.tm_hour)
        m = int(t.tm_min)
        if (m < 59):
            m = m +1
        else: #если закончился час
            m = 0
            if (h < 23): h = h + 1
            else: #если закончился день
                h = m = 0 #ноль часов, ноль минут -> переход на следующий день
                if (day < 28):
                    day = day + 1 #полюбому не конец месяца
                else:
                    if (endMonth(day, month, year)):
                        if (month < 12): #если не декабрь
                            day = 1
                            month = month +1
                        else: #иначе новый Год 
                            day = month = 1
                            year = year + 1
                    else: day = day +1 #если все же не конец месяца
        s.d = makeMyString(year) + '.' + makeMyString(month) + '.' + makeMyString(day)
        s.t = makeMyString(h) + ':' + makeMyString(m) #секунды у нас не считаются никогда
        return s
    #except Exception:
    #    print ("ошибка формата даты\времени: \nдата " + str(sd) + "\nвремя " + str(st))


def minsBetween(date1, time1, date2, time2):
    d1 = time.strptime(str(date1) , "%Y.%m.%d")
    t1 = time.strptime(str(time1) , "%H:%M")
    d2 = time.strptime(str(date2) , "%Y.%m.%d")
    t2 = time.strptime(str(time1) , "%H:%M")
    tmp = (datetime.datetime.strptime(str(date1) , "%Y.%m.%d") - datetime.datetime.strptime(str(date2) , "%Y.%m.%d")).seconds/60 + (datetime.datetime.strptime(str(time1) , "%H:%M") - datetime.datetime.strptime(str(time2) , "%H:%M")).seconds/60
    return int(tmp)
        
    
