import math
import heapq
import networkx as nx

class CairoMap:
    def __init__(self):
        # Initialize empty data structures
        self.neighborhoods = []
        self.facilities = []
        self.existing_roads = []
        self.new_roads = []
        self.traffic_patterns = []
        self.metro_lines = []
        self.bus_routes = []
        self.public_transport_demand = []
        
        # Create empty graph
        self.G = nx.Graph()
        
    def _add_nodes(self):
        """Add neighborhood and facility nodes to the graph"""
        for area in self.neighborhoods:
            self.G.add_node(str(area["ID"]), 
                        name=area["Name"],
                        population=area["Population"],
                        type=area["Type"],
                        pos=(area["X"], area["Y"]),
                        node_type="neighborhood",  # <-- أضف هذا السطر
                        importance=math.log(area["Population"]))
        
        for facility in self.facilities:
            self.G.add_node(facility["id"],
                        name=facility["name"],
                        type=facility["type"],
                        pos=(facility["longitude"], facility["latitude"]),
                        node_type="facility",  # <-- أضف هذا السطر
                        importance=3)

    def _add_edges(self):
        """Add road edges to the graph"""
        for road in self.existing_roads:
            from_node = str(road["from_id"])
            to_node = str(road["to_id"])
            traffic = self._get_traffic_data(from_node, to_node)
            avg_traffic = (traffic["morning"] + traffic["afternoon"] + traffic["evening"] + traffic["night"]) / 4
            travel_time = road["distance_km"] * (1 + avg_traffic / road["capacity"])
            self.G.add_edge(from_node, to_node,
                            distance=road["distance_km"],
                            capacity=road["capacity"],
                            condition=road["condition"],
                            morning_traffic=traffic["morning"],
                            afternoon_traffic=traffic["afternoon"],
                            evening_traffic=traffic["evening"],
                            night_traffic=traffic["night"],
                            avg_traffic=avg_traffic,
                            travel_time=travel_time,
                            road_type="existing")
        
        for road in self.new_roads:
            from_node = str(road["from"])
            to_node = str(road["to"])
            traffic = self._get_traffic_data(from_node, to_node)
            avg_traffic = (traffic["morning"] + traffic["afternoon"] + traffic["evening"] + traffic["night"]) / 4
            travel_time = road["distance"] * (1 + avg_traffic / road["capacity"])
            self.G.add_edge(from_node, to_node,
                            distance=road["distance"],
                            capacity=road["capacity"],
                            cost=road["cost"],
                            morning_traffic=traffic["morning"],
                            afternoon_traffic=traffic["afternoon"],
                            evening_traffic=traffic["evening"],
                            night_traffic=traffic["night"],
                            avg_traffic=avg_traffic,
                            travel_time=travel_time,
                            road_type="proposed")

    def _get_traffic_data(self, from_node, to_node):
        """Helper method to get traffic data for a road"""
        road1 = f"{from_node}-{to_node}"
        road2 = f"{to_node}-{from_node}"
        for pattern in self.traffic_patterns:
            if pattern["road"] == road1 or pattern["road"] == road2:
                return pattern
        # Default traffic values if no specific pattern found
        return {"morning": 1000, "afternoon": 800, "evening": 900, "night": 500}