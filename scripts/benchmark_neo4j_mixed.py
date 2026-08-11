import csv
import random
import time
from pathlib import Path

from neo4j import GraphDatabase

from benchmark.statistics import calculate_statistics
from workloads.mixed import get_mixed_read_write_query


URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "benchmark_password"

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
    print("Neo4j Mixed Read/Write Benchmark")
    print("=" * 60)

    node_ids = load_node_ids()

    random.seed(RANDOM_SEED)

    selected_nodes = random.sample(
        node_ids,
        SAMPLE_SIZE * 2,
    )

    pairs = []

    for i in range(
        0,
        SAMPLE_SIZE * 2,
        2,
    ):

        source_id = selected_nodes[i]
        target_id = selected_nodes[i + 1]

        if source_id != target_id:
            pairs.append(
                (
                    source_id,
                    target_id,
                )
            )

    pairs = pairs[:SAMPLE_SIZE]

    if len(pairs) < SAMPLE_SIZE:
        raise RuntimeError(
            "Unable to create 100 pairs."
        )

    print(
        f"Selected read/write pairs: "
        f"{len(pairs)}"
    )

    driver = GraphDatabase.driver(
        URI,
        auth=(
            USERNAME,
            PASSWORD,
        ),
    )

    try:

        driver.verify_connectivity()

        print(
            "✓ Neo4j connection successful"
        )

        query = get_mixed_read_write_query()

        with driver.session() as session:

            print(
                f"Warm-up: "
                f"{WARMUP_ITERATIONS} iterations"
            )

            for i in range(
                WARMUP_ITERATIONS
            ):

                source_id, target_id = pairs[
                    i % len(pairs)
                ]

                result = session.run(
                    query,
                    source_id=source_id,
                    target_id=target_id,
                )

                record = result.single()

                result.consume()

                if record is None:
                    raise RuntimeError(
                        "Mixed workload returned "
                        "no result during warm-up."
                    )

            print(
                f"Measurement: "
                f"{MEASURED_ITERATIONS} iterations"
            )

            latencies = []

            for i in range(
                MEASURED_ITERATIONS
            ):

                source_id, target_id = pairs[
                    i % len(pairs)
                ]

                start_time = (
                    time.perf_counter()
                )

                result = session.run(
                    query,
                    source_id=source_id,
                    target_id=target_id,
                )

                record = result.single()

                result.consume()

                elapsed = (
                    time.perf_counter()
                    - start_time
                )

                if record is None:
                    raise RuntimeError(
                        "Mixed workload returned "
                        "no result."
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
        print("MIXED READ/WRITE RESULTS")
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