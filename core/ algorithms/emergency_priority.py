from .traffic_signal_optimizer import optimize_traffic_signal

def adjust_signal_for_emergency(intersection_data, emergency_direction):
    """
    يزيد الوقت بشكل جشع للاتجاه اللي فيه سيارة إسعاف
    """
    optimized = optimize_traffic_signal(intersection_data)
    emergency_time = min(60, optimized[emergency_direction] * 1.5)
    remaining = 100 - emergency_time
    other_dirs = [d for d in intersection_data if d != emergency_direction]
    total_other = sum(intersection_data[d] for d in other_dirs)
    
    result = {emergency_direction: round(emergency_time, 2)}
    for d in other_dirs:
        portion = (intersection_data[d] / total_other) if total_other else 1/len(other_dirs)
        result[d] = round(portion * remaining, 2)
    return result