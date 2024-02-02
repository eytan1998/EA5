import copy
import math
from functools import reduce
import networkx as nx


def alter_to_pareto_efficient(graph, circle: list, valuations: list[list[float]],
                              allocation: list[list[float]], toPrint = False) -> list[list[float]]:
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
    for i in range(len(circle) - 1):
        new_allocation[circle[i]][R[i - 1]] += E[i - 1]
        new_allocation[circle[i]][R[i]] -= E[i]

    # print
    if toPrint:
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
    function to find if given valuations and allocation are pareto efficient. if not you can see improvment.
    :param valuations: matrix for each player how much he values each resourse
    :param allocation: matrix for each player how much he got from each resourse
    :param find_improve: if you want to get new allocation that is better than the current allocation.
    :return: True if there are no improvements, False otherwise

    # bad example due to rounding,
    # we can fix by try to get improve by using find_improve=True and see there are no improvements.
    >>> is_pareto_efficient(\
        valuations=[[10, 20, 30, 40],\
                    [40, 30, 20, 10]]\
                    \
        ,allocation=[[0, 0.7, 1, 1],\
                     [1, 0.3, 0, 0]],find_improve=True)
    True

    # bad example from class
    >>> is_pareto_efficient(valuations=[[6, 1, 3], [1, 3, 6], [3, 6, 1]],\
                            allocation=[[0, 0, 1], [0, 1, 0], [1, 0, 0]])
    False

    # the currection from class
    >>> is_pareto_efficient(valuations=[[6, 1, 3],\
                                        [1, 3, 6],\
                                        [3, 6, 1]],\
                            allocation=[[1, 0, 0],\
                                        [0, 0, 1],\
                                        [0, 1, 0]])
    True

    # the pirate is pareto efficient.
    >>> is_pareto_efficient(valuations=[[6, 1, 3]\
                                       ,[1, 3, 6],\
                                        [3, 6, 1]],\
                            allocation=[[1, 1, 1],\
                                        [0, 0, 0],\
                                        [0, 0, 0]])
    True
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
                    if allocation[i][k] == 0: continue
                    tmp = valuations[i][k] / valuations[j][k]
                    if min_weight > tmp > 0:
                        min_weight = tmp
                        index_res = k
                # also save index of res for the pareto efficient improve
                G.add_edge(i, j, weight=min_weight, res=index_res)

    # so can pass the graph without the log changes
    GTMP = copy.deepcopy(G)

    # change all the weight to the log of them
    for edge in GTMP.edges():
        GTMP[edge[0]][edge[1]]['weight'] = math.log(GTMP[edge[0]][edge[1]]['weight'])

    # find if it has negative circle
    for node in range(num_player):
        try:
            ans = nx.find_negative_cycle(GTMP, node)
            # if got here there is negative circle
            if find_improve:
                if allocation == alter_to_pareto_efficient(G, ans, valuations, allocation): return True
            return False
        except nx.NetworkXError:
            pass
    # is pareto efficient
    return True


if __name__ == '__main__':
    import doctest
    doctest.testmod()

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
