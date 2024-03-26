from edge import Edge
from node import Node
from djkNode import DjkNode
from aStarNode import AStarNode
import math

#test this datalines: 
#['991979', 'KŁOSOK Długołęka', '936', '21:20:00', '21:22:00', 'Siedlec - skrzy. Osiedlowa', 'Tokary - osiedle', '51.23393258', '17.12152196', '51.23070259', '17.13474563\n']
#and after adding this upper, add this:
#['992027', 'KŁOSOK Długołęka', '936', '22:57:00', '22:57:00', 'Siedlec - skrzy. Osiedlowa', 'Siedlec - stacja', '51.23404976', '17.12148102', '51.23453089', '17.12147004\n']

def buildGraphFromCSV():
    graph=[dict(),[]]
    normalizedGraph=dict()

    # with open(csvFileName) as file:
    # for i in range(1000):
    #     print(file.readline())
    count=0 #test
    for dataLine in [
        '990816,KŁOSOK Długołęka,936,04:20:00,04:20:00,Siedlec - stacja,Siedlec - skrzy. Osiedlowa,51.23456424,17.12128629,51.23393258,17.12152196',
        '990817,KŁOSOK Długołęka,936,04:20:00,04:22:00,Siedlec - skrzy. Osiedlowa,Tokary - osiedle,51.23393258,17.12152196,51.23070259,17.13474563',
        '990862,KŁOSOK Długołęka,936,05:30:00,05:30:00,Siedlec - stacja,Siedlec - skrzy. Osiedlowa,51.23456424,17.12128629,51.23393258,17.12152196',
        '990863,KŁOSOK Długołęka,936,05:30:00,05:32:00,Siedlec - skrzy. Osiedlowa,Tokary - osiedle,51.23393258,17.12152196,51.23070259,17.13474563',
        '990908,KŁOSOK Długołęka,936,06:40:00,06:40:00,Siedlec - stacja,Siedlec - skrzy. Osiedlowa,51.23456424,17.12128629,51.23393258,17.12152196',
        '990909,KŁOSOK Długołęka,936,06:40:00,06:42:00,Siedlec - skrzy. Osiedlowa,Tokary - osiedle,51.23393258,17.12152196,51.23070259,17.13474563',
        '990973,KŁOSOK Długołęka,936,08:40:00,08:40:00,Siedlec - stacja,Siedlec - skrzy. Osiedlowa,51.23456424,17.12128629,51.23393258,17.12152196',
        '990974,KŁOSOK Długołęka,936,08:40:00,08:42:00,Siedlec - skrzy. Osiedlowa,Tokary - osiedle,51.23393258,17.12152196,51.23070259,17.13474563',
        '991037,KŁOSOK Długołęka,936,10:28:00,10:30:00,Tokary - osiedle,Siedlec - skrzy. Osiedlowa,51.23085629,17.13505302,51.23404976,17.12148102',
        '991038,KŁOSOK Długołęka,936,10:30:00,10:30:00,Siedlec - skrzy. Osiedlowa,Siedlec - stacja,51.23404976,17.12148102,51.23453089,17.12147004',
        '991043,KŁOSOK Długołęka,936,10:40:00,10:40:00,Siedlec - stacja,Siedlec - skrzy. Osiedlowa,51.23456424,17.12128629,51.23393258,17.12152196',
        '991044,KŁOSOK Długołęka,936,10:40:00,10:42:00,Siedlec - skrzy. Osiedlowa,Tokary - osiedle,51.23393258,17.12152196,51.23070259,17.13474563'
        ]:
        count=count+1 #test

        #print(count)

        dataLine=dataLine.split(',')
        if dataLine[0]!='':
            start_node = Node(dataLine[5], float(dataLine[7]), float(dataLine[8]))
            if (dataLine[5]=='Siedlec - skrzy. Osiedlowa'):
                print(dataLine)
            end_node = Node(dataLine[6], float(dataLine[9]), float(dataLine[10]))
            edge = Edge(
                dataLine[0],
                dataLine[1],
                dataLine[2],
                validateTime(dataLine[3]),
                validateTime(dataLine[4]),
                start_node,
                end_node
            )

            # id = dataLine[0]
            # company = dataLine[1]
            # line = dataLine[2]
            # departure_time = dataLine[3]
            # arrival_time = dataLine[4]
            # start_node = Node(dataLine[5], dataLine[7], dataLine[8])
            # end_node = Node(dataLine[6], dataLine[9], dataLine[10])

            #here if true, we need to correct data
            # departure_time = correctTime(departure_time)
            # arrival_time = correctTime(arrival_time)
            #printDataLine([id, company, line, departure_time, arrival_time, start_node, end_node])

            #print(edge)
            graph[1].append(edge)

            if(not (f'{start_node._stop_name()}{start_node._stop_lat()}{start_node._stop_lon()}' in graph[0])):
                graph[0][f'{start_node._stop_name()}{start_node._stop_lat()}{start_node._stop_lon()}']=start_node

            if(not (f'{end_node._stop_name()}{end_node._stop_lat()}{end_node._stop_lon()}' in graph[0])):
                graph[0][f'{end_node._stop_name()}{end_node._stop_lat()}{end_node._stop_lon()}']=end_node

            #add to normalized graph to get average location of stop
                #ta funkcja jest sprawdzona i wykonuje się właściwie
                normalizedGraph = addToNormalizedGraph(edge, normalizedGraph)
                #normalizedGraph = addToNormalizedGraph(end_node, start_node, normalizedGraph)

            #if(count==5):
                #break
    #ta część też wykonuje się właściwie
    #for every stop name
    #count=0
    for key in normalizedGraph:
        #count+=1

        averageLon=0 #x
        averageLat=0 #y
        #we take average lat and lon
        for node in normalizedGraph[key]['nodes']:
            averageLon+=node._stop_lon()
            averageLat+=node._stop_lat()
        averageLon/=len(normalizedGraph[key]['nodes'])
        averageLat/=len(normalizedGraph[key]['nodes'])
        normalizedGraph[key]['averageLon']=averageLon
        normalizedGraph[key]['averageLat']=averageLat

        #print(normalizedGraph[key])
        # if count==5:
        #     break

    return normalizedGraph

def validateTime(time):
        time=time.split(':')
        time[0]=int(time[0])
        if(time[0]>=24):
            time[0]=str(time[0]%24)
            if(len(time[0])==1):
                time[0]=f'0{time[0]}'
        return f'{time[0]}:{time[1]}:{time[2]}'

def addToNormalizedGraph(edge, normalizedGraph):
    if(not(edge._start_node()._stop_name() in normalizedGraph)):
        #print(edge._start_node()._stop_name())
        #print(normalizedGraph[0])
        normalizedGraph[edge._start_node()._stop_name()]={
            'nodes': [edge._start_node()],
            #'edges': {edge._end_node()._stop_name(): [edge._end_node()._time_diff(), edge._end_node()._distance()]}
            'edges': [edge],
            'neighbours': set([edge._end_node()._stop_name()]),
            'name': edge._start_node()._stop_name(),
            #nowe:
            'f': None,
            'g':None,
            'h':None
            }
    else:
        #jeżeli tego konkretnego węzła nie ma w zbiorze węzłów, to go dodajemy
        if(edge._start_node() not in normalizedGraph[edge._start_node()._stop_name()]['nodes']):
            normalizedGraph[edge._start_node()._stop_name()]['nodes'].append(edge._start_node())
        #normalizedGraph[1][node.stop_name()]['edges'].add(nodeTo.stop_name())
        #krawędź dodajemy tak czy owak, ponieważ każda jest unikalna
        normalizedGraph[edge._start_node()._stop_name()]['edges'].append(edge)
        #jeżeli tego konkretnego węzła nie ma w zbiorze sąsiadów, to zostanie dodany
        normalizedGraph[edge._start_node()._stop_name()]['neighbours'].add(edge._end_node()._stop_name())
        
    return addEndNodeToNormalizedGraph(edge._end_node(),normalizedGraph)

def addEndNodeToNormalizedGraph(end_node, normalizedGraph):
    if(not(end_node._stop_name() in normalizedGraph)):
        #print(edge._start_node()._stop_name())
        #print(normalizedGraph[0])
        normalizedGraph[end_node._stop_name()]={
            'nodes': [end_node],
            #'edges': {edge._end_node()._stop_name(): [edge._end_node()._time_diff(), edge._end_node()._distance()]}
            'edges': [],
            'neighbours': set(),
            'name': end_node._stop_name(),
            #nowe:
            'f': None,
            'g':None,
            'h':None
            }
    else:
        #jeżeli tego konkretnego węzła nie ma w liście węzłów, to go dodajemy
        if(end_node not in normalizedGraph[end_node._stop_name()]['nodes']):
            normalizedGraph[end_node._stop_name()]['nodes'].append(end_node)
        #normalizedGraph[1][node.stop_name()]['edges'].add(nodeTo.stop_name())
        
    return normalizedGraph

if __name__=='__main__':
    print(buildGraphFromCSV())