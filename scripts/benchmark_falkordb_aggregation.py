import time

from falkordb import FalkorDB

from benchmark.statistics import calculate_statistics
from workloads.aggregation import get_aggregation_query


HOST = "localhost"
PORT = 6379
GRAPH_NAME = "pokec"

WARMUP_ITERATIONS = 20
MEASURED_ITERATIONS = 100


def main():

    print("=" * 60)
    print("FalkorDB Aggregation Benchmark")
    print("=" * 60)

    client = FalkorDB(
        host=HOST,
        port=PORT,
    )

    graph = client.select_graph(
        GRAPH_NAME
    )

    test = graph.query(
        "RETURN 1"
    )

    if not test.result_set:
        raise RuntimeError(
            "FalkorDB connection failed."
        )

    print(
        "✓ FalkorDB connection successful"
    )

    query = get_aggregation_query()

    print(
        f"Warm-up: "
        f"{WARMUP_ITERATIONS} iterations"
    )

    for _ in range(
        WARMUP_ITERATIONS
    ):

        result = graph.query(query, timeout=60000)

        # Force result materialization.
        result.result_set

    print(
        f"Measurement: "
        f"{MEASURED_ITERATIONS} iterations"
    )

    latencies = []

    for i in range(
        MEASURED_ITERATIONS
    ):

        start_time = time.perf_counter()

        result = graph.query(query)

        rows = result.result_set

        elapsed = (
            time.perf_counter()
            - start_time
        )

        if not rows:
            raise RuntimeError(
                "Aggregation returned "
                "no results."
            )

        latencies.append(
            elapsed * 1000
        )

        if (i + 1) % 20 == 0:

            print(
                f"Completed "
                f"{i + 1}/"
                f"{MEASURED_ITERATIONS}"
            )

    stats = calculate_statistics(
        latencies
    )

    print()
    print("=" * 60)
    print("AGGREGATION RESULTS")
    print("=" * 60)

    print(
        f"p50 : "
        f"{stats['p50_ms']:.3f} ms"
    )

    print(
        f"p95 : "
        f"{stats['p95_ms']:.3f} ms"
    )

    print(
        f"mean: "
        f"{stats['mean_ms']:.3f} ms"
    )

    print(
        f"min : "
        f"{stats['min_ms']:.3f} ms"
    )

    print(
        f"max : "
        f"{stats['max_ms']:.3f} ms"
    )

    print("=" * 60)


if __name__ == "__main__":
    main()