import csv
import random
import time
from pathlib import Path

from neo4j import GraphDatabase

from benchmark.statistics import calculate_statistics
from workloads.lookup import get_point_lookup_query


URI = "bolt://localhost:7688"

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
    print("Memgraph Point Lookup Benchmark")
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

    driver = GraphDatabase.driver(
        URI,
        auth=None,
    )

    try:

        driver.verify_connectivity()

        print(
            "✓ Memgraph connection successful"
        )

        query = get_point_lookup_query()

        with driver.session() as session:

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

                result = session.run(
                    query,
                    node_id=node_id,
                )

                result.consume()

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

                result = session.run(
                    query,
                    node_id=node_id,
                )

                record = result.single()

                result.consume()

                elapsed = (
                    time.perf_counter()
                    - start_time
                )

                if record is None:
                    raise RuntimeError(
                        f"Node {node_id} "
                        f"was not found."
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

    finally:
        driver.close()


if __name__ == "__main__":
    main()