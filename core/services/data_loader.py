import json

class DataLoader:
    def __init__(self, json_filepath):
        self.json_filepath = json_filepath
        self.data = None
        self.traffic_patterns = []
        self.metro_lines = []
        self.bus_routes = []
        self.public_transport_demand = []

        self.load_data()

    def load_data(self):
        """Load JSON data from file and initialize datasets."""
        with open(self.json_filepath, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

        # Extract datasets
        self.traffic_patterns = self.data.get("traffic_patterns", [])
        self.metro_lines = self.data.get("metro_lines", [])
        self.bus_routes = self.data.get("bus_routes", [])
        self.public_transport_demand = self.data.get("public_transport_demand", [])

    def get_traffic_patterns(self):
        """Return the list of traffic patterns."""
        return self.traffic_patterns

    def get_metro_lines(self):
        """Return the list of metro lines."""
        return self.metro_lines

    def get_bus_routes(self):
        """Return the list of bus routes."""
        return self.bus_routes

    def get_public_transport_demand(self):
        """Return the list of public transport demand."""
        return self.public_transport_demand

    def find_traffic_by_road(self, road_id):
        """Return traffic data for a specific road."""
        for pattern in self.traffic_patterns:
            if pattern["road"] == road_id:
                return pattern
        return None

# Example usage:
if __name__ == "__main__":
    # Instantiate DataLoader with your JSON file path
    data_loader = DataLoader("data/transport.json")    
    # Access data
    traffic_patterns = data_loader.get_traffic_patterns()
    # Example: print all roads
    for pattern in traffic_patterns:
        print(f"Road: {pattern['road']}, Morning Traffic: {pattern['morning']}")