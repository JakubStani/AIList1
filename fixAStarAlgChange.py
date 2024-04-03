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

######

#chcemy otrzymać: czy będzie przesiadka, i edge możliwie bez przesiadki
def getChanges(node, node_next_normalized_graph):
    change=0
    nodeFromTime = node['arrivalTime']
    chosenEdge=None

    #szukamy połączeń, które prowadzą do przystanku docelowego
    #muszą takie istnieć, bo node next to zawsze ten z sąsiadów noda,
    #a jest sąsiadem, jeżeli ma wspólną krawędź
    edgesWithTheSameEnd=[] #TODO: tu się przyda sortowanie przez wstawianie !!!!!!!!!!!!!!!!!!
    for edge in node['edges']:
        if(edge._end_node()._stop_name()==node_next_normalized_graph['name']):
            edgesWithTheSameEnd=addToSortedEdgesList(edge, edgesWithTheSameEnd) #tutaj nie zależy nam na czasie, a jedynie na tej samej linii

    #odsiewamy te, które są tą samą linią
    edgesWithTheSameLine=[]
    #dla węzła startowego nie ma żadnej lini, którą przyjechaliśmy, więc tego nie sprawdzamy
    if(not node['departureLine']==None):
        for edge in edgesWithTheSameEnd:
            if(f'{edge._company()} {edge._line()}'==node['departureLine']): #departureLine, to linia, którą się przyjechało do node (bo kolejne węzły zapamiętują poprzednie krawędzie)
                edgesWithTheSameLine.append(edge)

    
    #jeżeli są połączenia tą samą linia...
    edgesWithTheSameLineInTheFutureIndex=None
    if len(edgesWithTheSameLine)>0:
        #staramy się wybrać najszybsze z nich, które jest w przyszłości tego samego dnia
        for i in range(len(edgesWithTheSameLine)):
            if edgesWithTheSameLine[i]._departure_time()>=nodeFromTime:
                edgesWithTheSameLineInTheFutureIndex=i
                break
        
        #jeżeli są jakieś w przyszłości tego samego dnia...
        if not edgesWithTheSameLineInTheFutureIndex==None:
            #ponieważ edgesWithTheSameEnd jest posortowane czasem wyjazdu, pozostałe tablice też będą
            #szukamy linii z najszybszym przyjazdem (ale z przyjazdem w tym samym dniu)
            chosenEdge=chooseEdgeWithFastestArrival(edgesWithTheSameLine[edgesWithTheSameLineInTheFutureIndex:len(edgesWithTheSameLine)], nodeFromTime)

        #jeżeli nie, wybieramy z tych następnego dnia (czyli z całej tablicy, bo wtedy wszystkie edge są następnego dnia)
        else:
            chosenEdge=chooseEdgeWithFastestArrival(edgesWithTheSameLine)


    #jeżeli takich nie ma, wybieramy najszybsze z tych, co są w przyszłości
    else:
        #(w tej sekcji na pewno będzie przesiadka, więc change zwiększa sie do 1)
        change=1

        #więc najpierw odsiewamy wszystkie, które są w przyszłości
        edgesWithTheSameEndInTheFutureIndex=None
        for i in range(len(edgesWithTheSameEnd)):
            if edgesWithTheSameEnd[i]._departure_time()>=nodeFromTime:
                edgesWithTheSameEndInTheFutureIndex=i
                break
        
        #jeżeli są jakieś w przyszłości tego samego dnia...
        if not edgesWithTheSameEndInTheFutureIndex==None:
            #ponieważ edgesWithTheSameEnd jest posortowane czasem wyjazdu, pozostałe tablice też będą
            #szukamy linii z najszybszym przyjazdem (ale z przyjazdem w tym samym dniu)
            chosenEdge=chooseEdgeWithFastestArrival(edgesWithTheSameEnd[edgesWithTheSameEndInTheFutureIndex:len(edgesWithTheSameEnd)], nodeFromTime)

        #jeżeli nie, wybieramy z tych następnego dnia (czyli z całej tablicy, bo wtedy wszystkie edge są następnego dnia)
        else:
            chosenEdge=chooseEdgeWithFastestArrival(edgesWithTheSameEnd)

    #zwracamy informację o liczbie przesiadek i o wybranym połączeniu
    return [change, chosenEdge]

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
                # if listOfEdges[i]._departure_time()>'00:00:00': #TODO: TU JEST ŹLE! POPRAW W POZOSTAŁYCH!!! -> trzeba zakomentować tę linijkę i usunać wcięcie w dwóch wierszach poniżej
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

def calculateHChange(node_next_normalized_graph, end, graph):
    distanceKm=calculateHDistance(node_next_normalized_graph, end)
    return node_next_normalized_graph['g/hFFS']*distanceKm



# #WAŻNE!: zawsze przystanek, z którego wysiadamy jest przystankiem, na którym wsiadamy
def printSolutionAStarChange(node, endName):
    if(node['parent']==None):
        print(f" Przystanek: {node['name']}, na przystanku: {node['arrivalTime']}, ", end="")
    else:
        printSolutionAStarChange(node['parent'], endName)
        print(f'odjazd: {node['departureTime']} linią {node['departureLine']}, eId: {node['edgeId']}, przesidaki do tej pory: {node['g']}')
        print(f'-> Przystanek: {node['name']}, przyjazd: {node['arrivalTime']}, ', end="")
        if (node['name']==endName):
            time.sleep(0.5)
            print(f'Wartośc f dla tego rozwiazania= {node['f']}', file=sys.stderr)
            print(f'Czas obliczeń algorytmu= {aStarTimeCalculations*(10**(-9))} s', file=sys.stderr)

#IMP: Wzór "Haversine formula" (źródło: https://www.youtube.com/watch?v=HaGj0DjX8W8)
def calculateHDistance(normalizedNodeFrom, normalizedNodeTo):
    nauticalMileToKilometers=1.852
    # to trzeba zmienić na km
    # return (math.sqrt((normalizedNodeFrom['averageLon'] - 
    #         normalizedNodeTo['averageLon'])**2 + 
    #         (normalizedNodeFrom['averageLat'] - 
    #         normalizedNodeTo['averageLat'])**2))

    # return (math.acos(math.sin(normalizedNodeFrom['averageLat'])*math.sin(normalizedNodeTo['averageLat']) +
    #         math.cos(normalizedNodeFrom['averageLat']) * math.cos(normalizedNodeTo['averageLat']) * 
    #         math.cos(normalizedNodeTo['averageLon'] - normalizedNodeFrom['averageLon']))*6371)
    lat1 = degreesToRadians(normalizedNodeFrom['averageLat'])
    lon1 = degreesToRadians(normalizedNodeFrom['averageLon'])
    lat2 = degreesToRadians(normalizedNodeTo['averageLat'])
    lon2 = degreesToRadians(normalizedNodeTo['averageLon'])
    return (
        3440.1 * math.acos( 
            (math.sin(lat1) * math.sin(lat2)) +
            math.cos(lat1) * math.cos(lat2) *
            math.cos(lon1 - lon2)) *nauticalMileToKilometers
    )

def degreesToRadians(degrees):
    return degrees * math.pi / 180

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
    return validateTime(time.strftime('%H:%M:%S', time.gmtime(seconds)))

#IMP: kod ze strony: https://www.geeksforgeeks.org/convert-a-datetime-object-to-seconds/
def hourToSeconds(time):
    timeDateObject = datetime.strptime(time, "%H:%M:%S")

    timeWithReference = timeDateObject - datetime(1900, 1, 1)
    seconds = timeWithReference.total_seconds()

    return seconds

aStarTimeCalculations=None
#heurystyka to przesiadki (i g też)
def aStarAlgChange(start, end, graph, startTime): #start i end to znormalizowane węzły
    aStarAlgStartsCalculations=time.time_ns()

    list_open=[]
    list_closed=[]

    start['g']=0
    start['h']=0
    start['f']=start['g']+start['h']
    start['howFarFromStart']=0
    start['arrivalTime']=secondsToHour(startTime)


    list_open=[start]

    while len(list_open) > 0:
        node = None #to będzie znormalizowany węzeł
        node_cost=float('inf')

        for test_node in list_open:
            if (test_node['f']<node_cost):
                node = test_node
                node_cost = test_node['f']
        if node['name'] == end['name']:
            aStarAlgEndsCalculations=time.time_ns()
            global aStarTimeCalculations
            aStarTimeCalculations=aStarAlgEndsCalculations-aStarAlgStartsCalculations
            print('Rozwiązanie:')
            printSolutionAStarChange(node, end['name'])
            break

        list_open.remove(node)
        list_closed.append(node)

        #tu się zaczynają problemy z sąsiadami, bo info o sąsiadach ma normalized graph, a tam nie ma AstarNodów
        #tutaj node next ma być AStarNodem, tylko jak go utworzyć?
        for node_next_name in node['neighbours']:
            #szukam po nazwie, bo node_next nie jest AStarNodem
            node_next_normalized_graph=graph[node_next_name]
            gCh=getChanges(node, node_next_normalized_graph)
            #WAŻNE: możliwe uproszczenia
            if (node_next_normalized_graph not in list_open and node_next_normalized_graph not in list_closed): #TODO: be able to fin this node
                node_next_normalized_graph['howFarFromStart']=node['howFarFromStart'] + gCh[1]._distance()
                node_next_normalized_graph['g']=node['g'] + gCh[0] #!!!
                node_next_normalized_graph['g/hFFS']=(node_next_normalized_graph['g'])/node_next_normalized_graph['howFarFromStart'] #!!!
                node_next_normalized_graph['h']=calculateHChange(node_next_normalized_graph, end, graph)
                node_next_normalized_graph['f']=node_next_normalized_graph['h'] + node_next_normalized_graph['g'] #!!!
                node_next_normalized_graph['parent']=node #!!!
                node_next_normalized_graph['arrivalTime']=gCh[1]._arrival_time() #!!!
                node_next_normalized_graph['edgeId']=gCh[1]._id() #!!!
                node_next_normalized_graph['departureTime']=gCh[1]._departure_time() #!!!
                node_next_normalized_graph['departureLine']=f'{gCh[1]._company()} {gCh[1]._line()}' #!!!
                #node_next_normalized_graph['arrivalLine']=f'{gCh[1]._company()} {gCh[1]._line()}' #!!!
                
                list_open.append(node_next_normalized_graph)
            else:
                if(node_next_normalized_graph['g']>node['g'] + gCh[0]):
                    node_next_normalized_graph['g']=node['g'] + gCh[0]
                    node_next_normalized_graph['howFarFromStart']=node['howFarFromStart'] + gCh[1]._distance()
                    node_next_normalized_graph['g/hFFS']=(node_next_normalized_graph['g'])/node_next_normalized_graph['howFarFromStart'] 
                    node_next_normalized_graph['h']=calculateHChange(node_next_normalized_graph, end, graph)
                    node_next_normalized_graph['f']=node_next_normalized_graph['g']+node_next_normalized_graph['h']
                    node_next_normalized_graph['parent']=node #!!!
                    node_next_normalized_graph['arrivalTime']=gCh[1]._arrival_time() #!!!
                    node_next_normalized_graph['edgeId']=gCh[1]._id() #!!!
                    node_next_normalized_graph['departureTime']=gCh[1]._departure_time() #!!!
                    node_next_normalized_graph['departureLine']=f'{gCh[1]._company()} {gCh[1]._line()}' #!!!

                    if(node_next_normalized_graph in list_closed): #TODO: trzeba móc odnaleźć tego noda w liście
                        list_open.append(node_next_normalized_graph)
                        list_closed.remove(node_next_normalized_graph) #TODO: trzeba móc odnaleźć noda

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
            aStarAlgChange(startNormalized, endNormalized, normalizedGraph, startTime)
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