import time
import random

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

READ_WRITE_PAIR_COUNT = 100

# Temporary property used only for the benchmark.
BENCHMARK_PROPERTY = "benchmark_value"


def connect():
    return psycopg.connect(
        host=HOST,
        port=PORT,
        dbname=DATABASE,
        user=USER,
        password=PASSWORD,
    )


def initialize_age(conn):
    """
    Initialize Apache AGE for the current PostgreSQL session.
    """

    with conn.cursor() as cursor:
        cursor.execute("LOAD 'age'")

        cursor.execute(
            'SET search_path = ag_catalog, "$user", public'
        )


def run_cypher(conn, query):
    """
    Execute an AGE Cypher query.

    AGE requires the graph name and query to be
    SQL literals rather than PostgreSQL parameters.
    """

    with conn.cursor() as cursor:

        sql = f"""
        SELECT *
        FROM ag_catalog.cypher(
            '{GRAPH_NAME}',
            $$
            {query}
            $$
        ) AS result(value ag_catalog.agtype)
        """

        cursor.execute(sql)

        return cursor.fetchall()


def get_start_nodes(conn):
    """
    Select 100 actual AGE graph IDs from the User label.
    """

    with conn.cursor() as cursor:

        cursor.execute(
            """
            SELECT id
            FROM pokec."User"
            ORDER BY id
            LIMIT %s
            """,
            (READ_WRITE_PAIR_COUNT,),
        )

        rows = cursor.fetchall()

    return [
        int(row[0])
        for row in rows
    ]


def read_node(conn, graph_id):
    """
    Read one User node.
    """

    query = f"""
    MATCH (u:User)
    WHERE id(u) = {graph_id}
    RETURN u
    """

    return run_cypher(
        conn,
        query
    )


def write_node(conn, graph_id, value):
    """
    Update one User node with a temporary benchmark property.
    """

    query = f"""
    MATCH (u:User)
    WHERE id(u) = {graph_id}
    SET u.{BENCHMARK_PROPERTY} = {value}
    RETURN u
    """

    return run_cypher(
        conn,
        query
    )


def cleanup_benchmark_property(conn):
    """
    Remove the temporary benchmark property from all User nodes.
    """

    query = f"""
    MATCH (u:User)
    WHERE u.{BENCHMARK_PROPERTY} IS NOT NULL
    REMOVE u.{BENCHMARK_PROPERTY}
    RETURN count(u)
    """

    rows = run_cypher(
        conn,
        query
    )

    return rows


def run_read_write_pair(conn, graph_id, value):
    """
    Execute one read followed by one write.

    The elapsed time covers both operations.
    """

    # -----------------------------
    # READ
    # -----------------------------

    rows = read_node(
        conn,
        graph_id
    )

    rows = list(rows)

    if not rows:
        raise RuntimeError(
            f"Read returned no result "
            f"for AGE graph ID {graph_id}"
        )

    # -----------------------------
    # WRITE
    # -----------------------------

    rows = write_node(
        conn,
        graph_id,
        value
    )

    rows = list(rows)

    if not rows:
        raise RuntimeError(
            f"Write returned no result "
            f"for AGE graph ID {graph_id}"
        )


def main():

    print("=" * 60)
    print("Apache AGE Mixed Read/Write Benchmark")
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

        # --------------------------------------------------
        # Get benchmark nodes
        # --------------------------------------------------

        start_nodes = get_start_nodes(
            conn
        )

        if len(start_nodes) != READ_WRITE_PAIR_COUNT:

            raise RuntimeError(
                f"Expected "
                f"{READ_WRITE_PAIR_COUNT} nodes, "
                f"but found {len(start_nodes)}."
            )

        print(
            f"Selected read/write pairs: "
            f"{len(start_nodes)}"
        )

        # --------------------------------------------------
        # Warm-up
        # --------------------------------------------------

        print(
            f"Warm-up: "
            f"{WARMUP_ITERATIONS} iterations"
        )

        for i in range(
            WARMUP_ITERATIONS
        ):

            graph_id = random.choice(
                start_nodes
            )

            run_read_write_pair(
                conn,
                graph_id,
                i + 1
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

            graph_id = random.choice(
                start_nodes
            )

            value = i + 1

            start_time = time.perf_counter()

            run_read_write_pair(
                conn,
                graph_id,
                value
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

        # --------------------------------------------------
        # Statistics
        # --------------------------------------------------

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

        # --------------------------------------------------
        # Cleanup benchmark property
        # --------------------------------------------------

        try:
            cleanup_benchmark_property(conn)
        except Exception as cleanup_error:
            print(
                f"Warning: benchmark cleanup failed: "
                f"{cleanup_error}"
            )

        conn.close()


if __name__ == "__main__":
    main()