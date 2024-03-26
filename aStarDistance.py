import math
import time

#nowa wersja -> działa właściwie; heurystyka to odległość (i g też)
def aStarAlg(start, end, graph): #start i end to znormalizowane węzły

    list_open=[]
    list_closed=[]

    start['g']=0
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
            #print(f'Rozwiazanie:{list(map(lambda x: x["name"], list_closed))}')
            #print(f'otwarta lista:{list(map(lambda x: x["name"], list_open))}')
            print('Rozwiązanie:')
            printSolution(node)
            break

        #TODO: be able to find this node
        list_open.remove(node)
        list_closed.append(node)

        #tu się zaczynają problemy z sąsiadami, bo info o sąsiadach ma normalized graph, a tam nie ma AstarNodów
        #tutaj node next ma być AStarNodem, tylko jak go utworzyć?
        for node_next_name in node['neighbours']:
            #szukam po nazwie, bo node_next nie jest AStarNodem
            node_next_normalized_graph=graph[node_next_name]
            if (node_next_normalized_graph not in list_open and node_next_normalized_graph not in list_closed): #TODO: be able to fin this node
                nnH=calculateHDistance(node_next_normalized_graph, end, graph)
                #TODO: czy trzeba zrobić z czasem? Jak tak, to wtedy trzeba stworzyć calculate h time
                nnG=node['g'] + getDistance(node, node_next_normalized_graph)
                node_next_normalized_graph['h']=nnH
                node_next_normalized_graph['g']=nnG
                node_next_normalized_graph['f']=nnH + nnG
                node_next_normalized_graph['parent']=node
                list_open.append(node_next_normalized_graph)
            else:
                if(node_next_normalized_graph['g']>node['g'] + getDistance(node,node_next_normalized_graph)):
                    node_next_normalized_graph['g']=node['g'] +getDistance(node,node_next_normalized_graph)
                    node_next_normalized_graph['parent']=node
                    node_next_normalized_graph['f']=node_next_normalized_graph['g']+node_next_normalized_graph['h']
                    if(node_next_normalized_graph in list_closed): #TODO: trzeba móc odnaleźć tego noda w liście
                        list_open.append(node_next_normalized_graph)
                        list_closed.remove(node_next_normalized_graph) #TODO: trzeba móc odnaleźć noda
    #print(f'Lista zamknięta:{list(map(lambda x: x["name"], list_closed))}')
    #print(f'Lista otwarta:{list(map(lambda x: x["name"], list_open))}')
    
#WAŻNE!: zawsze przystanek, z którego wysiadamy jest przystankiem, na którym wsiadamy
def printSolution(node):
    if(node['parent']==None):
        print(f'Przystanek: {node['name']}, \
              czas pojawienia się na przystanku: {secondsToHour(node['g'])}, \
                odjazd z tego przystanku: {node['departureTime']} linią {node['departureLine']}')
    else:
        printSolution(node['parent'])
        print(f' -> Przystanek: {node['name']}, \
              przyjazd: {secondsToHour(node['g'])}, \
                odjazd z tego przystanku: {node['departureTime']} \
                    linią {node['departureLine']}')
        
#IMP: kod z gemini
def secondsToHour(seconds):
    return time.strftime('%H:%M:%S', time.gmtime(seconds))

def calculateHDistance(normalizedNodeFrom, normalizedNodeTo, graph):
    return (math.sqrt((normalizedNodeFrom['averageLon'] - 
            normalizedNodeTo['averageLon'])**2 + 
            (normalizedNodeFrom['averageLat'] - 
            normalizedNodeTo['averageLat'])**2))

#Chcemy brać dystans, czy czas?
def getDistance(node, node_next):
    for edge in node['edges']:
        if(edge._end_node()._stop_name()==node_next['name']):
            return edge._distance()
    print(f"Nie udalo się dla: {list(map(lambda x: x._end_node()._stop_name(), node['edges']))} i {node_next['name']}, a przystanek to {node['name']}")
   