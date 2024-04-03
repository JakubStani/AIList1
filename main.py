from edge import Edge
from node import Node
from djkNode import DjkNode
from aStarNode import AStarNode
import math
from datetime import datetime
import time
import sys


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

###

###Info: powyższe jest takie samo dla wszystkich