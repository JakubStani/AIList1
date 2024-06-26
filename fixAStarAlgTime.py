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

# #WAŻNE!: zawsze przystanek, z którego wysiadamy jest przystankiem, na którym wsiadamy
def printSolution(node, endName):
    if(node['parent']==None):
        print(f" Przystanek: {node['name']}, na przystanku: {node['arrivalTime']}, ", end="")
    else:
        printSolution(node['parent'], endName)
        print(f'odjazd: {node['departureTime']} linią {node['departureLine']}, eId: {node['edgeId']}')
        print(f'-> Przystanek: {node['name']}, przyjazd: {node['arrivalTime']}, ', end="")
        if (node['name']==endName):
            time.sleep(0.1)
            print(f'Wartośc f dla tego rozwiazania= {node['f']} s', file=sys.stderr)
            print(f'Czas obliczeń algorytmu= {aStarTimeCalculations * (10**(-9))} s', file=sys.stderr)



#TODO: zaimplementuj, aby wybierało linię, która ma najszybszy dojazd z linii z przyszłości
#pomysł na skrócenie czasu obliczeń-> od razu wstawianie do listy otwartej tak, żeby było sortowanie przez wstawianie
mpkBusAvgVelocity=21.3
aStarTimeCalculations=None
#nowa wersja -> heurystyka to czas (i g też)
def aStarAlgTime(start, end, graph, startTime): #start i end to znormalizowane węzły
    aStarAlgStartsCalculations=time.time_ns()

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
            aStarAlgEndsCalculations=time.time_ns()
            global aStarTimeCalculations
            aStarTimeCalculations=aStarAlgEndsCalculations-aStarAlgStartsCalculations
            print('Rozwiązanie:')
            printSolution(node, end['name'])
            break

        #TODO: be able to find this node
        list_open.remove(node)
        list_closed.append(node)

        #zapisuj co trzeba (arrival time itp.) ale w następnym nodzie
        for node_next_name in node['neighbours']:
            node_next_normalized_graph=graph[node_next_name]
            if (node_next_normalized_graph not in list_open and node_next_normalized_graph not in list_closed): #TODO: be able to fin this node
                nnH=calculateHTime(node_next_normalized_graph, end)
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
    global mpkBusAvgVelocity
    return (calculateHDistance(node_next_normalized_graph, end) / mpkBusAvgVelocity)*3600

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

#TODO: do poprawy to, że nie rozróżnia linii i może się przesiąść, nawet, jeżeli nie musi, bo czas będzie ten sam (np. z K przesiadam się do 144 i jadę do domu)
#TODO: tutaj skończyłem. Trzeba znaleźć, kiedy będzie najszybsze połączenie -> zaimplementuj algorytm sortowania przez wstawianie
def getTimeDiff(node, node_next_normalized_graph):

    # #WERSJA POPRZEDNIA -> bez uwzględnienia najszybszego dojazdu, tylko uwzględnienie najszybszego wyjazdu
    # #szukamy połączeń, które prowadzą do przystanku docelowego
    # #muszą takie istnieć, bo node next to zawsze ten z sąsiadów noda,
    # #a jest sąsiadem, jeżeli ma wspólną krawędź
    # edgesWithTheSameEnd=[]
    # for edge in node['edges']:
    #     if(edge._end_node()._stop_name()==node_next_normalized_graph['name']):
    #         if not len(edge._departure_time())==len(node['arrivalTime']):
    #             print('Niezgodna dlugosc dat! 290')
    #         if(edge._departure_time()==node['arrivalTime']):
    #             return [edge._time_diff(), edge]
    #         else:
    #             edgesWithTheSameEnd=addToSortedEdgesList(edge, edgesWithTheSameEnd)  
    # chosenEdge = None
    # for edge in edgesWithTheSameEnd:
    #     if not len(edge._departure_time())==len(node['arrivalTime']):
    #             print('Niezgodna dlugosc dat! 310')
    #     if edge._departure_time()>node['arrivalTime']: #nie =, bo to już było sprawdzone
    #         chosenEdge=edge
    #         break
    # if chosenEdge==None:
    #     chosenEdge=edgesWithTheSameEnd[0]
    # chosenEdgeArrTime=hourToSeconds(chosenEdge._arrival_time()) #tutaj muszą być posortowane
    # return [abs(chosenEdgeArrTime - hourToSeconds(node['arrivalTime'])), chosenEdge]

    #NOWA WERSJA -> uwzględnienie najszybszego dojazdu, a nie najszybszego wyjazdu
    nodeFromTime = node['arrivalTime']

    # #najkorzystniejsze połączenie z tą samą linią
    # chosenEdgeWithTheSameLine= None
    # #jaka sytuacja: 0-> wyjazd tegosamego dnia, co dojazd, 1-> wyjazd i dojazd w różne dni, 2-> wyjazd i dojazd następnego dnia
    # eventWithTheSameLine=None

    #najkorzystniejsze połączenie ogółem
    chosenEdge=None
    # #jaka sytuacja: 0-> wyjazd tegosamego dnia, co dojazd, 1-> wyjazd i dojazd w różne dni, 2-> wyjazd i dojazd następnego dnia
    # eventGeneral=None


    #szukamy połączeń, które prowadzą do przystanku docelowego
    #muszą takie istnieć, bo node next to zawsze ten z sąsiadów noda,
    #a jest sąsiadem, jeżeli ma wspólną krawędź
    edgesWithTheSameEnd=[] #TODO: tu się przyda sortowanie przez wstawianie !!!!!!!!!!!!!!!!!!
    for edge in node['edges']:
        if(edge._end_node()._stop_name()==node_next_normalized_graph['name']):
            edgesWithTheSameEnd=addToSortedEdgesList(edge, edgesWithTheSameEnd)

    # #Jednak tego poniższego nie
    # #odsiewamy te, które są tą samą linią
    # edgesWithTheSameLine=[]
    # #dla węzła startowego nie ma żadnej lini, którą przyjechaliśmy, więc tego nie sprawdzamy
    # if(not node['departureLine']==None):
    #     for edge in edgesWithTheSameEnd:
    #         if(f'{edge._company()} {edge._line()}'==node['departureLine']): #departureLine, to linia, którą się przyjechało do node (bo kolejne węzły zapamiętują poprzednie krawędzie)
    #             edgesWithTheSameLine.append(edge)

    
    # #jeżeli są połączenia tą samą linia...
    # edgesWithTheSameLineInTheFutureIndex=None
    # if len(edgesWithTheSameLine)>0:
    #     #staramy się znaleźć najszybsze z nich, które jest w przyszłości tego samego dnia
    #     for i in range(len(edgesWithTheSameLine)):
    #         if edgesWithTheSameLine[i]._departure_time()>=nodeFromTime:
    #             edgesWithTheSameLineInTheFutureIndex=i
    #             break
        
    #     #jeżeli są jakieś w przyszłości tego samego dnia...
    #     if not edgesWithTheSameLineInTheFutureIndex==None:
    #         #ponieważ edgesWithTheSameEnd jest posortowane czasem wyjazdu, pozostałe tablice też będą
    #         #szukamy linii z najszybszym przyjazdem (ale z przyjazdem w tym samym dniu)
    #         chosenEdgeWithTheSameLine=chooseEdgeWithFastestArrival(edgesWithTheSameLine[edgesWithTheSameLineInTheFutureIndex:len(edgesWithTheSameLine)], nodeFromTime)

    #     #jeżeli nie, wybieramy z tych następnego dnia (czyli z całej tablicy, bo wtedy wszystkie edge są następnego dnia)
    #     else:
    #         chosenEdgeWithTheSameLine=chooseEdgeWithFastestArrival(edgesWithTheSameLine)


    #sprawdzamy ogólnie najszybsze połączenie z tych, co są w przyszłości
    #więc najpierw odsiewamy wszystkie, które są w przyszłości
    edgesWithTheSameEndInTheFutureIndex=None
    for i in range(len(edgesWithTheSameEnd)):
        if edgesWithTheSameEnd[i]._departure_time()>=nodeFromTime:
            edgesWithTheSameEndInTheFutureIndex=i
            break
    
    #jeżeli są jakieś w przyszłości tego samego dnia...
    if not edgesWithTheSameEndInTheFutureIndex==None:
        #(ponieważ edgesWithTheSameEnd jest posortowane czasem wyjazdu, pozostałe tablice też będą)
        #szukamy linii z najszybszym przyjazdem (ale z tych, których odjazd jest przed północą)
        chosenEdge=chooseEdgeWithFastestArrival(edgesWithTheSameEnd[edgesWithTheSameEndInTheFutureIndex:len(edgesWithTheSameEnd)], nodeFromTime)

    #jeżeli nie, wybieramy z tych następnego dnia (czyli z całej tablicy, bo wtedy wszystkie edge są następnego dnia)
    else:
        chosenEdge=chooseEdgeWithFastestArrival(edgesWithTheSameEnd)

    # #Poniższego jednak nie
    # #sprawdzamy, czy najszybsze połączenie z tą samą linią, jest faktycznie jednym z najszybszych możliwych połączeń
    # #przyjazd chosenEdge jest na pewno najszybszym z możliwych
    # #I warunek: szybszy przyjazd
    # if(chosenEdgeWithTheSameLine._arrival_time()<=chosenEdge._arrival_time()):
    #     #II warunek: czy w obu przypadkach wyjazd jest tego samego dnia, co przyjazd
    #     if(chosenEdgeWithTheSameLine._departure_time()<chosenEdgeWithTheSameLine._arrival_time() and chosenEdge._departure_time()<chosenEdge._arrival_time()):

    #zwracamy różnicę czasu i wybrane połączenie
    chosenEdgeArrTime=hourToSeconds(chosenEdge._arrival_time()) #tutaj muszą być posortowane
    return [abs(chosenEdgeArrTime - hourToSeconds(node['arrivalTime'])), chosenEdge]

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

# def calculateHTime(normalizedNodeFrom, normalizedNodeTo, graph):
#     #TODO: stwórz funkcję, konwertującą szerokość kątową na kilometry (żeby móc obliczyć przewidywany czas do celu)
#     mpkBusAvgVelocity=21.3
#     return (math.sqrt((normalizedNodeFrom['averageLon'] - 
#             normalizedNodeTo['averageLon'])**2 + 
#             (normalizedNodeFrom['averageLat'] - 
#             normalizedNodeTo['averageLat'])**2))

    
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