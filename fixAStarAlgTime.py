from edge import Edge
from node import Node
from djkNode import DjkNode
from aStarNode import AStarNode
import math
from datetime import datetime
import time

#edgeToCheck=None
#Graf buduje się właściwie
def buildGraphFromCSV(csvFileName):
    #global edgeToCheck
    graph=[dict(),[]]
    normalizedGraph=dict()

    with open(csvFileName,  encoding="UTF-8") as file:

        for dataLine in file:
            dataLine=dataLine.split(',')
            if dataLine[0]!='':
                
                    
                start_node = Node(dataLine[5], float(dataLine[7]), float(dataLine[8]))
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
                # if dataLine[0]=='55116':
                #     edgeToCheck=edge
                graph[1].append(edge)
                if(not (f'{start_node._stop_name()}{start_node._stop_lat()}{start_node._stop_lon()}' in graph[0])):
                    graph[0][f'{start_node._stop_name()}{start_node._stop_lat()}{start_node._stop_lon()}']=start_node
                if(not (f'{end_node._stop_name()}{end_node._stop_lat()}{end_node._stop_lon()}' in graph[0])):
                    graph[0][f'{end_node._stop_name()}{end_node._stop_lat()}{end_node._stop_lon()}']=end_node
                #add to normalized graph to get average location of stop
                    #ta funkcja jest sprawdzona i wykonuje się właściwie
                normalizedGraph = addToNormalizedGraph(edge, normalizedGraph)
                    #normalizedGraph = addToNormalizedGraph(end_node, start_node, normalizedGraph)
        for key in normalizedGraph:
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

    return normalizedGraph

def validateTime(time):
        time=time.split(':')
        time[0]=int(time[0])
        time[0]=str(time[0]%24)
        if(len(time[0])==1):
            time[0]=f'0{time[0]}'
        return f'{time[0]}:{time[1]}:{time[2]}'

def addToNormalizedGraph(edge, normalizedGraph):
    if(not(edge._start_node()._stop_name() in normalizedGraph)):
        normalizedGraph[edge._start_node()._stop_name()]={
            'nodes': [edge._start_node()],
            'edges': [edge],
            'neighbours': set([edge._end_node()._stop_name()]),
            'name': edge._start_node()._stop_name(),
            'f': None,
            'g':None,
            'h':None,
            'parent':None,
            'departureTime': None,
            'departureLine': None,
            'arrivalLine': None,
            'arrivalTime': None,
            'edgeId': None,
            'howFarFromStart': None,
            'g/hFFS': None
            }
    else:
        #jeżeli tego konkretnego węzła nie ma w zbiorze węzłów, to go dodajemy
        if(edge._start_node() not in normalizedGraph[edge._start_node()._stop_name()]['nodes']):
            normalizedGraph[edge._start_node()._stop_name()]['nodes'].append(edge._start_node())
        #krawędź dodajemy tak czy owak, ponieważ każda jest unikalna
        normalizedGraph[edge._start_node()._stop_name()]['edges'].append(edge)
        #jeżeli tego konkretnego węzła nie ma w zbiorze sąsiadów, to zostanie dodany
        normalizedGraph[edge._start_node()._stop_name()]['neighbours'].add(edge._end_node()._stop_name())
        
    return addEndNodeToNormalizedGraph(edge._end_node(),normalizedGraph, edge)

def addEndNodeToNormalizedGraph(end_node, normalizedGraph, edge):
    if(not(end_node._stop_name() in normalizedGraph)):
        normalizedGraph[end_node._stop_name()]={
            'nodes': [end_node],
            'edges': [],
            'neighbours': set(),
            'name': end_node._stop_name(),
            'f': None,
            'g':None,
            'h':None,
            'parent':None,
            'departureTime': None,
            'departureLine': None,
            'arrivalLine': None,
            'arrivalTime': None,
            'edgeId': None,
            'howFarFromStart': None,
            'g/hFFS': None
            }
    else:
        #jeżeli tego konkretnego węzła nie ma w liście węzłów, to go dodajemy
        if(end_node not in normalizedGraph[end_node._stop_name()]['nodes']):
            normalizedGraph[end_node._stop_name()]['nodes'].append(end_node)

    return normalizedGraph

######

# #WAŻNE!: zawsze przystanek, z którego wysiadamy jest przystankiem, na którym wsiadamy
def printSolution(node):
    if(node['parent']==None):
        print(f" Przystanek: {node['name']}, \
              czas pojawienia się na przystanku: {node['arrivalTime']}, ", end="")
    else:
        printSolution(node['parent'])
        print(f'odjazd z tego przystanku: {node['departureTime']} \
                    linią {node['departureLine']}')
        print(f'-> {node['edgeId']} Przystanek: {node['name']}, \
              przyjazd: {node['arrivalTime']}, ')



#TODO: coś tu nie działa-> czasem linia jest zła
# TODO: g to koszt dotarcia, a koszt dotarcia do startu powinien wynosić 0 !!! (popra to jakoś, może np. normalizuj od danej godziny)
mpkBusAvgVelocity=21.3
#nowa wersja -> heurystyka to czas (i g też)
def aStarAlgTime(start, end, graph, startTime): #start i end to znormalizowane węzły

    list_open=[]
    list_closed=[]

    start['g']=0 #startTime #tutaj jest zmiana, bo musimy być o którejś godzinie
    start['arrivalTime']=secondsToHour(startTime)
    print(f'start time: {secondsToHour(startTime)} {startTime}= startTime')
    start['h']=0
    start['f']=start['g']+start['h']


    list_open=[start]

    while len(list_open) > 0:
        node = None #to będzie znormalizowany węzeł
        node_cost=float('inf')

        for test_node in list_open:
            if (test_node['f']<node_cost):
                node = test_node
                node_cost = test_node['f']
        if node['name'] == end['name']:
            print('Rozwiązanie:')
            printSolution(node)
            break

        #TODO: be able to find this node
        list_open.remove(node)
        list_closed.append(node)

        #zapisuj co trzeba (arrival time itp.) ale w następnym nodzie
        for node_next_name in node['neighbours']:
            node_next_normalized_graph=graph[node_next_name]
            if (node_next_normalized_graph not in list_open and node_next_normalized_graph not in list_closed): #TODO: be able to fin this node
                nnH=calculateHTime(node_next_normalized_graph, end, graph)
                gTDResult=getTimeDiff(node, node_next_normalized_graph)
                nnG=node['g'] + gTDResult[0]
                node_next_normalized_graph['h']=nnH
                node_next_normalized_graph['g']=nnG
                node_next_normalized_graph['f']=nnH + nnG
                node_next_normalized_graph['parent']=node
                node_next_normalized_graph['arrivalTime']=gTDResult[1]._arrival_time()
                node_next_normalized_graph['edgeId']=gTDResult[1]._id()
                node_next_normalized_graph['departureTime']=gTDResult[1]._departure_time()
                node_next_normalized_graph['departureLine']=f'{gTDResult[1]._company()} {gTDResult[1]._line()}'
                # node['departureTime']=gTDResult[1]._departure_time()
                # node['departureLine']=f'{gTDResult[1]._company()} {gTDResult[1]._line()}'
                # node['edgeId']=gTDResult[1]._id()
                list_open.append(node_next_normalized_graph)
            else:
                #co tu się dokładnie dzieje?
                gTDResult=getTimeDiff(node,node_next_normalized_graph)
                if(node_next_normalized_graph['g']>node['g'] + gTDResult[0]):
                    node_next_normalized_graph['g']=node['g'] +gTDResult[0]
                    # node['departureTime']=gTDResult[1]._departure_time()
                    # node['departureLine']=f'{gTDResult[1]._company()} {gTDResult[1]._line()}'
                    # node['edgeId']=gTDResult[1]._id()
                    node_next_normalized_graph['arrivalTime']=gTDResult[1]._arrival_time()
                    node_next_normalized_graph['parent']=node
                    node_next_normalized_graph['f']=node_next_normalized_graph['g']+node_next_normalized_graph['h']
                    node_next_normalized_graph['edgeId']=gTDResult[1]._id()
                    node_next_normalized_graph['departureTime']=gTDResult[1]._departure_time()
                    node_next_normalized_graph['departureLine']=f'{gTDResult[1]._company()} {gTDResult[1]._line()}'
                    if(node_next_normalized_graph in list_closed): #TODO: trzeba móc odnaleźć tego noda w liście
                        list_open.append(node_next_normalized_graph)
                        list_closed.remove(node_next_normalized_graph) #TODO: trzeba móc odnaleźć noda

#acos(sin(lat1)*sin(lat2)+cos(lat1)*cos(lat2)*cos(lon2-lon1))*6371
#IMP: powyższe ze strony: https://community.fabric.microsoft.com/t5/Desktop/How-to-calculate-lat-long-distance/td-p/1488227  
#zwraca czas w sekundach                  
def calculateHTime(node_next_normalized_graph, end):
    return ((math.acos(math.sin(node_next_normalized_graph['averageLat'])*math.sin(end['averageLat']) +
            math.cos(node_next_normalized_graph['averageLat']) * math.cos(end['averageLat']) * 
            math.cos(end['averageLon'] - node_next_normalized_graph['averageLon']))*6371 / mpkBusAvgVelocity)*3600)

#TODO: do poprawy to, że nie rozróżnia linii i może się przesiąść, nawet, jeżeli nie musi, bo czas będzie ten sam (np. z K przesiadam się do 144 i jadę do domu)
#TODO: tutaj skończyłem. Trzeba znaleźć, kiedy będzie najszybsze połączenie -> zaimplementuj algorytm sortowania przez wstawianie
def getTimeDiff(node, node_next_normalized_graph):
    nodeFromTime = node['arrivalTime']
    edgesToCheck=[] #TODO: tu się przyda sortowanie przez wstawianie !!!!!!!!!!!!!!!!!!
    for edge in node['edges']:
        if(edge._end_node()._stop_name()==node_next_normalized_graph['name']):
            if not len(edge._departure_time())==len(nodeFromTime):
                print('Niezgodna dlugosc dat! 290')
            if(edge._departure_time()==nodeFromTime):
                return [edge._time_diff(), edge]
            else:
                edgesToCheck=addToSortedEdgesList(edge, edgesToCheck)  
    chosenEdge = None
    for edge in edgesToCheck:
        if not len(edge._departure_time())==len(nodeFromTime):
                print('Niezgodna dlugosc dat! 310')
        if edge._departure_time()>nodeFromTime: #nie =, bo to już było sprawdzone
            chosenEdge=edge
            break
    if chosenEdge==None:
        chosenEdge=edgesToCheck[0]
    chosenEdgeArrTime=hourToSeconds(chosenEdge._arrival_time()) #tutaj muszą być posortowane
    return [abs(chosenEdgeArrTime - hourToSeconds(node['arrivalTime'])), chosenEdge]
    


def addToSortedEdgesList(edge, edgesToCheck):
    for i in range(len(edgesToCheck)):
        if not len(edgesToCheck[i]._departure_time())==len(edge._departure_time()):
            print('Niezgodne długości dat! 320')
            print(f'{edgesToCheck[i]._departure_time()} vs {edge._departure_time()}, więc {edgesToCheck[i]._departure_time()>edge._departure_time()}')
        if(edgesToCheck[i]._departure_time()>edge._departure_time()):
            edgesToCheck.insert(i, edge)
            return edgesToCheck
    edgesToCheck.append(edge)
    return edgesToCheck
        
#IMP: kod z gemini
def secondsToHour(seconds):
    return validateTime(time.strftime('%H:%M:%S', time.gmtime(seconds))
)
#IMP: kod ze strony: https://www.geeksforgeeks.org/convert-a-datetime-object-to-seconds/
def hourToSeconds(time):
    timeDateObject = datetime.strptime(time, "%H:%M:%S")

    timeWithReference = timeDateObject - datetime(1900, 1, 1)
    seconds = timeWithReference.total_seconds()

    return seconds

def calculateHTime(normalizedNodeFrom, normalizedNodeTo, graph):
    #TODO: stwórz funkcję, konwertującą szerokość kątową na kilometry (żeby móc obliczyć przewidywany czas do celu)
    mpkBusAvgVelocity=21.3
    return (math.sqrt((normalizedNodeFrom['averageLon'] - 
            normalizedNodeTo['averageLon'])**2 + 
            (normalizedNodeFrom['averageLat'] - 
            normalizedNodeTo['averageLat'])**2))

    
if __name__=='__main__':
    normalizedGraph=buildGraphFromCSV('connection_graph.csv')
    while True:
        start=input('Podaj przystanek początkowy:')
        end=input('Podaj przystanek końcowy:')

        #IMP: kod z gemini konwertujący czas ze stringa w sekundy
        startTime=hourToSeconds(input('Podaj czas wyjazdu'))
        try:
            startNormalized=normalizedGraph[start]
            endNormalized=normalizedGraph[end]
            aStarAlgTime(startNormalized, endNormalized, normalizedGraph, startTime)
            #print(edgeToCheck)
        except KeyError:
            print('Nieprawidłowe dane wejściowe')
        option=input('Press "c" to continue or "s" to stop')
        if(option=='s'):
            break
        else:
            for node in normalizedGraph:
                normalizedGraph[node]['f']=None
                normalizedGraph[node]['g']=None
                normalizedGraph[node]['h']=None
                normalizedGraph[node]['parent']=None
                normalizedGraph[node]['departureTime']=None
                normalizedGraph[node]['departureLine']=None
                normalizedGraph[node]['edgeId']=None
                normalizedGraph[node]['startNodeStartTime']=None
                normalizedGraph[node]['arrivalLine']=None
                normalizedGraph[node]['arrivalTime']=None
                normalizedGraph[node]['howFarFromStart']=None
                normalizedGraph[node]['g/hFFS']=None