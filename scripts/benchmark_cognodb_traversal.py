import csv
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from neo4j import GraphDatabase

from benchmark.statistics import calculate_statistics
from workloads.traversal import get_traversal_query


load_dotenv()


URI = os.getenv("COGNODB_URI")
USERNAME = os.getenv("COGNODB_USERNAME")
PASSWORD = os.getenv("COGNODB_PASSWORD")

PROCESSED_DIR = Path("datasets/processed")

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

    if len(node_ids) < MEASURED_ITERATIONS:
        raise ValueError(
            f"{file_path} contains only "
            f"{len(node_ids)} nodes."
        )

    return node_ids


def run_traversal_benchmark(
    session,
    depth,
    start_nodes,
):
    query = get_traversal_query(depth)

    print()
    print(
        f"Running {depth}-hop traversal..."
    )

    # -------------------------------------------------
    # Warm-up
    # -------------------------------------------------

    print(
        f"Warm-up: "
        f"{WARMUP_ITERATIONS} iterations"
    )

    for i in range(WARMUP_ITERATIONS):

        start_id = start_nodes[
            i % len(start_nodes)
        ]

        result = session.run(
            query,
            start_id=start_id,
        )

        result.consume()

    # -------------------------------------------------
    # Measurement
    # -------------------------------------------------

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

        result = session.run(
            query,
            start_id=start_id,
        )

        result.consume()

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
    print("CognoDB Traversal Benchmark")
    print("=" * 60)

    driver = GraphDatabase.driver(
        URI,
        auth=(
            USERNAME,
            PASSWORD,
        ),
        connection_timeout=30,
    )

    try:

        driver.verify_connectivity()

        print(
            "✓ CognoDB connection successful"
        )

        results = []

        with driver.session() as session:

            for depth in [1, 2, 3]:

                start_nodes = (
                    load_start_nodes(depth)
                )

                print()
                print(
                    f"Eligible start pool: "
                    f"{len(start_nodes):,}"
                )

                stats = run_traversal_benchmark(
                    session,
                    depth,
                    start_nodes,
                )

                stats["database"] = "CognoDB"
                stats["workload"] = (
                    f"{depth}-hop traversal"
                )
                stats["depth"] = depth

                results.append(stats)

                print()
                print(
                    f"{depth}-hop results:"
                )

                print(
                    f"  p50 : "
                    f"{stats['p50_ms']:.3f} ms"
                )

                print(
                    f"  p95 : "
                    f"{stats['p95_ms']:.3f} ms"
                )

                print(
                    f"  mean: "
                    f"{stats['mean_ms']:.3f} ms"
                )

                print(
                    f"  min : "
                    f"{stats['min_ms']:.3f} ms"
                )

                print(
                    f"  max : "
                    f"{stats['max_ms']:.3f} ms"
                )

        print()
        print("=" * 60)
        print("BENCHMARK COMPLETE")
        print("=" * 60)

        for result in results:

            print(
                f"{result['workload']:<20} "
                f"p50="
                f"{result['p50_ms']:.3f} ms "
                f"p95="
                f"{result['p95_ms']:.3f} ms"
            )

    finally:
        driver.close()


if __name__ == "__main__":
    main()