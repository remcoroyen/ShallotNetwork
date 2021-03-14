import math
import random


def shallot_RandomDijkstra(Source, Destination, IPs, Ports, Neighbours):
    LinkCosts = randomizeCosts(IPs, Ports, Neighbours)
    Nodes = [None]*len(IPs)
    for i in range(len(IPs)):
        Nodes[i] = [IPs[i], Ports[i]]
    PathCosts, Paths = Dijkstra(Source, Nodes, Neighbours, LinkCosts)
    
    Path = [Destination]
    Current_node = Destination
    while Current_node != Source:
        for Path_index in range(len(Paths)):
            if Paths[Path_index][1] == Current_node:
                Current_node = Paths[Path_index][0]
                Path.append(Current_node)
    Path.pop()  # pop the source node from the path!
    return Path


def randomizeCosts(IPs,Ports,Neighbours):
    LinkCosts = [[math.inf for m in range(len(IPs))] for m in range(len(IPs))]
    for i in range(len(IPs)):
        for j in range(len(IPs)):
            if i == j:
                LinkCosts[i][j] = 0
            elif [IPs[j], Ports[j]] in Neighbours[i] and LinkCosts[i][j] == math.inf:
                cost = random.randint(1, 16)
                LinkCosts[i][j] = cost
                LinkCosts[j][i] = cost
    return LinkCosts           
    
# Assumed that node itself is in its own neighbour list

# Nodes: Nested list containing for each node the list of its IP address and Port number
# Neighbours: Nested list containing for each node the list of IP addresses and Port numbers of its neighbours
# LinkCosts: Nested #nodes x #nodes list: LinkCosts(i,j)=LinkCosts(j,i)=cost of link between j and i; C(i,i)=0


def Dijkstra(Source, Nodes, Neighbours, LinkCosts):
    LeastCosts = [None] * len(Nodes)
    Paths = []  # nested list containing the least cost paths to each destination
    
    LeastCostPathFound = [Source]
    source_index = Nodes.index(Source)
    
    # initialization
    for node_index in range(len(Nodes)):
        if Nodes[node_index] in Neighbours[source_index]:
            LeastCosts[node_index] = LinkCosts[source_index][node_index]
            Paths.append([Source, Nodes[node_index]])
        else:
            LeastCosts[node_index] = math.inf
    
    # Updating
    while len(LeastCostPathFound) < len(Nodes):
        unvisitedNode_found = False
        LeastCosts_temp = LeastCosts[:]
        # copies list LeastCosts into LeastCosts_temp; LeastCosts_temp = LeastCosts -> LeastCosts_temp is just
        # reference to LeastCosts
        while unvisitedNode_found is False:
            node_current_index = LeastCosts_temp.index(min(LeastCosts_temp))
            if Nodes[node_current_index] not in LeastCostPathFound:
                LeastCostPathFound.append(Nodes[node_current_index])
                unvisitedNode_found = True
            else:
                LeastCosts_temp[node_current_index] = math.inf
                # Least Cost path to node already found -> eliminate it from search
                
        for node_index in range(len(Nodes)):
            if Nodes[node_index] in Neighbours[node_current_index] and Nodes[node_index] not in LeastCostPathFound:
                if LeastCosts[node_index] > LeastCosts[node_current_index] + LinkCosts[node_current_index][node_index]:
                    LeastCosts[node_index] = LeastCosts[node_current_index] + LinkCosts[node_current_index][node_index]
                    # deleting old path
                    for path in Paths:
                        if path[1] == Nodes[node_index]:
                            Paths.pop(Paths.index(path))
                    # adding new path
                    Paths.append([Nodes[node_current_index],Nodes[node_index]])

    return LeastCosts, Paths
