# core/algorithms/road_maintenance_optimizer.py

def optimize_road_maintenance(roads, budget):
    """
    roads: قائمة بالطرق:
        [
            {"road_id": str, "repair_cost": int, "urgency": int}
        ]
    budget: الحد الأقصى للميزانية

    يرجع: الطرق المختارة + إجمالي الأهمية
    """
    n = len(roads)
    dp = [[0] * (budget + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        cost = roads[i-1]["repair_cost"]
        urgency = roads[i-1]["urgency"]
        for w in range(budget + 1):
            if cost <= w:
                dp[i][w] = max(dp[i-1][w], dp[i-1][w - cost] + urgency)
            else:
                dp[i][w] = dp[i-1][w]

    # استرجاع الطرق المختارة
    selected = []
    w = budget
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i-1][w]:
            selected.append(roads[i-1])
            w -= roads[i-1]["repair_cost"]

    return selected[::-1], dp[n][budget]
