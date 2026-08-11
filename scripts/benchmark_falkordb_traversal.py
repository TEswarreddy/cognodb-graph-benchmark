import csv
import time
from pathlib import Path

from falkordb import FalkorDB

from benchmark.statistics import calculate_statistics
from workloads.traversal import get_traversal_query


HOST = "localhost"
PORT = 6379
GRAPH_NAME = "pokec"

PROCESSED_DIR = Path(
    "datasets/processed"
)

WARMUP_ITERATIONS = 20
MEASURED_ITERATIONS = 100


def load_start_nodes(depth):

    file_path = (
        PROCESSED_DIR
        / f"traversal_starts_{depth}hop.csv"
    )

    node_ids = []

    with open(
        file_path,
        "r",
        encoding="utf-8",
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            node_ids.append(
                int(row["node_id"])
            )

    if len(node_ids) != 100:

        raise ValueError(
            f"Expected 100 start nodes, "
            f"found {len(node_ids)}"
        )

    return node_ids


def convert_query(query):

    # FalkorDB uses the same Cypher-style
    # traversal syntax, but the query helper
    # may return a Neo4j-style string.

    return query


def run_benchmark(
    graph,
    depth,
    start_nodes,
):

    query = convert_query(
        get_traversal_query(depth)
    )

    print()
    print(
        f"Running {depth}-hop traversal..."
    )

    print(
        f"Warm-up: "
        f"{WARMUP_ITERATIONS} iterations"
    )

    for i in range(
        WARMUP_ITERATIONS
    ):

        start_id = start_nodes[
            i % len(start_nodes)
        ]

        result = graph.query(
            query,
            params={
                "start_id": start_id
            },
        )

        # Force result processing.
        result.result_set

    print(
        f"Measurement: "
        f"{MEASURED_ITERATIONS} iterations"
    )

    latencies = []

    for i in range(
        MEASURED_ITERATIONS
    ):

        start_id = start_nodes[
            i % len(start_nodes)
        ]

        start_time = time.perf_counter()

        result = graph.query(
            query,
            params={
                "start_id": start_id
            },
        )

        result.result_set

        elapsed = (
            time.perf_counter()
            - start_time
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

    return calculate_statistics(
        latencies
    )


def main():

    print("=" * 60)
    print("FalkorDB Traversal Benchmark")
    print("=" * 60)

    client = FalkorDB(
        host=HOST,
        port=PORT,
    )

    graph = client.select_graph(
        GRAPH_NAME
    )

    # Connectivity check.
    result = graph.query(
        "RETURN 1"
    )

    if not result.result_set:

        raise RuntimeError(
            "FalkorDB connection test failed."
        )

    print(
        "✓ FalkorDB connection successful"
    )

    results = []

    for depth in [1, 2, 3]:

        start_nodes = load_start_nodes(
            depth
        )

        print()
        print(
            f"Start-node pool: "
            f"{len(start_nodes)}"
        )

        stats = run_benchmark(
            graph,
            depth,
            start_nodes,
        )

        results.append(
            (
                depth,
                stats,
            )
        )

        print()
        print(
            f"{depth}-hop results:"
        )

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

    print()

    for depth, stats in results:

        print(
            f"{depth}-hop traversal      "
            f"p50={stats['p50_ms']:.3f} ms "
            f"p95={stats['p95_ms']:.3f} ms"
        )


if __name__ == "__main__":
    main()