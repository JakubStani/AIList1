from edge import Edge
from node import Node
from djkNode import DjkNode
from aStarNode import AStarNode
import math
from datetime import datetime
import time


#Graf buduje się właściwie
def buildGraphFromCSV(csvFileName):
    # graph=[dict(),[]]
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
                # graph[1].append(edge)
                # if(not (f'{start_node._stop_name()}{start_node._stop_lat()}{start_node._stop_lon()}' in graph[0])):
                #     graph[0][f'{start_node._stop_name()}{start_node._stop_lat()}{start_node._stop_lon()}']=start_node
                # if(not (f'{end_node._stop_name()}{end_node._stop_lat()}{end_node._stop_lon()}' in graph[0])):
                #     graph[0][f'{end_node._stop_name()}{end_node._stop_lat()}{end_node._stop_lon()}']=end_node

                #add to normalized graph to get average location of stop
                    #ta funkcja jest sprawdzona i wykonuje się właściwie
                normalizedGraph = addToNormalizedGraph(edge, normalizedGraph)
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

def djikstraAlg(source, graph):
    # djkSource= DjkNode(getNodeFromNodes(source, nodes), 0)
    # djkNodes = dict()

    # #add d value to nodes
    # for node in nodes:
    #     if(node._stop_name() != source):
    #         djkNodes[node._stop_name()] = DjkNode(node)
    #     else:
    #         djkNodes[source] == djkSource

    pass



def getNodeFromNodes(searched_node_name, nodes):
    if searched_node_name in nodes:
        return nodes[searched_node_name]

#chcemy otrzymać: czy będzie przesiadka, i edge możliwie bez przesiadki
def getChanges(node, node_next_normalized_graph):
    change=0
    nodeFromTime = node['arrivalTime']
    edgesToCheck=[] #TODO: tu się przyda sortowanie przez wstawianie !!!!!!!!!!!!!!!!!!


    for edge in node['edges']:
        if(edge._end_node()._stop_name()==node_next_normalized_graph['name']):
            if(edge._departure_time()==nodeFromTime and f'{edge._company()} {edge._line()}'==node['arrivalLine']):
                return [change, edge]
            else:
                edgesToCheck=addToSortedEdgesList(edge, edgesToCheck) #tutaj nie zależy nam na czasie, a jedynie na tej samej linii
    
    chosenEdge = None
    if (not node['arrivalLine']==None):
        for edge in edgesToCheck:
            if edge._departure_time()>nodeFromTime and f'{edge._company()} {edge._line()}' == node['arrivalLine']: #nie =, bo to już było sprawdzone
                chosenEdge=edge
                break
    else:
        for edge in edgesToCheck:
            if edge._departure_time()>nodeFromTime:
                change=1
                chosenEdge=edge
                break
    if chosenEdge==None:
        for edge in edgesToCheck:
            if edge._departure_time()>nodeFromTime:
                chosenEdge=edge
                change=1
                break

    if chosenEdge==None:
        # if not node['arrivalLine']==None:
        change=1
        chosenEdge=edgesToCheck[0]
    # chosenEdgeArrTime=hourToSeconds(chosenEdge._arrival_time()) #tutaj muszą być posortowane
    return [change, chosenEdge]

def calculateHChange(node_next_normalized_graph, end, graph):
    distanceKm=calculateHDistance(node_next_normalized_graph, end, graph)
    return node_next_normalized_graph['g/hFFS']*distanceKm



# #WAŻNE!: zawsze przystanek, z którego wysiadamy jest przystankiem, na którym wsiadamy
def printSolution(node):
    if(node['parent']==None):
        print(f' {node['edgeId']} Przystanek: {node['name']}, liczba przesiadek: {node['g']}, \
              czas pojawienia się na przystanku: {node['arrivalTime']}, \
                odjazd z tego przystanku: {node['departureTime']} linią {node['departureLine']}')
    else:
        printSolution(node['parent'])
        print(f' -> {node['edgeId']} Przystanek: {node['name']} liczba przesiadek: {node['g']}, \
              przyjazd: {node['arrivalTime']}, \
                odjazd z tego przystanku: {node['departureTime']} \
                    linią {node['departureLine']}')

# # TODO: g to koszt dotarcia, a koszt dotarcia do startu powinien wynosić 0 !!! (popra to jakoś, może np. normalizuj od danej godziny)
mpkBusAvgVelocity=21.3
# #nowa wersja -> heurystyka to czas (i g też)
# def aStarAlgTime(start, end, graph, startTime): #start i end to znormalizowane węzły

#     list_open=[]
#     list_closed=[]

#     start['g']=0 #startTime #tutaj jest zmiana, bo musimy być o którejś godzinie
#     start['arrivalTime']=secondsToHour(startTime)
#     print(f'start time: {secondsToHour(startTime)} {startTime}= startTime')
#     start['h']=0
#     start['f']=start['g']+start['h']


#     list_open=[start]

#     while len(list_open) > 0:
#         node = None #to będzie znormalizowany węzeł
#         node_cost=float('inf')

#         for test_node in list_open:
#             if (test_node['f']<node_cost):
#                 node = test_node
#                 node_cost = test_node['f']
#         if node['name'] == end['name']:
#             #print(f'Rozwiazanie:{list(map(lambda x: x["name"], list_closed))}')
#             #print(f'otwarta lista:{list(map(lambda x: x["name"], list_open))}')
#             print('Rozwiązanie:')
#             printSolution(node)
#             break

#         #TODO: be able to find this node
#         list_open.remove(node)
#         list_closed.append(node)

#         #tu się zaczynają problemy z sąsiadami, bo info o sąsiadach ma normalized graph, a tam nie ma AstarNodów
#         #tutaj node next ma być AStarNodem, tylko jak go utworzyć?
#         for node_next_name in node['neighbours']:
#             #szukam po nazwie, bo node_next nie jest AStarNodem
#             node_next_normalized_graph=graph[node_next_name]
#             if (node_next_normalized_graph not in list_open and node_next_normalized_graph not in list_closed): #TODO: be able to fin this node
#                 nnH=calculateHTime(node_next_normalized_graph, end, graph)
#                 #TODO: czy trzeba zrobić z czasem? Jak tak, to wtedy trzeba stworzyć calculate h time
#                 gTDResult=getTimeDiff(node, node_next_normalized_graph)
#                 nnG=node['g'] + gTDResult[0]
#                 node_next_normalized_graph['h']=nnH
#                 node_next_normalized_graph['g']=nnG
#                 # node_next_normalized_graph['gString']=secondsToHour(nnG)
#                 node_next_normalized_graph['f']=nnH + nnG
#                 node_next_normalized_graph['parent']=node
#                 node_next_normalized_graph['arrivalTime']=gTDResult[1]._arrival_time()
#                 node['departureTime']=gTDResult[1]._departure_time()
#                 node['departureLine']=f'{gTDResult[1]._company()} {gTDResult[1]._line()}'
#                 node['edgeId']=gTDResult[1]._id()
#                 list_open.append(node_next_normalized_graph)
#             else:
#                 #co tu się dokładnie dzieje?
#                 gTDResult=getTimeDiff(node,node_next_normalized_graph)
#                 if(node_next_normalized_graph['g']>node['g'] + gTDResult[0]):
#                     node_next_normalized_graph['g']=node['g'] +gTDResult[0]
#                     node['departureTime']=gTDResult[1]._departure_time()
#                     node['departureLine']=f'{gTDResult[1]._company()} {gTDResult[1]._line()}'
#                     node['edgeId']=gTDResult[1]._id()
#                     node_next_normalized_graph['arrivalTime']=gTDResult[1]._arrival_time()
#                     # node_next_normalized_graph['gString']=secondsToHour(node_next_normalized_graph['g'])
#                     node_next_normalized_graph['parent']=node
#                     node_next_normalized_graph['f']=node_next_normalized_graph['g']+node_next_normalized_graph['h']
#                     if(node_next_normalized_graph in list_closed): #TODO: trzeba móc odnaleźć tego noda w liście
#                         list_open.append(node_next_normalized_graph)
#                         list_closed.remove(node_next_normalized_graph) #TODO: trzeba móc odnaleźć noda
            #print(f'{node['name']} {node['edgeId']}')
            
    #print(f'Lista zamknięta:{list(map(lambda x: x["name"], list_closed))}')
    #print(f'Lista otwarta:{list(map(lambda x: x["name"], list_open))}')

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

    #WERSJA DZIAŁAJĄCA:
    for edge in node['edges']:
        if(edge._end_node()._stop_name()==node_next_normalized_graph['name']):
            if not len(edge._departure_time())==len(nodeFromTime):
                print('Niezgodna dlugosc dat! 290')
            if(edge._departure_time()==nodeFromTime):
                return [edge._time_diff(), edge]
            else:
                edgesToCheck=addToSortedEdgesList(edge, edgesToCheck)
    #wstawiłem ten powyższy wiersz
    #             if(edge._departure_time()>nodeFromTime):
    #                 edgesInTheFuture.append(edge)
    # if(len(edgesInTheFuture)>0):
    #     chosenEdgeArrTime=datetime.strptime(edgesInTheFuture[0]._arrival_time(), "%H:%M:%S").second #tutaj muszą być posortowane
    #     return abs(chosenEdgeArrTime - nodeFromTimeSeconds)
    #
    # else:
    #     #trzeba wybrać pierwszą, która się trafi (czyli np. następnego dnia)
    #     pass
    
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

    #WERSJA NIEDZIAŁAJĄCA:
    # for edge in node['edges']:
    #     if(edge._end_node()._stop_name()==node_next_normalized_graph['name']):
    #             edgesToCheck=addToSortedEdgesList(edge, edgesToCheck)


    # chosenEdge = None
    # #jeżeli na przystanek dojedziemy już po wszystkich kursach danego dnia, 
    # #będziemy musieli poczekać do najbliższego następnego dnia
    # earliestEdgeInTheDay=edgesToCheck[0]

    # #mówi gdzie zacznie się pierwszy edge z wyjazdem w przyszłości (lub równym naszemu przyjazdowi na start tego edga)
    # pivot=None
    # for i in range(len(edgesToCheck)):
    #     if edgesToCheck[i]._departure_time()>node['arrivalTime']:
    #         pivot=i
    #         break
    # earliestArrivalInGeneral='23:59:59'
    # posOfEAG=None
    # earliestArrivalInTheSameLine='23:59:59'
    # posOfEAITS=None

    # #jeżeli przyjechaliśmy i w danym dniu jeszcze jest jakiś kurs na tym edgu
    # if not pivot==None:
    #     #sprawdzamy, którym edgem dojedziemy najszybciej i staramy się, aby byłą to ta sama linia, którą przyjechaliśmy (ale nie musi być ta sama)
    #     for l in range(pivot, len(edgesToCheck)):
    #         #print(f'art: {edgesToCheck[l]._arrival_time()}, eaig: {earliestArrivalInGeneral} {edgesToCheck[l]._arrival_time()<=earliestArrivalInGeneral}')
    #         if edgesToCheck[l]._arrival_time()<=earliestArrivalInGeneral:
    #             earliestArrivalInGeneral=edgesToCheck[l]._arrival_time()
    #             posOfEAG=l
    #         if(not node['arrivalLine'] ==None):
    #             if edgesToCheck[l]._arrival_time()<=earliestArrivalInTheSameLine and f'{edgesToCheck[l]._company()} {edgesToCheck[l]._line()}' == node['arrivalLine']:
    #                 earliestArrivalInTheSameLine=edgesToCheck[l]._arrival_time()
    #                 posOfEAITS=l

    #     #sprawdzamy, który edge okazał się najlepszym wyborem
    #     if((not posOfEAG==None) and not (posOfEAITS == None)):
    #         if(earliestArrivalInTheSameLine==earliestArrivalInGeneral):
    #             chosenEdge=edgesToCheck[posOfEAITS]
    #         else:
    #             chosenEdge=edgesToCheck[posOfEAG]
    #     else:
    #         # if(posOfEAG==None):
    #         #     print(str(edgesToCheck[len(edgesToCheck)-1]))
    #         chosenEdge=edgesToCheck[posOfEAG]  

    # #jeżeli w danym dniu nie ma już kursu na tym edgu
    # else:
    #     chosenEdge=edgesToCheck[0]

    # # for edge in edgesToCheck:
    # #     if edge._departure_time()>nodeFromTime:
    # #         chosenEdge=edge
    # #         break
    # if chosenEdge==None:
    #     chosenEdge=edgesToCheck[0]
    # chosenEdgeArrTime=hourToSeconds(chosenEdge._arrival_time()) #tutaj muszą być posortowane
    # return [abs(chosenEdgeArrTime - hourToSeconds(node['arrivalTime'])), chosenEdge]
    # ###
    


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
    

# #nowa wersja -> działa właściwie; heurystyka to odległość (i g też)
# def aStarAlg(start, end, graph): #start i end to znormalizowane węzły

#     list_open=[]
#     list_closed=[]

#     start['g']=0
#     start['h']=0
#     start['f']=start['g']+start['h']


#     list_open=[start]

#     while len(list_open) > 0:
#         node = None #to będzie znormalizowany węzeł
#         node_cost=float('inf')

#         for test_node in list_open:
#             if (test_node['f']<node_cost):
#                 node = test_node
#                 node_cost = test_node['f']
#         if node['name'] == end['name']:
#             #print(f'Rozwiazanie:{list(map(lambda x: x["name"], list_closed))}')
#             #print(f'otwarta lista:{list(map(lambda x: x["name"], list_open))}')
#             print('Rozwiązanie:')
#             printSolution(node)
#             break

#         #TODO: be able to find this node
#         list_open.remove(node)
#         list_closed.append(node)

#         #tu się zaczynają problemy z sąsiadami, bo info o sąsiadach ma normalized graph, a tam nie ma AstarNodów
#         #tutaj node next ma być AStarNodem, tylko jak go utworzyć?
#         for node_next_name in node['neighbours']:
#             #szukam po nazwie, bo node_next nie jest AStarNodem
#             node_next_normalized_graph=graph[node_next_name]
#             if (node_next_normalized_graph not in list_open and node_next_normalized_graph not in list_closed): #TODO: be able to fin this node
#                 nnH=calculateHDistance(node_next_normalized_graph, end, graph)
#                 #TODO: czy trzeba zrobić z czasem? Jak tak, to wtedy trzeba stworzyć calculate h time
#                 nnG=node['g'] + getDistance(node, node_next_normalized_graph)
#                 node_next_normalized_graph['h']=nnH
#                 node_next_normalized_graph['g']=nnG
#                 node_next_normalized_graph['f']=nnH + nnG
#                 node_next_normalized_graph['parent']=node
#                 list_open.append(node_next_normalized_graph)
#             else:
#                 if(node_next_normalized_graph['g']>node['g'] + getDistance(node,node_next_normalized_graph)):
#                     node_next_normalized_graph['g']=node['g'] +getDistance(node,node_next_normalized_graph)
#                     node_next_normalized_graph['parent']=node
#                     node_next_normalized_graph['f']=node_next_normalized_graph['g']+node_next_normalized_graph['h']
#                     if(node_next_normalized_graph in list_closed): #TODO: trzeba móc odnaleźć tego noda w liście
#                         list_open.append(node_next_normalized_graph)
#                         list_closed.remove(node_next_normalized_graph) #TODO: trzeba móc odnaleźć noda
#     #print(f'Lista zamknięta:{list(map(lambda x: x["name"], list_closed))}')
#     #print(f'Lista otwarta:{list(map(lambda x: x["name"], list_open))}')
    
# #WAŻNE!: zawsze przystanek, z którego wysiadamy jest przystankiem, na którym wsiadamy
# def printSolution(node):
#     if(node['parent']==None):
#         print(f' {node['edgeId']} Przystanek: {node['name']}, \
#               czas pojawienia się na przystanku: {secondsToHour(node['g'])}, \
#                 odjazd z tego przystanku: {node['departureTime']} linią {node['departureLine']}')
#     else:
#         printSolution(node['parent'])
#         print(f' -> {node['edgeId']} Przystanek: {node['name']}, \
#               przyjazd: {secondsToHour(node['g'])}, \
#                 odjazd z tego przystanku: {node['departureTime']} \
#                     linią {node['departureLine']}')
        

#poprzednia wersja
#A*
#problem do naprawienia-> możliwe, że wśród neighbours są przystanki o tych samych nazwach, a tak nie powinno być
# def aStarAlg(start, end, graph): #start i end to znormalizowane węzły

#     list_open=[]
#     list_closed=[]

#     startG=0
#     startH=0
#     startNode=AStarNode(
#         start['name'],
#         start['averageLat'],
#         start['averageLon'],
#         startG+startH,
#         startH,
#         startG
#     )

#     list_open=[startNode]

#     while len(list_open) > 0:
#         node = None #to będzie znormalizowany węzeł
#         node_cost=float('inf')

#         for test_node in list_open:
#             if test_node._f()<node_cost:
#                 node = test_node
#                 node_cost = test_node._f()
#         if node._stop_name() == end['name']:
#             print(f'Rozwiazanie:{list(map(lambda x: x._stop_name(), list_closed))}')
#             print(f'otwarta lista:{list(map(lambda x: x._stop_name(), list_open))}')
#             break

#         #TODO: be able to find this node
#         list_open.remove(node)
#         list_closed.append(node)

#         #tu się zaczynają problemy z sąsiadami, bo info o sąsiadach ma normalized graph, a tam nie ma AstarNodów
#         #tutaj node next ma być AStarNodem, tylko jak go utworzyć?
#         for node_next_name in graph[node._stop_name()]['neighbours']:
#             #szukam po nazwie, bo node_next nie jest AStarNodem
#             node_next_normalized_graph=graph[node_next_name]
#             if node_next_name not in list(map(lambda x: x._stop_name(), list_open)) and node_next_name not in list(map(lambda x: x._stop_name(), list_closed)): #TODO: be able to fin this node
#                 nnH=calculateHDistance(node_next_normalized_graph, end, graph)
#                 #TODO: czy trzeba zrobić z czasem? Jak tak, to wtedy trzeba stworzyć calculate h time
#                 nnG=node._g() + getDistance(graph[node._stop_name()], node_next_normalized_graph)
#                 node_next=AStarNode(
#                     node_next_normalized_graph['name'],
#                     node_next_normalized_graph['averageLat'],
#                     node_next_normalized_graph['averageLon'],
#                     nnH+nnG,
#                     nnH,
#                     nnG
#                 )

#                 list_open.append(node_next)
#             else:
#                 if(node_next_name not in list(map(lambda x: x._stop_name(), list_open))):
#                     node_next = getNodeFromList(node_next_name, list_closed)
#                 else:
#                     node_next = getNodeFromList(node_next_name, list_open)
                    
#                 if(node_next._g()>node._g() + getDistance(graph[node._stop_name()],node_next_normalized_graph)):
#                     node_next.setG(node._g() +getDistance(graph[node._stop_name()],node_next_normalized_graph))
#                     node_next.setF(node_next._g() + node_next._h())
#                     if(node_next in list_closed): #TODO: trzeba móc odnaleźć tego noda w liście
#                         list_open.append(node_next)
#                         list_closed.remove(node_next) #TODO: trzeba móc odnaleźć noda

def getNodeFromList(node_name, list):
    for nn in list:
        if nn._stop_name()==node_name:
            return nn

#Chcemy brać dystans, czy czas?
def getDistance(node, node_next):
    for edge in node['edges']:
        if(edge._end_node()._stop_name()==node_next['name']):
            return edge._distance()
    print(f"Nie udalo się dla: {list(map(lambda x: x._end_node()._stop_name(), node['edges']))} i {node_next['name']}, a przystanek to {node['name']}")
        
# def getTime(node, node_next):
#     for edge in node['edges']:
#         if(edge._end_node()._stop_name()==node_next['normalizedNode']['name']):
#             return edge._time_diff()

def calculateHDistance(normalizedNodeFrom, normalizedNodeTo, graph):
    # to trzeba zmienić na km
    # return (math.sqrt((normalizedNodeFrom['averageLon'] - 
    #         normalizedNodeTo['averageLon'])**2 + 
    #         (normalizedNodeFrom['averageLat'] - 
    #         normalizedNodeTo['averageLat'])**2))

    return (math.acos(math.sin(normalizedNodeFrom['averageLat'])*math.sin(normalizedNodeTo['averageLat']) +
            math.cos(normalizedNodeFrom['averageLat']) * math.cos(normalizedNodeTo['averageLat']) * 
            math.cos(normalizedNodeTo['averageLon'] - normalizedNodeFrom['averageLon']))*6371)

def calculateHTime(normalizedNodeFrom, normalizedNodeTo, graph):
    #TODO: stwórz funkcję, konwertującą szerokość kątową na kilometry (żeby móc obliczyć przewidywany czas do celu)
    mpkBusAvgVelocity=21.3
    return (math.sqrt((normalizedNodeFrom['averageLon'] - 
            normalizedNodeTo['averageLon'])**2 + 
            (normalizedNodeFrom['averageLat'] - 
            normalizedNodeTo['averageLat'])**2))


#heurystyka to przesiadki (i g też)
def aStarAlgChange(start, end, graph, startTime): #start i end to znormalizowane węzły

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
            print('Rozwiązanie:')
            printSolution(node)
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
                node['departureTime']=gCh[1]._departure_time() #!!!
                node['departureLine']=gCh[1]._line() #!!!
                node['edgeId']=gCh[1]._id() #!!!
                node_next_normalized_graph['arrivalTime']=gCh[1]._arrival_time() #!!!
                node_next_normalized_graph['arrivalLine']=f'{gCh[1]._company()} {gCh[1]._line()}' #!!!
                
                list_open.append(node_next_normalized_graph)
            else:
                if(node_next_normalized_graph['g']>node['g'] + gCh[0]):
                    node_next_normalized_graph['g']=node['g'] + gCh[0]
                    node_next_normalized_graph['howFarFromStart']=node['howFarFromStart'] + gCh[1]._distance()
                    node_next_normalized_graph['g/hFFS']=(node_next_normalized_graph['g'])/node_next_normalized_graph['howFarFromStart'] 
                    node_next_normalized_graph['h']=calculateHChange(node_next_normalized_graph, end, graph)
                    node_next_normalized_graph['parent']=node
                    node_next_normalized_graph['f']=node_next_normalized_graph['g']+node_next_normalized_graph['h']
                    node['departureTime']=gCh[1]._departure_time()
                    node['departureLine']=gCh[1]._line()
                    node['edgeId']=gCh[1]._id()
                    node_next_normalized_graph['arrivalTime']=gCh[1]._arrival_time()
                    node_next_normalized_graph['arrivalLine']=f'{gCh[1]._company()} {gCh[1]._line()}'
                    if(node_next_normalized_graph in list_closed): #TODO: trzeba móc odnaleźć tego noda w liście
                        list_open.append(node_next_normalized_graph)
                        list_closed.remove(node_next_normalized_graph) #TODO: trzeba móc odnaleźć noda
                        
# mpkBusAvgVelocity=21.3
# #nowa wersja -> heurystyka to czas (i g też)
# def aStarAlgTime(start, end, graph, startTime): #start i end to znormalizowane węzły

#     list_open=[]
#     list_closed=[]

#     start['g']=0 #startTime #tutaj jest zmiana, bo musimy być o którejś godzinie
#     start['arrivalTime']=secondsToHour(startTime)
#     print(f'start time: {secondsToHour(startTime)} {startTime}= startTime')
#     start['h']=0
#     start['f']=start['g']+start['h']


#     list_open=[start]

#     while len(list_open) > 0:
#         node = None #to będzie znormalizowany węzeł
#         node_cost=float('inf')

#         for test_node in list_open:
#             if (test_node['f']<node_cost):
#                 node = test_node
#                 node_cost = test_node['f']
#         if node['name'] == end['name']:
#             print('Rozwiązanie:')
#             printSolution(node)
#             break

#         #TODO: be able to find this node
#         list_open.remove(node)
#         list_closed.append(node)

#         #tu się zaczynają problemy z sąsiadami, bo info o sąsiadach ma normalized graph, a tam nie ma AstarNodów
#         #tutaj node next ma być AStarNodem, tylko jak go utworzyć?
#         for node_next_name in node['neighbours']:
#             node_next_normalized_graph=graph[node_next_name]
#             if (node_next_normalized_graph not in list_open and node_next_normalized_graph not in list_closed): #TODO: be able to fin this node
#                 nnH=calculateHTime(node_next_normalized_graph, end, graph)
#                 gTDResult=getTimeDiff(node, node_next_normalized_graph)
#                 nnG=node['g'] + gTDResult[0]
#                 node_next_normalized_graph['h']=nnH
#                 node_next_normalized_graph['g']=nnG
#                 # node_next_normalized_graph['gString']=secondsToHour(nnG)
#                 node_next_normalized_graph['f']=nnH + nnG
#                 node_next_normalized_graph['parent']=node
#                 node_next_normalized_graph['arrivalTime']=gTDResult[1]._arrival_time()
#                 node['departureTime']=gTDResult[1]._departure_time()
#                 node['departureLine']=f'{gTDResult[1]._company()} {gTDResult[1]._line()}'
#                 node['edgeId']=gTDResult[1]._id()
#                 list_open.append(node_next_normalized_graph)
#             else:
#                 #co tu się dokładnie dzieje?
#                 gTDResult=getTimeDiff(node,node_next_normalized_graph)
#                 if(node_next_normalized_graph['g']>node['g'] + gTDResult[0]):
#                     node_next_normalized_graph['g']=node['g'] +gTDResult[0]
#                     node['departureTime']=gTDResult[1]._departure_time()
#                     node['departureLine']=f'{gTDResult[1]._company()} {gTDResult[1]._line()}'
#                     node['edgeId']=gTDResult[1]._id()
#                     node_next_normalized_graph['arrivalTime']=gTDResult[1]._arrival_time()
#                     # node_next_normalized_graph['gString']=secondsToHour(node_next_normalized_graph['g'])
#                     node_next_normalized_graph['parent']=node
#                     node_next_normalized_graph['f']=node_next_normalized_graph['g']+node_next_normalized_graph['h']
#                     if(node_next_normalized_graph in list_closed): #TODO: trzeba móc odnaleźć tego noda w liście
#                         list_open.append(node_next_normalized_graph)
#                         list_closed.remove(node_next_normalized_graph) #TODO: trzeba móc odnaleźć noda


if __name__=='__main__':
    normalizedGraph=buildGraphFromCSV('connection_graph.csv')
    #print(normalizedGraph)
    #print(normalizedGraph['Broniewskiego'])
    #print(normalizedGraph['Trzebnicka'])
    #print(normalizedGraph['Siedlec - skrzy. Osiedlowa'])
    while True:
        start=input('Podaj przystanek początkowy:')
        end=input('Podaj przystanek końcowy:')

        #IMP: kod z gemini konwertujący czas ze stringa w sekundy
        startTime=hourToSeconds(input('Podaj czas wyjazdu'))
        tOrP=input('Wybierz opcję: t- minimalizacja czasu, p- minimalizacja przesiadek')
        # try:
        startNormalized=normalizedGraph[start]
        endNormalized=normalizedGraph[end]
        # if(tOrP=='t'):
        #aStarAlgTime(startNormalized, endNormalized, normalizedGraph, startTime)
        #if(tOrP=='p'):
        aStarAlgChange(startNormalized, endNormalized, normalizedGraph, startTime)
        # except KeyError:
        #     print('Nieprawidłowe dane wejściowe')
        option=input('Press "c" to continue or "s" to stop')
        if(option=='s'):
            break
        else:
            for node in normalizedGraph:
                normalizedGraph[node]['f']=None
                normalizedGraph[node]['g']=None
                # normalizedGraph[node]['gString']=None
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


