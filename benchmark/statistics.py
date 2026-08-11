from statistics import mean, median


def percentile(values, percentile):
    """
    Calculate a percentile using linear interpolation.
    """

    if not values:
        raise ValueError("Cannot calculate percentile of empty data")

    sorted_values = sorted(values)

    if len(sorted_values) == 1:
        return sorted_values[0]

    position = (len(sorted_values) - 1) * percentile

    lower = int(position)
    upper = lower + 1

    if upper >= len(sorted_values):
        return sorted_values[-1]

    fraction = position - lower

    return (
        sorted_values[lower]
        + fraction
        * (sorted_values[upper] - sorted_values[lower])
    )


def calculate_statistics(latencies_ms):
    if not latencies_ms:
        raise ValueError("No latency measurements provided")

    return {
        "iterations": len(latencies_ms),
        "min_ms": min(latencies_ms),
        "max_ms": max(latencies_ms),
        "mean_ms": mean(latencies_ms),
        "median_ms": median(latencies_ms),
        "p50_ms": percentile(latencies_ms, 0.50),
        "p95_ms": percentile(latencies_ms, 0.95),
    }