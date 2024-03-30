from edge import Edge
from node import Node
from djkNode import DjkNode
from aStarNode import AStarNode
import math
from datetime import datetime
import time
import sys


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

def hourToSeconds(time):
    timeDateObject = datetime.strptime(time, "%H:%M:%S")

    timeWithReference = timeDateObject - datetime(1900, 1, 1)
    seconds = timeWithReference.total_seconds()

    return seconds


def dijkstraAlg(start, end, normalizedGraph, startTime):

    start['g']=0
    start['arrivalTime']=secondsToHour(startTime)

    #Lista nazw wierzchołków
    qList=[]

    #ustawiamy g (czyli koszt najkrótszej ścieżki od startu do danego węzła) 
    #dla każdego węzła grafu, poza węzłem startowym
    #to mogę też chyba robić od razu, gdy tworzę noda tzn. ustawiać g na nieskończoność)
    for node in normalizedGraph:
        if not node==start['name']:
            normalizedGraph[node]['g']=float('inf')
            qList.append(node)

    previousNode=start


    while len(qList)>0:

        #następnym wybranym węzłem będzie ten, o najmniejszym koszcie g
        next_node=None
        next_node_cost=float('inf')

        chosenEdge=None

        #TODO: tutaj też chcemy zapisać, do jakich węzłów jest już dostęp i przypisać im g (potem będziemy sprawdzać, czy istnieje szybszy dostęp do g)
        #najpierw posortujmy wszystkie krawędzie
        edgesSortedByDeparture=[] 
        for edge in previousNode['edges']:
            edgesSortedByDeparture=addToSortedEdgesList(edge, edgesSortedByDeparture) 

        #musimy znaleźć wszystkie krawędzie, które mają wyjazd w przyszłości
        edgesInTheFutureIndex=None
        for i in range(len(edgesSortedByDeparture)):
            if edgesSortedByDeparture[i]._departure_time()>=previousNode['arrivalTime']:
                edgesInTheFutureIndex=i
                break

        #jeżeli są jakieś w przyszłości tego samego dnia...
        if not edgesInTheFutureIndex==None:
            #ponieważ edgesSortedByDeparture jest posortowane czasem wyjazdu, pozostałe tablice też będą
            #szukamy linii z najszybszym przyjazdem (ale z przyjazdem w tym samym dniu lub z wyjazdem w tym samym dniu i przyjazdem w następnym)
            chosenEdge=chooseEdgeWithFastestArrival(edgesSortedByDeparture[edgesInTheFutureIndex:len(edgesSortedByDeparture)], previousNode['arrivalTime'])

        #jeżeli nie, wybieramy z tych następnego dnia (czyli z całej tablicy, bo wtedy wszystkie edge są następnego dnia)
        else:
            chosenEdge=chooseEdgeWithFastestArrival(edgesSortedByDeparture)



        #PO WYBRANIU WĘZŁA DOCELOWEGO
        
        if(not chosenEdge==None):
            chosenNode=normalizedGraph[chosenEdge._end_node()._stop_name()]
            qList.remove[chosenNode['name']]
            if(chosenNode['g']<previousNode['g']+(hourToSeconds(chosenEdge._arrival_time()) - hourToSeconds(previousNode['arrivalTime']))):
                chosenNode['g']=previousNode['g']+(hourToSeconds(chosenEdge._arrival_time()) - hourToSeconds(previousNode['arrivalTime']))
        

        #na koniec trzeba ustawić previous noda na


#listOfEdges nie może być pusta!!
def chooseEdgeWithFastestArrival(listOfEdges, nodeFromTime=None):

    fastestEdgeArrival='23:59:59'
    fastestEdgeArrivalIndex=None

    for i in range(len(listOfEdges)):
        if listOfEdges[i]._arrival_time()<fastestEdgeArrival:
            if(not nodeFromTime==None):
                #chcemy uniknać sytuacji, że wybierze linię, która przyjeżdża o np. 00:00:01, a wyjeżdża o 23:59:59, jeżeli są lepsze opcje 
                #(bo taka linia przyjeżdża o najszybszej godzinie, ale najszybszej w następnym dniu)
                if listOfEdges[i]._arrival_time()>nodeFromTime:
                    fastestEdgeArrival=listOfEdges[i]._arrival_time()
                    fastestEdgeArrivalIndex=i
            else:
                #ta sytuacja ma miejsce, gdy przyjechaliśmy na przystanek i nie ma już żadnych linii tego dnia
                #chcemy uniknać sytuacji, że wybierze linię, która najszybciej przyjeżdża, bo wyjeżdża poprzedniego dnia
                if listOfEdges[i]._departure_time()>'00:00:00':
                    fastestEdgeArrival=listOfEdges[i]._arrival_time()
                    fastestEdgeArrivalIndex=i
            
    # if(fastestEdgeArrivalIndex==None):
    #     list(map(lambda x: print(f'dep: {x._departure_time()}, arr: {x._arrival_time()}', listOfEdges)))
                    
    #jeżeli były tylko takie opcje, które wyjeżdżają jednego dnia, a dojeżdżają drugiego...
    if(fastestEdgeArrivalIndex==None and not nodeFromTime==None):
        #wybieramy tą z najszybszym dojazdem
        fastestEdgeArrival='23:59:59'
        for i in range(len(listOfEdges)):
            if listOfEdges[i]._arrival_time()<fastestEdgeArrival:
                fastestEdgeArrival=listOfEdges[i]._arrival_time()
                fastestEdgeArrivalIndex=i

    return listOfEdges[fastestEdgeArrivalIndex]

#IMP: kod z gemini
def secondsToHour(seconds):
    return validateTime(time.strftime('%H:%M:%S', time.gmtime(seconds)))

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

def validateTime(time):
        time=time.split(':')
        time[0]=int(time[0])
        time[0]=str(time[0]%24)
        if(len(time[0])==1):
            time[0]=f'0{time[0]}'
        return f'{time[0]}:{time[1]}:{time[2]}'

if __name__=='__main__':
    normalizedGraph=buildGraphFromCSV('connection_graph.csv')
    while True:
        start=input('Podaj przystanek początkowy: ')
        end=input('Podaj przystanek końcowy: ')

        #IMP: kod z gemini konwertujący czas ze stringa w sekundy
        startTime=hourToSeconds(input('Podaj czas wyjazdu: '))
        try:
            startNormalized=normalizedGraph[start]
            endNormalized=normalizedGraph[end]
            dijkstraAlg(startNormalized, endNormalized, normalizedGraph, startTime)
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