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
    #ustawiamy g (czyli koszt najkrótszej ścieżki od startu do danego węzła) 
    #dla każdego węzła grafu, poza węzłem startowym
    #to mogę też chyba robić od razu, gdy tworzę noda tzn. ustawiać g na nieskończoność)
    for node in normalizedGraph:
        if not node==start['name']:
            normalizedGraph[node]['g']=float('inf')
    


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