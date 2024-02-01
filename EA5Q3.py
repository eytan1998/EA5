import copy
import math
from functools import reduce
from typing import List

import networkx as nx
import matplotlib.pyplot as plt


def alter_to_pareto_efficient(graph, circle: list, valuations: list[list[float]],
                              allocation: list[list[float]]) -> list[list[float]]:
    # [6, 1, 3]
    # [1, 3, 6]
    # [3, 6, 1]
    #
    #
    # [0, 0, 1]
    # [0, 1, 0]
    # [1, 0, 0]

    # circle 2 -> 0 -> 1 -> 2
    # R 0    2    1
    # a=2, b=0, c=1
    # x=0, y=2, z=1
    num_player = len(valuations)
    num_res = len(valuations[0])

    # get the resource that the edges are talking about
    R = [graph[circle[i]][circle[i + 1]]['res'] for i in range(len(circle) - 1)]

    P = (reduce(lambda x, y: x * y, [valuations[circle[i]][R[i]] for i in range(len(circle) - 1)])
         / reduce(lambda x, y: x * y, [valuations[circle[i]][R[i - 1]] for i in range(1, len(circle))]))
    Q = P ** (1 / 3)

    # find Ex we can pass for all
    E = [_ for _ in range(len(circle) - 1)]
    E[0] = 1
    for i in range(len(circle) - 1):
        if allocation[circle[i]][R[i]] < E[0]:
            E[0] = allocation[circle[i]][R[i]]

    for i in range(1, len(E)):
        E[i] = E[i - 1] * Q * (valuations[circle[i]][R[i - 1]] / valuations[circle[i]][R[i]])
    E[0] = E[-1] * Q * (valuations[circle[0]][R[-1]] / valuations[circle[0]][R[0]])

    # so can test the improvement
    new_allocation = copy.deepcopy(allocation)

    # move allocation to improve
    new_allocation[circle[0]][R[len(R) - 1]] += E[-1]
    new_allocation[circle[0]][R[0]] -= E[0]
    for i in range(1, len(circle) - 1):
        new_allocation[circle[i]][R[i - 1]] += E[i - 1]
        new_allocation[circle[i]][R[i]] -= E[i]

    # print
    for i in range(num_player):
        print(
            f'=========player {i}==============='
            f'\npre he got: {sum(allocation[i][j] * valuations[i][j] for j in range(num_res))}'
            f'\nnow he got:{sum(new_allocation[i][j] * valuations[i][j] for j in range(num_res))}'
            f'\nimprove by: {sum(new_allocation[i][j] * valuations[i][j] for j in range(num_res)) - sum(allocation[i][j] * valuations[i][j] for j in range(num_res))}'
            f'\n===================================')

    # for row in range(len(allocation)):
    #     for col in range(len(allocation)):
    #         print(allocation[row][col], end="  ")
    #     print()
    #
    # print("")
    # for row in range(len(new_allocation)):
    #     for col in range(len(new_allocation)):
    #         print(new_allocation[row][col], end="  ")
    #     print()

    return new_allocation


def is_pareto_efficient(valuations: list[list[float]], allocation: list[list[float]], find_improve=False) -> bool:
    '''

    :param find_improve:
    :param valuations:
    :param allocation:
    :return:
    >>> is_pareto_efficient(\
        valuations=[[10, 20, 30, 80],\
                     [40, 30, 20, 10]]\
         , allocation=[[0, 0.7, 1, 1],\
                      [1, 0.3, 0, 0]])
    True
    >>> is_pareto_efficient(valuations=[[6, 1, 3], [1, 3, 6], [3, 6, 1]],\
                            allocation=[[0, 0, 1], [0, 1, 0], [1, 0, 0]])
    True
    >>> is_pareto_efficient(valuations=[[6, 1, 3],\
                                        [1, 3, 6],\
                                        [3, 6, 1]],\
                            allocation=[[1, 0, 0],\
                                        [0, 0, 1],\
                                        [0, 1, 0]])
    False
    >>> valuations = [[10, 5], [8, 6], [6, 7]]
    >>> allocation = [[1, 0], [0, 1], [1, 1]]
    >>> is_pareto_efficient(valuations, allocation)
    True

    >>> valuations = [[10, 5], [8, 6], [6, 7]]
    >>> allocation = [[0, 0], [0, 0], [0, 0]]
    >>> is_pareto_efficient(valuations, allocation)
    False

    >>> valuations = [[10, 5], [8, 6], [6, 7]]
    >>> allocation = [[1, 0], [0, 1], [0, 0]]
    >>> is_pareto_efficient(valuations, allocation)
    False
    '''
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
            if find_improve:
                return alter_to_pareto_efficient(G, ans, valuations, allocation)
            return True
        except nx.NetworkXError:
            pass

    return hasNagetive


if __name__ == '__main__':
    import doctest
    doctest.testmod()

    x = is_pareto_efficient(valuations=[[6, 1, 3], [1, 3, 6], [3, 6, 1]],allocation=[[0, 0, 1], [0, 1, 0], [1, 0, 0]], find_improve=True)


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
