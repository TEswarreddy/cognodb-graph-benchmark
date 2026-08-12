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
START_NODE_POOL_SIZE = 100


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
    Execute an Apache AGE Cypher query.

    AGE requires the graph name and Cypher query to be
    SQL literals rather than PostgreSQL parameters.
    """

    with conn.cursor() as cursor:

        escaped_query = query.replace(
            "$$",
            "$$$$"
        )

        sql = f"""
        SELECT *
        FROM ag_catalog.cypher(
            '{GRAPH_NAME}',
            $$
            {escaped_query}
            $$
        ) AS result(value ag_catalog.agtype)
        """

        cursor.execute(sql)

        return cursor.fetchall()


def get_start_nodes(conn):
    """
    Select a deterministic pool of 100 User IDs.
    """

    with conn.cursor() as cursor:

        cursor.execute(
            """
            SELECT id
            FROM pokec."User"
            ORDER BY id
            LIMIT %s
            """,
            (START_NODE_POOL_SIZE,),
        )

        rows = cursor.fetchall()

    return [
        int(row[0])
        for row in rows
    ]


def benchmark_hop(conn, hop_count, start_nodes):

    if hop_count == 1:

        query_template = """
        MATCH (u:User)-[:CONNECTS_TO]->(v:User)
        WHERE u.id = {start_id}
        RETURN v
        """

    elif hop_count == 2:

        query_template = """
        MATCH (u:User)-[:CONNECTS_TO]->()
              -[:CONNECTS_TO]->(v:User)
        WHERE u.id = {start_id}
        RETURN v
        """

    elif hop_count == 3:

        query_template = """
        MATCH (u:User)-[:CONNECTS_TO]->()
              -[:CONNECTS_TO]->()
              -[:CONNECTS_TO]->(v:User)
        WHERE u.id = {start_id}
        RETURN v
        """

    else:
        raise ValueError(
            f"Unsupported hop count: {hop_count}"
        )

    print(
        f"Start-node pool: {len(start_nodes)}"
    )

    print()

    print(
        f"Running {hop_count}-hop traversal..."
    )

    # --------------------------------------------------
    # Warm-up
    # --------------------------------------------------

    print(
        f"Warm-up: {WARMUP_ITERATIONS} iterations"
    )

    for _ in range(WARMUP_ITERATIONS):

        start_id = random.choice(
            start_nodes
        )

        query = query_template.format(
            start_id=start_id
        )

        rows = run_cypher(
            conn,
            query
        )

        # Force result materialization.
        list(rows)

    # --------------------------------------------------
    # Measurement
    # --------------------------------------------------

    print(
        f"Measurement: {MEASURED_ITERATIONS} iterations"
    )

    latencies = []

    for i in range(
        MEASURED_ITERATIONS
    ):

        start_id = random.choice(
            start_nodes
        )

        query = query_template.format(
            start_id=start_id
        )

        start_time = time.perf_counter()

        rows = run_cypher(
            conn,
            query
        )

        # Force result materialization.
        list(rows)

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
                f"{i + 1}/{MEASURED_ITERATIONS}"
            )

    # --------------------------------------------------
    # Statistics
    # --------------------------------------------------

    stats = calculate_statistics(
        latencies
    )

    print()

    print(
        f"{hop_count}-hop results:"
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

    return stats


def main():

    print("=" * 60)
    print("Apache AGE Traversal Benchmark")
    print("=" * 60)

    conn = connect()

    try:

        initialize_age(conn)

        # --------------------------------------------------
        # Connection test
        # --------------------------------------------------

        run_cypher(
            conn,
            "RETURN 1"
        )

        print(
            "✓ Apache AGE connection successful"
        )

        # --------------------------------------------------
        # Get benchmark start-node pool
        # --------------------------------------------------

        start_nodes = get_start_nodes(
            conn
        )

        if len(start_nodes) != START_NODE_POOL_SIZE:

            raise RuntimeError(
                f"Expected "
                f"{START_NODE_POOL_SIZE} start nodes, "
                f"but found {len(start_nodes)}."
            )

        # --------------------------------------------------
        # Run 1, 2 and 3 hop benchmarks
        # --------------------------------------------------

        results = {}

        for hop_count in [1, 2, 3]:

            results[hop_count] = benchmark_hop(
                conn,
                hop_count,
                start_nodes,
            )

            print()

        # --------------------------------------------------
        # Summary
        # --------------------------------------------------

        print("=" * 60)
        print("TRAVERSAL SUMMARY")
        print("=" * 60)

        for hop_count in [1, 2, 3]:

            stats = results[hop_count]

            print(
                f"{hop_count}-hop traversal      "
                f"p50={stats['p50_ms']:.3f} ms "
                f"p95={stats['p95_ms']:.3f} ms"
            )

        print("=" * 60)

    finally:

        conn.close()


if __name__ == "__main__":
    main()