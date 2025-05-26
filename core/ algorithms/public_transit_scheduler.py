# core/algorithms/public_transit_scheduler.py

def schedule_transit(lines, max_buses):
    """
    جدولة خطوط الباص أو المترو لتقليل وقت الانتظار وزيادة التغطية.

    lines: قائمة من الخطوط، كل خط عبارة عن dict فيه:
        {
            "line_id": str,
            "start_time": int,
            "end_time": int,
            "passenger_demand": int
        }

    max_buses: عدد الباصات المتاح.

    يرجع: الخطوط المختارة + مجموع الركاب
    """
    n = len(lines)
    lines.sort(key=lambda x: x["end_time"])

    # DP[i]: أقصى عدد ركاب ممكن ننقلهم باختيار من أول خط حتى الخط i
    dp = [0] * (n + 1)
    prev = [-1] * n  # prev[i] = آخر خط لا يتعارض مع الخط i

    for i in range(n):
        for j in range(i-1, -1, -1):
            if lines[j]["end_time"] <= lines[i]["start_time"]:
                prev[i] = j
                break

    for i in range(1, n + 1):
        include = lines[i-1]["passenger_demand"]
        if prev[i-1] != -1:
            include += dp[prev[i-1] + 1]
        dp[i] = max(dp[i-1], include)

    # استرجاع الخطوط المختارة
    result = []
    i = n
    while i > 0:
        if dp[i] != dp[i-1]:
            result.append(lines[i-1])
            i = prev[i-1] + 1
        else:
            i -= 1

    return result[::-1], dp[n]
