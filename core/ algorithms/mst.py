# core/algorithm/mst.py
import networkx as nx
import math

def design_mst_network(graph, weight_criteria="distance", include_facilities=True):
    mst_graph = nx.Graph()
    mst_graph.add_nodes_from(graph.nodes(data=True))
    edges_with_weights = []

    for u, v, data in graph.edges(data=True):
        if weight_criteria == "distance":
            weight = data['distance']
        elif weight_criteria == "travel_time":
            weight = data['travel_time']
        elif weight_criteria == "congestion":
            weight = data['avg_traffic'] / data['capacity']
        else:
            weight = data['distance']

        pop_u = graph.nodes[u].get('population', 0)
        pop_v = graph.nodes[v].get('population', 0)
        avg_pop = (pop_u + pop_v) / 2
        weight = weight / (math.log(avg_pop + 1))
        edges_with_weights.append((u, v, weight))

    parent = {node: node for node in graph.nodes()}

    def find(u):
        while parent[u] != u:
            parent[u] = parent[parent[u]]
            u = parent[u]
        return u

    def union(u, v):
        u_root = find(u)
        v_root = find(v)
        if u_root != v_root:
            parent[v_root] = u_root

    edges_with_weights.sort(key=lambda x: x[2])

    for u, v, weight in edges_with_weights:
        if find(u) != find(v):
            mst_graph.add_edge(u, v, **graph.edges[u, v])
            union(u, v)

    if include_facilities:
        facilities = [node for node, data in graph.nodes(data=True) if data.get('node_type') == 'facility']
        for facility in facilities:
            # ربط المرافق بأقرب نقطة في الشبكة إن لم تكن مرتبطة
            if not nx.has_path(mst_graph, facility, list(mst_graph.nodes())[0]):
                try:
                    path = nx.shortest_path(graph, source=facility, target=list(mst_graph.nodes())[0], weight=weight_criteria)
                    for i in range(len(path)-1):
                        u=path[i]
                        v=path[i+1]
                        if not mst_graph.has_edge(u, v):
                            mst_graph.add_edge(u, v, **graph.edges[u, v])
                except nx.NetworkXNoPath:
                    print(f"Warning: No path to reach {facility}")
    return mst_graph
    pass