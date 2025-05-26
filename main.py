import json
from core.models.data_module import CairoMap
from core.services.data_loader import DataLoader
from gui.gui import CairoMapGUI
import tkinter as tk

def load_data(cairo_map):
    """Load all data into the CairoMap instance"""
    try:
        # Load neighborhoods
        with open('data/neighborhoods.json', 'r', encoding='utf-8') as f:
            cairo_map.neighborhoods = json.load(f)
        
        # Load facilities
        with open('data/facilities.json', 'r', encoding='utf-8') as f:
            cairo_map.facilities = json.load(f)
        
        # Load roads
        with open('data/roads.json', 'r', encoding='utf-8') as f:
            roads_data = json.load(f)
            cairo_map.existing_roads = roads_data.get("existing_roads", [])
            cairo_map.new_roads = roads_data.get("new_roads", [])
        
        # Load transport data using DataLoader
        transport_loader = DataLoader('data/transport.json')
        cairo_map.traffic_patterns = transport_loader.get_traffic_patterns()
        cairo_map.metro_lines = transport_loader.get_metro_lines()
        cairo_map.bus_routes = transport_loader.get_bus_routes()
        cairo_map.public_transport_demand = transport_loader.get_public_transport_demand()
        
        # Build the graph
        cairo_map._add_nodes()
        cairo_map._add_edges()
        
        print(f"Data loaded successfully! Nodes: {len(cairo_map.G.nodes())}, Edges: {len(cairo_map.G.edges())}")
        return True
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        return False

def main():
    # Create CairoMap instance
    cairo_map = CairoMap()
    
    # Load data
    if not load_data(cairo_map):
        print("Failed to load data. Exiting...")
        return
    
    # Create and run GUI
    root = tk.Tk()
    app = CairoMapGUI(root, cairo_map)
    root.mainloop()

if __name__ == "__main__":
    main()