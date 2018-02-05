import pygraphviz as pgv
import TwC
from functools import reduce
import os.path

def get_input():
    """
    first line numV is the number of vertices of the graph
    second line contains the index of source and sink vertices
    next numV lines is the matrix representation of the graph
    """
    numV = int(input().strip())
    source, sink = map(int, input().split())
    graphMatrix = []
    # get matrix representation of graph:
    for i in range(numV):
        graphMatrix.append(list(map(int, input().split())))
    return (numV, source, sink, graphMatrix)


def get_level_graph(numV, source, matrix):

    # get levels
    
    matrix_copy = [[0 for i in range(numV)] for j in range(numV)]
    levels = [-10 for i in range(numV)]
    levels[source] = 0

    queue = [source]

    explored = []

    visited = [source]

    while queue:

        v_start = queue.pop(0)
        explored.append(v_start)

        row = matrix[v_start]

        for i in range(len(row)):
            if row[i]:
                v_end = i

                if v_end not in visited:
                    queue.append(v_end)
                    visited.append(v_end)

                    levels[v_end] = levels[v_start] + 1

    # build level graph
    for i in range(numV):
        for j in range(numV):
            if levels[j] - levels[i] == 1:
                matrix_copy[i][j] = matrix[i][j]

    return matrix_copy


# uses pygrahpviz to visualize graph
def draw_graph(numV, matrix, filename):

    A=pgv.AGraph(directed = True)

    for i in range(numV):
        for j in range(numV):
            if matrix[i][j]:
                A.add_edge(chr(i+97), chr(j+97), label = str(matrix[i][j]), weight = matrix[i][j])

    A.layout()
    A.draw(filename)


def advance(source, sink, level_graph, original_graph, forest, NumToNodeDict, flowGraph, huge, step, level = 0):

    forest.visualize("diagrams/" + "level" + str(level) + " "+ str(step) + "advance" + ".png")
    # draw_graph(len(flowGraph), flowGraph, str(step) + "flow" + ".png")

    node_source = NumToNodeDict[source]
    node_sink = NumToNodeDict[sink]

    numV = len(level_graph)

    node_v = forest.findroot(node_source)

    if node_v == node_sink:
        return augment(source, sink, level_graph, original_graph, forest, NumToNodeDict, flowGraph, huge, step+1, level = level)

    else:

        # if there are no edges out of v
        if set(level_graph[node_v.toNum()]) == set([0]):
            return retreat(source, sink, level_graph, original_graph, forest, NumToNodeDict, flowGraph, huge, step+1, node_v, level = level)
        else:
            for i in range(numV):
                if level_graph[node_v.toNum()][i]:
                    w = i
                    node_w = NumToNodeDict[w]

                    forest.addcost(node_v, level_graph[node_v.toNum()][w] -  huge)
                    forest.link(node_v, node_w)

                    return advance(source, sink, level_graph, original_graph, forest, NumToNodeDict, flowGraph, huge, step+1, level = level)
                    
                    break;

    


def augment(source, sink, level_graph, original_graph, forest, NumToNodeDict, flowGraph, huge, step, level = 0):

    forest.visualize("diagrams/" + "level" + str(level) + " "+ str(step) + "augment" + ".png")
    # draw_graph(len(flowGraph), flowGraph, str(step) + "flow" + ".png")

    node_source = NumToNodeDict[source]

    node_v, delta = forest.findcost(node_source)
    forest.addcost(node_source, -delta)

    return delete(source, sink, level_graph, original_graph, forest, NumToNodeDict, flowGraph, huge, step+1, node_v, level = level)

def delete(source, sink, level_graph, original_graph, forest, NumToNodeDict, flowGraph, huge, step, node_v, level = 0):

    forest.visualize("diagrams/" + "level" + str(level) + " "+ str(step) + "delete" + ".png")
    # draw_graph(len(flowGraph), flowGraph, str(step) + "flow" + ".png")

    node_source = NumToNodeDict[source]

    node_w =node_v.parent

    forest.cut(node_v)
    forest.addcost(node_v, huge)

    # add to flow graph
    flowGraph[node_v.toNum()][node_w.toNum()] = original_graph[node_v.toNum()][node_w.toNum()]

    #delete [v,p(v)] from the level graph
    level_graph[node_v.toNum()][node_w.toNum()] = 0

    node_v, delta = forest.findcost(node_source)

    if delta == 0:
        return delete(source, sink, level_graph, original_graph, forest, NumToNodeDict, flowGraph, huge, step+1, node_v, level = level)

    else:
        return advance(source, sink, level_graph, original_graph, forest, NumToNodeDict, flowGraph, huge, step+1, level = level)

def retreat(source, sink, level_graph, original_graph, forest, NumToNodeDict, flowGraph, huge, step, node_v, level = 0):

    forest.visualize("diagrams/" + "level" + str(level) + " "+ str(step) + "retreat" + ".png")
    # draw_graph(len(flowGraph), flowGraph, str(step) + "flow" + ".png")

    print (node_v)

    numV = len(level_graph)
    node_source = NumToNodeDict[source]
    v = node_v.toNum()
    if node_v == node_source:
        return source, sink, level_graph, original_graph, forest, NumToNodeDict, flowGraph, huge, step
    else:
        # for every edge [u,v], delete [u,v] from the graph
        for u in range(numV):
            
            if level_graph[u][v]:

                level_graph[u][v] = 0

                node_u = NumToNodeDict[u]

                if node_u.parent != node_v:
                    flowGraph[u][v] = 0
                else:
                    forest.cut(node_u)
                    node_w, delta = forest.findcost(node_u)
                    forest.addcost(node_w, huge - delta)
                    flowGraph[node_w.toNum()][v] = original_graph[node_w.toNum()][v] - delta

        return advance(source, sink, level_graph, original_graph, forest, NumToNodeDict, flowGraph, huge, step+1, level = level)


def postProcess(source, sink, level_graph, original_graph, forest, NumToNodeDict, flowGraph, huge, step):

    numV = len(level_graph)
    for u in range(numV):
        for v in range(numV):
            if level_graph[u][v]:

                level_graph[u][v] = 0

                node_u = NumToNodeDict[u]
                node_v = NumToNodeDict[v]

                if node_u.parent != node_v:
                    flowGraph[u][v] = 0
                else:
                    forest.cut(node_u)
                    node_w, delta = forest.findcost(node_u)
                    forest.addcost(node_w, huge - delta)
                    flowGraph[node_w.toNum()][v] = original_graph[node_w.toNum()][v] - delta

    return flowGraph, step+1


def getBlockingFlow(level_graph, original_graph, source, sink, level = 0):

    # first, create forest of nodes
    numV = len(level_graph)
    huge = sum([sum(row) for row in level_graph]) + 100

    roots = [TwC.TwC_Node(chr(i+97), huge) for i in range(numV)]
    forest = TwC.TwC_Forest(roots)

    # Then, make a num to node dictionary
    NumToNodeDict = {}
    for root in roots:
        NumToNodeDict[root.toNum()] = root

    # Then, initialize flow graph
    flow = [[0 for i in range(numV)] for j in range(numV)]

    source, sink, level, original, forest, NumToNodeDict, flow, huge, step = \
    advance(source, sink, level_graph, original_graph, forest, NumToNodeDict, flow, huge, 0, level = level)

    flow, steps = postProcess(source, sink, level, original, forest, NumToNodeDict, flow, huge, step)

    print (steps)
    return flow


def getResidualGraph(flow_graph, original_graph):

    numV = len(flow_graph)

    for u in range(numV):
        for v in range(numV):
            if flow_graph[u][v]:
                original_graph[u][v] -= flow_graph[u][v]
                original_graph[v][u] += flow_graph[u][v]

    return original_graph

def getFlow(numV, source, sink, original_graph):

    if not os.path.exists("diagrams"):
        os.makedir("diagrams")
    
    level = 1
    draw_graph(numV, original_graph, "diagrams/original_graph.png")
    

    total_flow_graph = [[0 for i in range(numV)] for j in range(numV)]

    residual_graph = original_graph

    while (True):

        level_graph = get_level_graph(numV, source, original_graph)
        draw_graph(numV, level_graph, "diagrams/level_graph"+str(level)+".png")

        flow_graph = getBlockingFlow(level_graph, original_graph, source, sink, level = level)
        draw_graph(numV, flow_graph, "diagrams/flow_graph"+str(level)+".png")

        # if matrix is all zeroes, halt
        if all(row == [0 for i in range(numV)] for row in flow_graph):
            break

        else:
            residual_graph = getResidualGraph(flow_graph, residual_graph)
            draw_graph(numV, residual_graph, "diagrams/residual_graph"+str(level)+".png")

             # add flow graph to total_flow_graph
            for u in range(numV):
                for v in range(numV):
                    total_flow_graph[u][v] += flow_graph[u][v]

            level += 1

    return total_flow_graph, sum(total_flow_graph[0])

def main():

    numV, source, sink, original_graph = get_input()

    total_flow_graph, total_flow = getFlow(numV, source, sink, original_graph)

    draw_graph(numV, total_flow_graph, "diagrams/total_flow.png")

    print (total_flow)



if __name__ == "__main__":
    main()