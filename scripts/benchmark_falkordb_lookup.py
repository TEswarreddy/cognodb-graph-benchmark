import csv
import random
import time
from pathlib import Path

from falkordb import FalkorDB

from benchmark.statistics import calculate_statistics


HOST = "localhost"
PORT = 6379
GRAPH_NAME = "pokec"

NODES_FILE = Path(
    "datasets/processed/pokec_nodes.csv"
)

RANDOM_SEED = 42
SAMPLE_SIZE = 100

WARMUP_ITERATIONS = 20
MEASURED_ITERATIONS = 100


def load_node_ids():

    node_ids = []

    with open(
        NODES_FILE,
        "r",
        encoding="utf-8",
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:
            node_ids.append(
                int(row["node_id"])
            )

    return node_ids


def main():

    print("=" * 60)
    print("FalkorDB Point Lookup Benchmark")
    print("=" * 60)

    node_ids = load_node_ids()

    random.seed(RANDOM_SEED)

    selected_nodes = random.sample(
        node_ids,
        SAMPLE_SIZE,
    )

    print(
        f"Selected lookup nodes: "
        f"{len(selected_nodes)}"
    )

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

    query = """
    MATCH (u:User {id: $node_id})
    RETURN u.id
    """

    print(
        f"Warm-up: "
        f"{WARMUP_ITERATIONS} iterations"
    )

    for i in range(
        WARMUP_ITERATIONS
    ):

        node_id = selected_nodes[
            i % len(selected_nodes)
        ]

        result = graph.query(
            query,
            params={
                "node_id": node_id
            },
        )

        if not result.result_set:
            raise RuntimeError(
                f"Node {node_id} not found."
            )

    print(
        f"Measurement: "
        f"{MEASURED_ITERATIONS} iterations"
    )

    latencies = []

    for i in range(
        MEASURED_ITERATIONS
    ):

        node_id = selected_nodes[
            i % len(selected_nodes)
        ]

        start_time = time.perf_counter()

        result = graph.query(
            query,
            params={
                "node_id": node_id
            },
        )

        if not result.result_set:
            raise RuntimeError(
                f"Node {node_id} not found."
            )

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

    stats = calculate_statistics(
        latencies
    )

    print()
    print("=" * 60)
    print("POINT LOOKUP RESULTS")
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