import copy
import math

import networkx as nx
import matplotlib.pyplot as plt


def alter_to_pareto_efficient(graph, cyrcle: list, valuations: list[list[float]],
                              allocation: list[list[float]]) -> bool:
    # >>> is_pareto_efficient(valuations=[[6, 1, 3]
    # ,[1, 3, 6]
    # ,[3, 6, 1]],\
    #                         allocation=[[0, 0, 1], [0, 1, 0], [1, 0, 0]])


    num_player = len(valuations)
    num_res = len(valuations[0])

    R = [graph[cyrcle[i]][cyrcle[i + 1]]['res'] for i in range(len(cyrcle) - 1)]
    P = (sum(valuations[cyrcle[i]][R[i]] for i in range(len(cyrcle) - 1)) /
         sum(valuations[cyrcle[i]][R[i - 1]] for i in range(1, len(cyrcle))))
    Q = P ** (1 / 3)
    E = [_ for _ in range(len(cyrcle) - 1)]
    E[0] =
    for i in range(1, len(E)):
        E[i] = E[i - 1] * Q * (valuations[cyrcle[i]][R[i - 1]] / valuations[cyrcle[i]][R[i]])

    print(cyrcle)
    print(R)
    print(E)
    #so can test the improvement
    new_allocation = copy.deepcopy(allocation)
    new_allocation[cyrcle[0]][R[len(R) - 1]] += E[len(E) - 1]
    new_allocation[cyrcle[0]][R[0]] -= E[len(E) - 1]
    for i in range(1, len(cyrcle)-1):
        new_allocation[cyrcle[i]][R[i - 1]] += E[len(E) - 1]
        new_allocation[cyrcle[i]][R[i]] -= E[len(E) - 1]
    for i in range(num_player):
        print(f' player {i} improve by {sum(new_allocation[i][j] * valuations[i][j] for j in range(num_res))-sum(allocation[i][j] * valuations[i][j] for j in range(num_res))}')

    print(allocation)
    print(new_allocation)
    return True


def is_pareto_efficient(valuations: list[list[float]], allocation: list[list[float]]) -> bool:
    # '''
    #
    # :param valuations:
    # :param allocation:
    # :return:
    # >>> is_pareto_efficient(\
    #     valuations=[[10, 20, 30, 80],\
    #                  [40, 30, 20, 10]]\
    #      , allocation=[[0, 0.7, 1, 1],\
    #                   [1, 0.3, 0, 0]])
    # True
    # >>> is_pareto_efficient(valuations=[[6, 1, 3], [1, 3, 6], [3, 6, 1]],\
    #                         allocation=[[0, 0, 1], [0, 1, 0], [1, 0, 0]])
    # True
    # >>> is_pareto_efficient(valuations=[[6, 1, 3],\
    #                                     [1, 3, 6],\
    #                                     [3, 6, 1]],\
    #                         allocation=[[1, 0, 0],\
    #                                     [0, 0, 1],\
    #                                     [0, 1, 0]])
    # False
    # >>> valuations = [[10, 5], [8, 6], [6, 7]]
    # >>> allocation = [[1, 0], [0, 1], [1, 1]]
    # >>> is_pareto_efficient(valuations, allocation)
    # True
    #
    # >>> valuations = [[10, 5], [8, 6], [6, 7]]
    # >>> allocation = [[0, 0], [0, 0], [0, 0]]
    # >>> is_pareto_efficient(valuations, allocation)
    # False
    #
    # >>> valuations = [[10, 5], [8, 6], [6, 7]]
    # >>> allocation = [[1, 0], [0, 1], [0, 0]]
    # >>> is_pareto_efficient(valuations, allocation)
    # False
    # '''
    num_player = len(valuations)
    num_res = len(valuations[0])

    calc_valuation = [[valuations[i][j] * allocation[i][j] for j in range(num_res)] for i in range(num_player)]

    # create a directed graph
    G = nx.DiGraph()

    # add nodes
    for i in range(num_player):
        G.add_node(i)

    #  add edges
    for i in range(num_player):
        for j in range(num_player):
            if i != j:
                min_weight = math.inf
                index_res = -1
                for k in range(num_res):
                    if (valuations[i][k]) == 0: continue
                    tmp = calc_valuation[i][k] / valuations[j][k]
                    if min_weight > tmp > 0:
                        min_weight = tmp
                        index_res = k
                G.add_edge(i, j, weight=min_weight, res=index_res)

    GTMP = G.copy()

    # change all the weight to the log of them
    for edge in GTMP.edges():
        GTMP[edge[0]][edge[1]]['weight'] = math.log(GTMP[edge[0]][edge[1]]['weight'])

    hasNagetive = False
    for node in range(num_player):
        try:
            ans = nx.find_negative_cycle(GTMP, node)
            return alter_to_pareto_efficient(G, ans, valuations, allocation)
        except nx.NetworkXError:
            pass

    return hasNagetive


if __name__ == '__main__':
    # import doctest
    #
    # doctest.testmod()

    is_pareto_efficient(valuations=[[6, 1, 3], [1, 3, 6], [3, 6, 1]],
                        allocation=[[0, 0, 1], [0, 1, 0], [1, 0, 0]])
# Print DiGraph
#   print("Graph edges:")
#   print(G.edges(data=True))
#
#   # Draw the graph with edge labels
#   pos = nx.random_layout(G)  # Choose a layout (you can try different layouts)
#   nx.draw(G, pos, with_labels=True, font_weight='bold', node_color='lightblue', edge_color='gray', arrowsize=20)
#
#   # Draw edge labels
#   nx.draw_networkx_edge_labels(G, pos)
#   plt.show()
