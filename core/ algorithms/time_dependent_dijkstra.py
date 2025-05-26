# core/algorithms/time_dependent_dijkstra.py
import networkx as nx

def get_time_dependent_path(graph, source, target, current_time):
    """
    current_time: int -> ساعة اليوم (مثلاً 8 تعني 8 صباحاً)
    """
    def get_weight(u, v):
        base = graph[u][v].get('distance', 1)
        rush_hours = (7 <= current_time <= 9) or (16 <= current_time <= 18)
        traffic_factor = graph[u][v].get('traffic_multiplier', 1.0)
        if rush_hours:
            return base * traffic_factor  # مضاعفة الوزن في الزحمة
        return base

    source = str(source)
    target = str(target)
    visited = set()
    distance = {node: float('inf') for node in graph.nodes()}
    distance[source] = 0
    parent = {source: None}
    nodes = list(graph.nodes())

    while nodes:
        u = min((n for n in nodes if n not in visited), key=lambda x: distance[x], default=None)
        if u is None or distance[u] == float('inf'):
            break
        visited.add(u)
        nodes.remove(u)
        for v in graph.neighbors(u):
            weight = get_weight(u, v)
            if distance[u] + weight < distance[v]:
                distance[v] = distance[u] + weight
                parent[v] = u

    path = []
    current = target
    while current is not None:
        path.insert(0, current)
        current = parent.get(current)
    if path[0] != source:
        return None, float('inf')
    return path, distance[target]
