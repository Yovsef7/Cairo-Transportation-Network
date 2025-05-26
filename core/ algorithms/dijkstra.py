# core/algorithm/dijkstra.py
import networkx as nx

cache = {}
def get_shortest_path_dijkstra(graph, source, target, weight_type='distance'):
    key = (source, target, weight_type)
    if key in cache:
        print("Using cached result.")
        return cache[key]
    if weight_type not in ['distance', 'travel_time']:
        print("Invalid weight_type! Use 'distance' or 'travel_time'.")
        return None, None
    try:
        path = nx.dijkstra_path(graph, source=str(source), target=str(target), weight=weight_type)
        length = nx.dijkstra_path_length(graph, source=str(source), target=str(target), weight=weight_type)
        print(f"Shortest path from {source} to {target} by {weight_type}:")
        for n in path:
            if "name" in graph.nodes[n]:
                print(f"- {graph.nodes[n]['name']} ({n})")
            else:
                print(f"- {n}")
        print(f"Total {weight_type}: {length}")
        return path, length
    except nx.NetworkXNoPath:
        print(f"No path from {source} to {target}")
        return None, float('inf')
    
    cache[key] = (path, length)
    return path, length
    pass