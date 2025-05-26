def optimize_traffic_signal(car_counts):
    total = sum(car_counts.values())
    if total == 0:
        return {direction: 25 for direction in car_counts}  # equal if no cars
    
    return {
        direction: round((count / total) * 100, 2)
        for direction, count in car_counts.items()
    }

test_data = {'north': 50, 'south': 30, 'east': 70, 'west': 20}
print(optimize_traffic_signal(test_data))
