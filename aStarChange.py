from main import *
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
            gCh=getChanges(node, node_next_normalized_graph)
            #WAŻNE: możliwe uproszczenia
            if (node_next_normalized_graph not in list_open and node_next_normalized_graph not in list_closed): #TODO: be able to fin this node
                #TODO: czy trzeba zrobić z czasem? Jak tak, to wtedy trzeba stworzyć calculate h time
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
    #print(f'Lista zamknięta:{list(map(lambda x: x["name"], list_closed))}')
    #print(f'Lista otwarta:{list(map(lambda x: x["name"], list_open))}')