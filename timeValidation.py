hourBiggerThan23=0
minutesBiggerThan59=0
secondsBiggerThan59=0
def showIfTimeNotalid(csvFileName):
    with open(csvFileName,  encoding="UTF-8") as file:
        for dataLine in file:
            dataLine=dataLine.split(',')
            if dataLine[0]!='':
                
                isTimeValid(dataLine[3])
                isTimeValid(dataLine[4])
    global hourBiggerThan23
    global minutesBiggerThan59
    global secondsBiggerThan59
    print(f'num of hour bigger than 23: {hourBiggerThan23}')
    print(f'num of minutes bigger than 59: {minutesBiggerThan59}')
    print(f'num of seconds bigger than 59: {secondsBiggerThan59}')

def isTimeValid(time):
    time=time.split(':')
    if(int(time[0])>23):
        global hourBiggerThan23
        hourBiggerThan23+=1
    if(int(time[1])>59):
        global minutesBiggerThan59
        minutesBiggerThan59+=1
    if(int(time[2])>59):
        global secondsBiggerThan59
        secondsBiggerThan59+=1

if __name__=='__main__':
    showIfTimeNotalid('connection_graph.csv')