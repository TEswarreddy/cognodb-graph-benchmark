import time

from neo4j import GraphDatabase

from benchmark.statistics import calculate_statistics
from workloads.aggregation import get_aggregation_query


URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "benchmark_password"

WARMUP_ITERATIONS = 20
MEASURED_ITERATIONS = 100


def main():

    print("=" * 60)
    print("Neo4j Aggregation Benchmark")
    print("=" * 60)

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

        query = get_aggregation_query()

        with driver.session() as session:

            print(
                f"Warm-up: "
                f"{WARMUP_ITERATIONS} iterations"
            )

            for _ in range(
                WARMUP_ITERATIONS
            ):

                result = session.run(query)

                result.consume()

            print(
                f"Measurement: "
                f"{MEASURED_ITERATIONS} iterations"
            )

            latencies = []

            for i in range(
                MEASURED_ITERATIONS
            ):

                start_time = (
                    time.perf_counter()
                )

                result = session.run(query)

                records = list(result)

                elapsed = (
                    time.perf_counter()
                    - start_time
                )

                if not records:
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

    finally:
        driver.close()


if __name__ == "__main__":
    main()