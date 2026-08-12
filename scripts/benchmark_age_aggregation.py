import time

import psycopg

from benchmark.statistics import calculate_statistics


HOST = "localhost"
PORT = 5455
DATABASE = "graphdb"
USER = "postgres"
PASSWORD = "benchmark_password"

GRAPH_NAME = "pokec"

WARMUP_ITERATIONS = 20
MEASURED_ITERATIONS = 100


def connect():
    return psycopg.connect(
        host=HOST,
        port=PORT,
        dbname=DATABASE,
        user=USER,
        password=PASSWORD,
    )


def initialize_age(conn):
    """Initialize Apache AGE for the current PostgreSQL session."""

    with conn.cursor() as cursor:
        cursor.execute("LOAD 'age'")
        cursor.execute(
            'SET search_path = ag_catalog, "$user", public'
        )


def run_aggregation(conn, query):
    """
    Execute the AGE aggregation query.

    IMPORTANT:
    The Cypher query returns TWO columns:
        1. node_id
        2. connection_count

    Therefore the PostgreSQL column definition must
    also contain TWO agtype columns.
    """

    with conn.cursor() as cursor:

        sql = f"""
        SELECT *
        FROM ag_catalog.cypher(
            '{GRAPH_NAME}',
            $$
            {query}
            $$
        ) AS result(
            node_id ag_catalog.agtype,
            connection_count ag_catalog.agtype
        )
        """

        cursor.execute(sql)

        return cursor.fetchall()


def get_aggregation_query():
    """
    Find the 100 users with the highest number
    of outgoing CONNECTS_TO relationships.
    """

    return """
    MATCH (u:User)-[:CONNECTS_TO]->()
    RETURN
        u.id AS node_id,
        count(*) AS connection_count
    ORDER BY connection_count DESC
    LIMIT 100
    """


def main():

    print("=" * 60)
    print("Apache AGE Aggregation Benchmark")
    print("=" * 60)

    conn = connect()

    try:

        # --------------------------------------------------
        # Initialize AGE
        # --------------------------------------------------

        initialize_age(conn)

        print(
            "✓ Apache AGE connection successful"
        )

        query = get_aggregation_query()

        # --------------------------------------------------
        # Warm-up
        # --------------------------------------------------

        print(
            f"Warm-up: "
            f"{WARMUP_ITERATIONS} iterations"
        )

        for _ in range(
            WARMUP_ITERATIONS
        ):

            rows = run_aggregation(
                conn,
                query
            )

            rows = list(rows)

            if not rows:
                raise RuntimeError(
                    "Aggregation returned no results "
                    "during warm-up."
                )

        # --------------------------------------------------
        # Measurement
        # --------------------------------------------------

        print(
            f"Measurement: "
            f"{MEASURED_ITERATIONS} iterations"
        )

        latencies = []

        for i in range(
            MEASURED_ITERATIONS
        ):

            start_time = time.perf_counter()

            rows = run_aggregation(
                conn,
                query
            )

            # Force complete result materialization.
            rows = list(rows)

            elapsed = (
                time.perf_counter()
                - start_time
            )

            if not rows:
                raise RuntimeError(
                    "Aggregation returned no results."
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

        # --------------------------------------------------
        # Statistics
        # --------------------------------------------------

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

        conn.close()


if __name__ == "__main__":
    main()