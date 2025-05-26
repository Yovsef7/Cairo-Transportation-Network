# core/algorithm/greedy.py
import networkx as nx

def greedy_search(graph, source, target, weight_type='distance'):
    source = str(source)
    target = str(target)
    path = [source]
    current = source
    visited = set([source])
    while current != target:
        neighbors = [n for n in graph.neighbors(current) if n not in visited]
        if not neighbors:
            print("No Avaliable Path")
            return None
        min_cost = float('inf')
        next_node = None
        for neighbor in neighbors:
            try:
                weight = graph[current][neighbor][weight_type]
                if weight < min_cost:
                    min_cost = weight
                    next_node = neighbor
            except KeyError:
                continue
        if next_node is None:
            print("Path not found")
            return None
        path.append(next_node)
        visited.add(next_node)
        current = next_node
        if current == target:
            print("Path founded")
            return path
    return path
    pass