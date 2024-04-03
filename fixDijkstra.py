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

dijkstraAlgTimeCalculations=None
def dijkstraAlg(start, end, normalizedGraph, startTime):

    dijkstraAlgStartCalculations=time.time_ns()

    start['g']=0
    start['arrivalTime']=secondsToHour(startTime)

    #słownik nazw wierzchołków (wraz z referencją do normalized graph) (budowa wierzchołka)
    qList=[]

    #ustawiamy g (czyli koszt najkrótszej ścieżki od startu do danego węzła) 
    #dla każdego węzła grafu, poza węzłem startowym
    #(to mogę też chyba robić od razu, gdy tworzę noda tzn. ustawiać g na nieskończoność)
    for node in normalizedGraph:
        if not node==start['name']:
            normalizedGraph[node]['g']=float('inf')
            qList.append(node)

    #na początku wybranym węzłem będzie start
    chosen_node=start


    while len(qList)>0:

        # chosenEdge=None

        #dla każdego sąsiada wybranego węzła, wybieramy najszybszą trasę
        #oraz zapisujemy rodzica i dane wybranej krawędzi (jeżeli jest to lepsze połączenie,
        #niż te wybrane wcześniej, tzn. gdy wybrano połączenie, które da mniejsze g)
        for node in chosen_node['neighbours']:

            #nie wracamy do już odwiedzonych wierzchołków
            if (node in qList):
                next_node=normalizedGraph[node]
                chosenEdge = chooseEdgeWithFAForSpecificNode(chosen_node, next_node)

                if next_node['g']>chosen_node['g'] + abs(hourToSeconds(chosenEdge._arrival_time()) - hourToSeconds(chosen_node['arrivalTime'])):
                    next_node['g']=chosen_node['g'] + abs(hourToSeconds(chosenEdge._arrival_time()) - hourToSeconds(chosen_node['arrivalTime']))
                    next_node['parent'] = chosen_node
                    next_node['departureTime']=chosenEdge._departure_time()
                    next_node['arrivalTime'] = chosenEdge._arrival_time()
                    next_node['departureLine'] = chosenEdge._line()
                    next_node['arrivalLine'] = chosenEdge._line() #zapis tego nie jest konieczny
                    next_node['edgeId'] = chosenEdge._id()


        # #to było trochę źle zrozumiane -> przeniosłem do funkcji
        # #TODO: tutaj też chcemy zapisać, do jakich węzłów jest już dostęp i przypisać im g (potem będziemy sprawdzać, czy istnieje szybszy dostęp do g)
        # #najpierw posortujmy wszystkie krawędzie węzła previousNode
        # edgesSortedByDeparture=[] 
        # for edge in previousNode['edges']:
        #     #wierzchołków, w których już byliśmy, nie sprawdzamy
        #     if (edge._end_node()._stop_name() in qList):
        #         edgesSortedByDeparture=addToSortedEdgesList(edge, edgesSortedByDeparture) 

        # #musimy znaleźć wszystkie krawędzie, które mają wyjazd w przyszłości
        # edgesInTheFutureIndex=None
        # for i in range(len(edgesSortedByDeparture)):
        #     if edgesSortedByDeparture[i]._departure_time()>=previousNode['arrivalTime']:
        #         edgesInTheFutureIndex=i
        #         break

        # #jeżeli są jakieś w przyszłości tego samego dnia...
        # if not edgesInTheFutureIndex==None:
        #     #ponieważ edgesSortedByDeparture jest posortowane czasem wyjazdu, pozostałe tablice też będą
        #     #szukamy linii z najszybszym przyjazdem (ale z przyjazdem w tym samym dniu lub z wyjazdem w tym samym dniu i przyjazdem w następnym)
        #     chosenEdge=chooseEdgeWithFastestArrival(edgesSortedByDeparture[edgesInTheFutureIndex:len(edgesSortedByDeparture)], previousNode['arrivalTime'])

        # #jeżeli nie, wybieramy z tych następnego dnia (czyli z całej tablicy, bo wtedy wszystkie edge są następnego dnia)
        # else:
        #     chosenEdge=chooseEdgeWithFastestArrival(edgesSortedByDeparture)



        # #PO WYBRANIU WĘZŁA DOCELOWEGO
        
        # # if(not chosenEdge==None):
        # chosenNode=normalizedGraph[chosenEdge._end_node()._stop_name()]
        # qList.remove[chosenNode['name']]
        # if(chosenNode['g']>previousNode['g']+(hourToSeconds(chosenEdge._arrival_time()) - hourToSeconds(previousNode['arrivalTime']))):
        #     chosenNode['g']=previousNode['g']+(hourToSeconds(chosenEdge._arrival_time()) - hourToSeconds(previousNode['arrivalTime']))
        

        # #na koniec trzeba ustawić previous noda na chosenNode
        # #previousNode = chosenNode


        #na koniec wybieramy kolejny węzeł, ktorego sąsiadów będziemy sprawdzać
        #wybranym węzłem będzie ten, o najmniejszym koszcie g
        chosen_node=None
        chosen_node_cost=float('inf')

        for node in qList:
            if normalizedGraph[node]['g']<chosen_node_cost:
                chosen_node_cost= normalizedGraph[node]['g']
                chosen_node = normalizedGraph[node]

        #usuwamy wybrany węzeł z listy qList
        qList.remove(chosen_node['name'])

        if chosen_node['name'] ==end['name']:
            dijkstraAlgEndCalculations=time.time_ns()
            global dijkstraAlgTimeCalculations
            dijkstraAlgTimeCalculations = dijkstraAlgEndCalculations - dijkstraAlgStartCalculations
            #TODO: wypisz drogę
            printSolutionDijkstra(chosen_node, end['name'])
            break

def chooseEdgeWithFAForSpecificNode(nodeFrom, nodeTo):
        
    nodeFromTime = nodeFrom['arrivalTime']
    chosenEdge=None

    #szukamy połączeń, które prowadzą do przystanku docelowego
    #muszą takie istnieć, bo node next to zawsze ten z sąsiadów noda,
    #a jest sąsiadem, jeżeli ma wspólną krawędź
    edgesWithTheSameEnd=[] #TODO: tu się przyda sortowanie przez wstawianie !!!!!!!!!!!!!!!!!!
    for edge in nodeFrom['edges']:
        if(edge._end_node()._stop_name()==nodeTo['name']):
            edgesWithTheSameEnd=addToSortedEdgesList(edge, edgesWithTheSameEnd)


    #wybieramy najszybsze z tych, co są w przyszłości
    #więc najpierw odsiewamy wszystkie, które są w przyszłości
    edgesWithTheSameEndInTheFutureIndex=None
    for i in range(len(edgesWithTheSameEnd)):
        if edgesWithTheSameEnd[i]._departure_time()>=nodeFromTime:
            edgesWithTheSameEndInTheFutureIndex=i
            break
    
    #jeżeli są jakieś w przyszłości tego samego dnia...
    if not edgesWithTheSameEndInTheFutureIndex==None:
        #ponieważ edgesWithTheSameEnd jest posortowane czasem wyjazdu, pozostałe tablice też będą
        #szukamy linii z najszybszym przyjazdem (ale z tych, których odjazd jest przed północą)
        chosenEdge=chooseEdgeWithFastestArrival(edgesWithTheSameEnd[edgesWithTheSameEndInTheFutureIndex:len(edgesWithTheSameEnd)], nodeFromTime)

    #jeżeli nie, wybieramy z tych następnego dnia (czyli z całej tablicy, bo wtedy wszystkie edge są następnego dnia)
    else:
        chosenEdge=chooseEdgeWithFastestArrival(edgesWithTheSameEnd)
    
    return chosenEdge
    #tu skończyłem

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
                #if listOfEdges[i]._departure_time()>'00:00:00': #TODO: TU JEST ŹLE! POPRAW W POZOSTAŁYCH!!! -> trzeba zakomentować tę linijkę i usunać wcięcie w dwóch wierszach poniżej
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

# #WAŻNE!: zawsze przystanek, z którego wysiadamy jest przystankiem, na którym wsiadamy
def printSolutionDijkstra(node, endName):
    if(node['parent']==None):
        print(f" Przystanek: {node['name']}, na przystanku: {node['arrivalTime']}, ", end="")
    else:
        printSolutionDijkstra(node['parent'], endName)
        print(f'odjazd: {node['departureTime']} linią {node['departureLine']}, eId: {node['edgeId']}')
        print(f'-> Przystanek: {node['name']}, przyjazd: {node['arrivalTime']}, ', end="")
        if (node['name']==endName):
            time.sleep(0.1)
            print(f'Wartośc g dla tego rozwiazania= {node['g']} s', file=sys.stderr)
            print(f'Czas obliczeń algorytmu= {dijkstraAlgTimeCalculations * (10**(-9))} s', file=sys.stderr)

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
            for nodeFrom in normalizedGraph:
                normalizedGraph[nodeFrom]['f']=None
                normalizedGraph[nodeFrom]['g']=None
                normalizedGraph[nodeFrom]['h']=None
                normalizedGraph[nodeFrom]['parent']=None
                normalizedGraph[nodeFrom]['departureTime']=None
                normalizedGraph[nodeFrom]['departureLine']=None
                normalizedGraph[nodeFrom]['edgeId']=None
                normalizedGraph[nodeFrom]['startNodeStartTime']=None
                normalizedGraph[nodeFrom]['arrivalLine']=None
                normalizedGraph[nodeFrom]['arrivalTime']=None
                normalizedGraph[nodeFrom]['howFarFromStart']=None
                normalizedGraph[nodeFrom]['g/hFFS']=None