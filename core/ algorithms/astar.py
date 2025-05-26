# core/algorithm/astar.py
import heapq
import math

def get_shortest_path_astar(graph, source, target, weight_type='distance'):
    def heuristic(u, v):
        pos_u = graph.nodes[u].get("pos", (0,0))
        pos_v = graph.nodes[v].get("pos", (0,0))
        return math.sqrt((pos_u[0] - pos_v[0])**2 + (pos_u[1] - pos_v[1])**2)

    source = str(source)
    target = str(target)
    open_set = []
    heapq.heappush(open_set, (0 + heuristic(source, target), 0, source, [source]))
    g_score = {node: float('inf') for node in graph.nodes()}
    g_score[source] = 0

    while open_set:
        f_current, g_current, current, path = heapq.heappop(open_set)
        if current == target:
            print("Path founded")
            total_cost = g_score[current]
            return path, total_cost
        for neighbor in graph.neighbors(current):
            try:
                weight = graph[current][neighbor][weight_type]
            except KeyError:
                continue
            tentative_g_score = g_score[current] + weight
            if tentative_g_score < g_score.get(neighbor, float('inf')):
                g_score[neighbor] = tentative_g_score
                f_score = tentative_g_score + heuristic(neighbor, target)
                heapq.heappush(open_set, (f_score, tentative_g_score, neighbor, path + [neighbor]))
    print("Path not found.")
    return None, float('inf')

    pass