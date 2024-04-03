from edge import Edge
from node import Node
from djkNode import DjkNode
from aStarNode import AStarNode
import math
from datetime import datetime
import time
import sys

###     wspólna dla wszystkich algorytmów funkcja budująca  graf
#funkcja budująca graf
#jako parametr podajemy nazwę pliku csv,
#z którego pobieramy dane dotyczące połączeń
def buildGraphFromCSV(csvFileName):
    
    #graf -> jest słownikiem, który będzie przechowywał 
    #dane węzłów (w tym krawędzi, które je łączą)
    normalizedGraph=dict()

    #pobieramy dane z pliku i przetwarzamy je (budujemy graf)
    with open(csvFileName,  encoding="UTF-8") as file:

        #dla każdej linijki pliku
        for dataLine in file:

            #w pliku csv dane oddzielone są przecinkiem
            dataLine=dataLine.split(',')

            #jeżeli pierwszy znak linii jest pustym napisem,
            #oznacza to, że linią jest wiersz z nazwami kolumn,
            #on nie zawiera danych, które potrzebujemy, więc go pomijamy
            if dataLine[0]!='':
                
                #tworzymy instancje węzła początkowego 
                #i końcowego (danej krawędzi/połączenia)    
                start_node = Node(dataLine[5], float(dataLine[7]), float(dataLine[8]))
                end_node = Node(dataLine[6], float(dataLine[9]), float(dataLine[10]))

                #tworzymy instancję krawędzi
                #wykorzystujemy "validateTime",
                #aby poprawić błędne zapisy czasu
                #oraz dodać 0 na początku,
                #jeżeli go brak (czas w formacie HH:MM:SS)
                edge = Edge(
                    dataLine[0],
                    dataLine[1],
                    dataLine[2],
                    validateTime(dataLine[3]),
                    validateTime(dataLine[4]),
                    start_node,
                    end_node
                )

                #korzystamy z "addToNormalizedGraph", 
                #aby odpowiednio ustrukturyzować normalizedGraph
                normalizedGraph = addToNormalizedGraph(edge, normalizedGraph)

        #dla każdego klucza (którym jest nazwa węzła)
        #obliczamy uśrednione współrzędne geograficzne
        for key in normalizedGraph:
            averageLon=0 #x
            averageLat=0 #y

            #(uśrednione dane na podstawie wielu węzłów-przystanków
            #o tej samej nazwie, lecz różnych współrzędnych ->
            #są one przechowywane pod kluczem "nodes" danego węzła)
            for node in normalizedGraph[key]['nodes']:

                averageLon+=node._stop_lon()
                averageLat+=node._stop_lat()

            averageLon/=len(normalizedGraph[key]['nodes'])
            averageLat/=len(normalizedGraph[key]['nodes'])
            
            #ustawienie uśrednionych współrzędnych węzłowi
            normalizedGraph[key]['averageLon']=averageLon
            normalizedGraph[key]['averageLat']=averageLat

    #zwracamy znormalizowany graf
    return normalizedGraph

#poprawia błędne zapisy czasu
#oraz dodaje 0 na początku,
#jeżeli go brak (czas w formacie HH:MM:SS)
def validateTime(time):
    time=time.split(':')
    time[0]=int(time[0])

    #za pomocą modulo upewniamy się,
    #że godzina nie będzie większa niz 23
    #(z testów wyszło, że w danych z "connection_graph.csv"
    #tylko godzina ma nieprawidłowe wystąpienia,
    #więc nie musimy sprawdzać poprawności minut i sekund)
    time[0]=str(time[0]%24)

    #dodajemy 0 na przodzie, jeżeli go nie ma
    if(len(time[0])==1):
        time[0]=f'0{time[0]}'

    #zwracamy datę w poprawnym 
    #dla nas (dla dalszych obliczeń) formacie
    return f'{time[0]}:{time[1]}:{time[2]}'


#odpowiednio strukturyzuje normalizedGraph
#jako parametry przyjmuje krawędź i znormalizowany graf
def addToNormalizedGraph(edge, normalizedGraph):

    #jeżeli początkowego węzła (nazwy tego przystanku) danej krawędzi 
    #nie ma jeszcze w grafie (jako klucz), dodajemy go 
    #za pomocą "addNewNodeToNormG"
    if(not(edge._start_node()._stop_name() in normalizedGraph)):
        # #stary zapis
        # normalizedGraph[edge._start_node()._stop_name()]={
        #     'nodes': [edge._start_node()],
        #     'edges': [edge],
        #     'neighbours': set([edge._end_node()._stop_name()]),
        #     'name': edge._start_node()._stop_name(),
        #     'f': None,
        #     'g':None,
        #     'h':None,
        #     'parent':None,
        #     'departureTime': None,
        #     'departureLine': None,
        #     'arrivalLine': None,
        #     'arrivalTime': None,
        #     'edgeId': None,
        #     'howFarFromStart': None,
        #     'g/hFFS': None
        #     }
        
        #nowy zapis
        normalizedGraph=addNewNodeToNormG(
            edge._start_node()._stop_name(), 
            [edge._start_node()], [edge], 
            set([edge._end_node()._stop_name()]), 
            normalizedGraph
            )
    else:
        #jeżeli początkowy węzeł (nazwa tego przystanku) danej krawędzi jest w grafie
        #ale nie ma go (tego konkretnego) w zbiorze węzłów "nodes", to go dodajemy
        if(edge._start_node() not in normalizedGraph[edge._start_node()._stop_name()]['nodes']):
            normalizedGraph[edge._start_node()._stop_name()]['nodes'].append(edge._start_node())

        #krawędź dodajemy tak czy owak, ponieważ każda jest unikalna
        normalizedGraph[edge._start_node()._stop_name()]['edges'].append(edge)

        #jeżeli tego konkretnego węzła nie ma w zbiorze sąsiadów "neighbours", to zostanie dodany
        normalizedGraph[edge._start_node()._stop_name()]['neighbours'].add(edge._end_node()._stop_name())
        
    #na koniec dodajemy jeszcze końcowy węzeł danej krawędzi,
    #korzystając z "addEndNodeToNormalizedGraph"
    return addEndNodeToNormalizedGraph(edge._end_node(),normalizedGraph, edge)

#dodaje węzeł (końcowy pewnej krawędzi), zachowujac odpowiednią
#strukturę znormalizowanego grafu
def addEndNodeToNormalizedGraph(end_node, normalizedGraph, edge):

    #jeżeli końcowego węzła (nazwy tego przystanku) danej krawędzi 
    #nie ma jeszcze w grafie (jako klucz), dodajemy go 
    #za pomocą "addNewNodeToNormG"
    if(not(end_node._stop_name() in normalizedGraph)):
        # #poprzedni zapis
        # normalizedGraph[end_node._stop_name()]={
        #     'nodes': [end_node],
        #     'edges': [],
        #     'neighbours': set(),
        #     'name': end_node._stop_name(),
        #     'f': None,
        #     'g':None,
        #     'h':None,
        #     'parent':None,
        #     'departureTime': None,
        #     'departureLine': None,
        #     'arrivalLine': None,
        #     'arrivalTime': None,
        #     'edgeId': None,
        #     'howFarFromStart': None,
        #     'g/hFFS': None
        #     }
        
        #nowy zapis
        normalizedGraph=addNewNodeToNormG(
            end_node._stop_name(), 
            [end_node], 
            [], 
            set(),normalizedGraph
            )
    else:
        #jeżeli końcowy węzeł (nazwa tego przystanku) danej krawędzi jest w grafie
        #ale nie ma go (tego konkretnego) w zbiorze węzłów "nodes", to go dodajemy
        if(end_node not in normalizedGraph[end_node._stop_name()]['nodes']):
            normalizedGraph[end_node._stop_name()]['nodes'].append(end_node)

    #zwracamy graf z dodanym węzłem
    return normalizedGraph

###nowe
#tworzy nowy znormalizowany węzeł w znormalizowanym grafie
def addNewNodeToNormG(nodeName, nodes, edges, neighbours, normalizedGraph):
    normalizedGraph[nodeName]={
            'nodes': nodes,
            'edges': edges,
            'neighbours': neighbours,
            'name': nodeName,
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
    
    return normalizedGraph

###     koniec wspólnej dla wszystkich algorytmów funkcji budującej graf


###     algorytm dijkstry

#zmienna, która będzie przechowywać czas obliczeń funkcji "dijkstraAlg"
dijkstraAlgTimeCalculations=None
#funkcja wyznaczająca najkrótszą trasę z punktu start do punktu end (węzły z normalizedGraph)
#w oparciu o kryterium minimalizacji czasu
#założenie: g jest kosztem najkrótszej ścieżki ze startu do danego węzła
#(koszt ten, to czas w sekundach [typu int])
def dijkstraAlg(start, end, normalizedGraph, startTime):

    #zmienna przechowująca czas rozpoczęcia obliczeń funkcji "dijkstraAlg"
    dijkstraAlgStartCalculations=time.time_ns()

    #węzłowi początkowemu ustawiamy g na 0
    start['g']=0
    #oraz czas przyjazdu na "startTime" (który jest momentem pojawienia się na przystanku
    #-> jest reprezentowany przez liczbę sekund, więc jest zamieniany na zapis godziny
    #w formacie HH:MM:SS za pomocą funkcji "secondsToHour")
    start['arrivalTime']=secondsToHour(startTime)

    #lista nazw węzłów z normalizedGraph (tych jeszcze nieodwiedzonych przez algorytm)
    qList=[]

    #dla każdego węzła grafu poza węzłem startowym ustawiamy g na nieskończoność dodatnią
    for node in normalizedGraph:
        if not node==start['name']:
            normalizedGraph[node]['g']=float('inf')
            qList.append(node)

    #na początku wybranym węzłem będzie start
    chosen_node=start

    #algorytm wykonuje się dopóki qList nie będzie puste 
    #lub aż wcześniej nie znajdzie rozwiązania (najkrótszej ścieżki do docelowego węzła)
    while len(qList)>0:

        #dla każdego sąsiada wybranego węzła, wybieramy najszybszą trasę
        #oraz zapisujemy rodzica, g (koszt) i odpowiednie dane wybranej krawędzi 
        #(ale tylko, jeżeli jest to lepsze połączenie, niż te wybrane wcześniej
        # - jeśli wcześniej g dla danego wierzchołka zostało wyznaczone, tzn. gdy wybrano połączenie, które da mniejsze g)
        for node in chosen_node['neighbours']:

            #nie wracamy już do odwiedzonych wierzchołków
            #sprawdzamy tylko te, które są w qList
            if (node in qList):
                next_node=normalizedGraph[node]

                #wybieramy najkorzystniejszą krawędż, łączącą chosen_node z next_node,
                #używając funkcji "chooseEdgeWithFAForSpecificNode"
                #(najkorzystniejsza, to taka, którą dojedziemy najszybciej do next_node)
                chosenEdge = chooseEdgeWithFAForSpecificNode(chosen_node, next_node)

                #jeżeli znaleziono połączenie, które zmniejszy g węzła next_node,
                #zapisujemy temu węzłowi nowe, mniej kosztowne g, referencję do rodzica (poprzednika)
                #i niektóre dane z krawędzi chosenEdge (każdy węzeł przechowuje dane z krawędzi, która do niego dporowadziła,
                #a nie, która z niego wychodzi -> z tego powodu węzeł startowy nie ma wszystkich danych: np. parent = None)
                if next_node['g']>chosen_node['g'] + abs(hourToSeconds(chosenEdge._arrival_time()) - hourToSeconds(chosen_node['arrivalTime'])):
                    next_node['g']=chosen_node['g'] + abs(hourToSeconds(chosenEdge._arrival_time()) - hourToSeconds(chosen_node['arrivalTime']))
                    next_node['parent'] = chosen_node
                    next_node['departureTime']=chosenEdge._departure_time()
                    next_node['arrivalTime'] = chosenEdge._arrival_time()
                    next_node['departureLine'] = chosenEdge._line()
                    next_node['arrivalLine'] = chosenEdge._line() #zapis tego nie jest konieczny
                    next_node['edgeId'] = chosenEdge._id()

        #na koniec wybieramy kolejny węzeł, ktorego sąsiadów będziemy sprawdzać
        #wybranym węzłem będzie ten należący do qList, którego g jest najmniejsze
        chosen_node=None
        chosen_node_cost=float('inf')

        for node in qList:
            if normalizedGraph[node]['g']<chosen_node_cost:
                chosen_node_cost= normalizedGraph[node]['g']
                chosen_node = normalizedGraph[node]

        #usuwamy wybrany węzeł z listy qList,
        #ponieważ traktujemy go, jak odwiedzonego
        qList.remove(chosen_node['name'])

        #jeżeli wybrany węzeł jest docelowym, algorytm kończy pracę i wyświetla wynik
        if chosen_node['name'] ==end['name']:
            dijkstraAlgEndCalculations=time.time_ns()
            global dijkstraAlgTimeCalculations

            #wyznaczenie czasu trwania obliczeń 
            dijkstraAlgTimeCalculations = dijkstraAlgEndCalculations - dijkstraAlgStartCalculations
            
            #wyświetlenie wyniku za pomocą funkcji "printSolutionDijkstra"
            printSolutionDijkstra(chosen_node, end['name'])
            break

#wybiera krawędź łączącą węzły nodeFrom i nodeTo, której arrival Time
#będzie najwcześniejszy (biorąc pod uwagę, że nie można wyjechać wcześniej,
#niż znajduje się na danym przystanku)
def chooseEdgeWithFAForSpecificNode(nodeFrom, nodeTo):
        
    #chosenEdge będzie przechowywać wybraną krawędź
    chosenEdge=None

    #szukamy połączeń, które prowadzą do przystanku docelowego
    #muszą takie istnieć, bo nodeTo jest zawsze sąsiadem nodeFrom,
    #a więc ma wspólną krawędź
    edgesWithTheSameEnd=[]
    for edge in nodeFrom['edges']:
        if(edge._end_node()._stop_name()==nodeTo['name']):

            #jeżeli dana krawędź prowadzi do nodeTo, 
            #dodajemy ją do edgesWithTheSameEnd za pomocą funkcji "addToSortedEdgesList",
            #która sortuje przez wstawianie dodawane krawędzie, na podstawie ich wyjazdu
            #(od najszybszego departure time do najpóźniejszego)
            edgesWithTheSameEnd=addToSortedEdgesList(edge, edgesWithTheSameEnd)


    #wybieramy najszybsze z tych, które są w przyszłości
    #więc najpierw odsiewamy wszystkie, które są w przyszłości.
    #edgesWithTheSameEndInTheFutureIndex zaznaczy indeks 
    #uporządkowanej listy edgesWithTheSameEnd, od którego wszystkie krawędzie
    #będą miały wyjazd w przyszłości (tzn. od momentu znalezienia się na przystanku nodeFrom)
    edgesWithTheSameEndInTheFutureIndex=None
    for i in range(len(edgesWithTheSameEnd)):
        if edgesWithTheSameEnd[i]._departure_time()>=nodeFrom['arrivalTime']:
            edgesWithTheSameEndInTheFutureIndex=i
            break
    
    #jeżeli są jakieś w przyszłości tego samego dnia...
    if not edgesWithTheSameEndInTheFutureIndex==None:
        #(ponieważ edgesWithTheSameEnd jest posortowane czasem wyjazdu, pozostałe tablice też będą)
        #szukamy linii z najszybszym przyjazdem (ale z tych, których odjazd jest przed północą),
        #korzystając z funkcji "chooseEdgeWithFastestArrival", która zwróci krawędź 
        #o najszybszym czasie przyjazdu do nodeTo z podanej listy (tutaj fragment listy "edgesWithTheSameEnd",
        #który zawiera jedynie krawędzie z przyszłości)
        chosenEdge=chooseEdgeWithFastestArrival(edgesWithTheSameEnd[edgesWithTheSameEndInTheFutureIndex:len(edgesWithTheSameEnd)], nodeFrom['arrivalTime'])

    #jeżeli nie, wybieramy z tych następnego dnia (czyli z całej tablicy, bo wtedy wszystkie edge są następnego dnia)
    else:
        chosenEdge=chooseEdgeWithFastestArrival(edgesWithTheSameEnd)
    
    #zwrócona zostaje najkorzystniejsza krawędź
    return chosenEdge

#wyświetla najkrótszą ścieżkę (pod względem czasu dotarcia) z węzła początkowego, do końcowego
#jest to funkcja rekurencyjna
def printSolutionDijkstra(node, endName):

    #warunek stopu
    #jeżeli węzeł jest węzłem początkowym, zostaną wyświetlone dane
    if(node['parent']==None):
        print(f" Przystanek: {node['name']}, na przystanku: {node['arrivalTime']}, ", end="")

    #jeżeli węzeł nie jest początkowym, najpierw funkcja zostanie wywołana dla rodzica,
    #a potem zostaną wyświetlone dane badanego węzła
    else:
        printSolutionDijkstra(node['parent'], endName)
        print(f'odjazd: {node['departureTime']} linią {node['departureLine']}, eId: {node['edgeId']}')
        print(f'-> Przystanek: {node['name']}, przyjazd: {node['arrivalTime']}, ', end="")

        #jeżeli badany węzłem jest węzłem docelowym, wyświetlone zostaną dane
        if (node['name']==endName):
            print(f'Wartośc g dla tego rozwiazania= {node['g']} s', file=sys.stderr)
            print(f'Czas obliczeń algorytmu= {dijkstraAlgTimeCalculations * (10**(-9))} s', file=sys.stderr)
###     koniec algorytmu dijkstry

###     algorytm aStarTime

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

    nodeFromTime = node['arrivalTime']

    #najkorzystniejsze połączenie ogółem
    chosenEdge=None

    #szukamy połączeń, które prowadzą do przystanku docelowego
    #muszą takie istnieć, bo node next to zawsze ten z sąsiadów noda,
    #a jest sąsiadem, jeżeli ma wspólną krawędź
    edgesWithTheSameEnd=[] #TODO: tu się przyda sortowanie przez wstawianie !!!!!!!!!!!!!!!!!!
    for edge in node['edges']:
        if(edge._end_node()._stop_name()==node_next_normalized_graph['name']):
            edgesWithTheSameEnd=addToSortedEdgesList(edge, edgesWithTheSameEnd)

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

    #zwracamy różnicę czasu i wybrane połączenie
    chosenEdgeArrTime=hourToSeconds(chosenEdge._arrival_time()) #tutaj muszą być posortowane
    return [abs(chosenEdgeArrTime - hourToSeconds(node['arrivalTime'])), chosenEdge]

#TODO: niech printSolution będzie mogło być wykorzystywane przez każdy algorytm
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

###     koniec algorytmu aStarTime

###     algorytm aStarChange

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

def calculateHChange(node_next_normalized_graph, end, graph):
    distanceKm=calculateHDistance(node_next_normalized_graph, end)
    return node_next_normalized_graph['g/hFFS']*distanceKm

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
            #szukamy linii z najszybszym przyjazdem (ale z tych, których odjazd jest przed północą)
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
            #szukamy linii z najszybszym przyjazdem (ale z tych, których odjazd jest przed północą)
            chosenEdge=chooseEdgeWithFastestArrival(edgesWithTheSameEnd[edgesWithTheSameEndInTheFutureIndex:len(edgesWithTheSameEnd)], nodeFromTime)

        #jeżeli nie, wybieramy z tych następnego dnia (czyli z całej tablicy, bo wtedy wszystkie edge są następnego dnia)
        else:
            chosenEdge=chooseEdgeWithFastestArrival(edgesWithTheSameEnd)

    #zwracamy informację o liczbie przesiadek i o wybranym połączeniu
    return [change, chosenEdge]

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

###     koniec algorytmu aStarChange

####    wspolne dla algorytmów funkcje

#zamienia napis reprezentujący godzinę w formacie HH:MM:SS
#na liczbę sekund 
#UWAGA: jest to kod ze strony: https://www.geeksforgeeks.org/convert-a-datetime-object-to-seconds/
def hourToSeconds(time):

    #utworzenie obiektu datetime
    timeDateObject = datetime.strptime(time, "%H:%M:%S")

    #obliczamy różnicę w sekundach daty timeDateObject od czasu odniesienia 
    #(tutaj data 01.01.1900)
    timeWithReference = timeDateObject - datetime(1900, 1, 1)
    seconds = timeWithReference.total_seconds()

    #zwrócona zostaje liczba sekund
    return seconds

#zwraca krawędź o najszybszym czasie przyjazdu do nodeTo z podanej listy krawędzi
#uwzględniajac czas przyjazdu nodeFromTime, jeżeli jest podany
def chooseEdgeWithFastestArrival(listOfEdges, nodeFromTime=None):

    #szukana będzie krawędź z najszybszym przyjazdem
    #filtrem będzie fastestEdgeArrival, który na początku
    #zostaje ustawiony na najwyższą możliwą godzinę
    fastestEdgeArrival='23:59:59'

    #fastestEdgeArrivalIndex będzie przechowywał indeks
    #szukanej krawędzi z listy "listOfEdges"
    fastestEdgeArrivalIndex=None

    for i in range(len(listOfEdges)):
        if listOfEdges[i]._arrival_time()<fastestEdgeArrival:
            if(not nodeFromTime==None):

                #chcemy uniknać sytuacji, że wybrana zostana linia (połączenie, krawędź), 
                #która przyjeżdża o np. 00:00:01, a wyjeżdża o 23:59:59, jeżeli są lepsze opcje 
                #(ponieważ taka linia przyjeżdża o najszybszej godzinie, ale najszybszej w następnym dniu)
                if listOfEdges[i]._arrival_time()>nodeFromTime:
                    fastestEdgeArrival=listOfEdges[i]._arrival_time()
                    fastestEdgeArrivalIndex=i
            else:
                #ta sytuacja ma miejsce, gdy przyjechano na przystanek 
                #i nie ma już żadnych linii tego dnia
                fastestEdgeArrival=listOfEdges[i]._arrival_time()
                fastestEdgeArrivalIndex=i
                    
    #jeżeli były tylko takie opcje, które wyjeżdżają jednego dnia, a dojeżdżają drugiego...
    if(fastestEdgeArrivalIndex==None and not nodeFromTime==None):
        #wybierana jest ta z najszybszym dojazdem z całej listy krawędzi
        fastestEdgeArrival='23:59:59'
        for i in range(len(listOfEdges)):
            if listOfEdges[i]._arrival_time()<fastestEdgeArrival:
                fastestEdgeArrival=listOfEdges[i]._arrival_time()
                fastestEdgeArrivalIndex=i

    #zwracana jest najkorzystniejsza krawędź
    return listOfEdges[fastestEdgeArrivalIndex]

#UWAGA: kod "time.strftime('%H:%M:%S', time.gmtime(seconds))" wygenerowany przez gemini
#zamienia sekundy (typ int) na napis 
#reprezentujący godzinę w formacie HH:MM:SS
#po czym zwraca zweryfikowaną przez funkcję "validateTime" godzinę
def secondsToHour(seconds):
    return validateTime(time.strftime('%H:%M:%S', time.gmtime(seconds)))

#funkcja sortuje przez wstawianie dodawaną krawędź
#edge do listy edgesToCheck, na podstawie jej godziny wyjazdu
#(od najszybszego departure time do najpóźniejszego)
def addToSortedEdgesList(edge, edgesToCheck):
    for i in range(len(edgesToCheck)):
        if(edgesToCheck[i]._departure_time()>edge._departure_time()):
            edgesToCheck.insert(i, edge)
            return edgesToCheck
    edgesToCheck.append(edge)
    return edgesToCheck


def printWholeGraph(normalizedGraph):
    for node in normalizedGraph:
        print(f'{node}:')
        print(f'    nodes:')
        list(map(lambda x: print(f'            {str(x)}'), normalizedGraph[node]['nodes']))
        print(f'    edges:')
        list(map(lambda x: print(f'            {str(x)}'), normalizedGraph[node]['edges']))
        print(f'    neighbours:')
        print(f'        {normalizedGraph[node]['neighbours']}')

###     koniec wspólnych dla algorytmów funkcji

if __name__=='__main__':
    # printWholeGraph(buildGraphFromCSV('test_data_file.csv'))
    normalizedGraph=buildGraphFromCSV('connection_graph.csv')
    while True:
        start=input('Podaj przystanek początkowy: ')
        end=input('Podaj przystanek końcowy: ')

        parameter=input('Podaj kryterium optymalizacyjne: td-> dijkstra czas, ta - a* czas, pa- a* przesiadki: ')

        #IMP: kod z gemini konwertujący czas ze stringa w sekundy
        startTime=hourToSeconds(input('Podaj czas wyjazdu: '))
        try:
            startNormalized=normalizedGraph[start]
            endNormalized=normalizedGraph[end]
            if(parameter=='td'):
                dijkstraAlg(startNormalized, endNormalized, normalizedGraph, startTime)
            if(parameter=='ta'):
                aStarAlgTime(startNormalized, endNormalized, normalizedGraph, startTime)
            if(parameter=='pa'):
                aStarAlgChange(startNormalized, endNormalized, normalizedGraph, startTime)
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


