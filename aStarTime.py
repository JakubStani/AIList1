from mainPrevious import *

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
                nnH=calculateHTime(node_next_normalized_graph, end, graph)
                #TODO: czy trzeba zrobić z czasem? Jak tak, to wtedy trzeba stworzyć calculate h time
                gTDResult=getTimeDiff(node, node_next_normalized_graph)
                nnG=node['g'] + gTDResult[0]
                node_next_normalized_graph['h']=nnH
                node_next_normalized_graph['g']=nnG
                # node_next_normalized_graph['gString']=secondsToHour(nnG)
                node_next_normalized_graph['f']=nnH + nnG
                node_next_normalized_graph['parent']=node
                node_next_normalized_graph['arrivalTime']=gTDResult[1]._arrival_time()
                node['departureTime']=gTDResult[1]._departure_time()
                node['departureLine']=f'{gTDResult[1]._company()} {gTDResult[1]._line()}'
                node['edgeId']=gTDResult[1]._id()
                list_open.append(node_next_normalized_graph)
            else:
                #co tu się dokładnie dzieje?
                gTDResult=getTimeDiff(node,node_next_normalized_graph)
                if(node_next_normalized_graph['g']>node['g'] + gTDResult[0]):
                    node_next_normalized_graph['g']=node['g'] +gTDResult[0]
                    node['departureTime']=gTDResult[1]._departure_time()
                    node['departureLine']=f'{gTDResult[1]._company()} {gTDResult[1]._line()}'
                    node['edgeId']=gTDResult[1]._id()
                    node_next_normalized_graph['arrivalTime']=gTDResult[1]._arrival_time()
                    # node_next_normalized_graph['gString']=secondsToHour(node_next_normalized_graph['g'])
                    node_next_normalized_graph['parent']=node
                    node_next_normalized_graph['f']=node_next_normalized_graph['g']+node_next_normalized_graph['h']
                    if(node_next_normalized_graph in list_closed): #TODO: trzeba móc odnaleźć tego noda w liście
                        list_open.append(node_next_normalized_graph)
                        list_closed.remove(node_next_normalized_graph) #TODO: trzeba móc odnaleźć noda