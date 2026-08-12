import csv
import time
from pathlib import Path

import psycopg


HOST = "localhost"
PORT = 5455
DATABASE = "graphdb"
USER = "postgres"
PASSWORD = "benchmark_password"

GRAPH_NAME = "pokec"

EDGES_FILE = Path(
    "datasets/processed/pokec_edges_300k.csv"
)

BATCH_SIZE = 1000


def get_connection():
    return psycopg.connect(
        host=HOST,
        port=PORT,
        dbname=DATABASE,
        user=USER,
        password=PASSWORD,
    )


def setup_age(conn):
    conn.autocommit = True

    with conn.cursor() as cursor:
        cursor.execute("LOAD 'age'")

        cursor.execute(
            """
            SET search_path =
                ag_catalog,
                "$user",
                public
            """
        )


def insert_edge_batch(cursor, edges):

    # Convert Python tuples into Cypher lists:
    #
    # [[612820,290349],[81414,372823],...]

    rows = ",".join(
        f"[{source_id},{target_id}]"
        for source_id, target_id in edges
    )

    cypher = f"""
        UNWIND [
            {rows}
        ] AS edge

        MATCH (a:User {{id: edge[0]}})
        MATCH (b:User {{id: edge[1]}})

        CREATE (a)-[:CONNECTS_TO]->(b)

        RETURN count(*) AS created
    """

    query = f"""
        SELECT *
        FROM cypher(
            '{GRAPH_NAME}',
            $$
            {cypher}
            $$
        ) AS (created agtype)
    """

    cursor.execute(query)


def load_relationships(conn):

    print("=" * 60)
    print("Apache AGE Relationship Loader")
    print("=" * 60)

    start_time = time.perf_counter()

    count = 0
    batch = []

    with conn.cursor() as cursor:

        with open(
            EDGES_FILE,
            "r",
            encoding="utf-8",
            newline="",
        ) as file:

            reader = csv.DictReader(file)

            expected_columns = {
                "source_id",
                "target_id",
            }

            actual_columns = set(
                reader.fieldnames or []
            )

            if not expected_columns.issubset(
                actual_columns
            ):
                raise RuntimeError(
                    "Unexpected CSV columns: "
                    f"{reader.fieldnames}"
                )

            for row in reader:

                source_id = int(
                    row["source_id"]
                )

                target_id = int(
                    row["target_id"]
                )

                batch.append(
                    (
                        source_id,
                        target_id,
                    )
                )

                if len(batch) >= BATCH_SIZE:

                    insert_edge_batch(
                        cursor,
                        batch,
                    )

                    count += len(batch)

                    conn.commit()

                    batch.clear()

                    if count % 5000 == 0:

                        elapsed = (
                            time.perf_counter()
                            - start_time
                        )

                        rate = (
                            count / elapsed
                            if elapsed > 0
                            else 0
                        )

                        print(
                            f"Relationships loaded: "
                            f"{count:,} "
                            f"({rate:.2f}/sec)"
                        )

            if batch:

                insert_edge_batch(
                    cursor,
                    batch,
                )

                count += len(batch)

                conn.commit()

    elapsed = (
        time.perf_counter()
        - start_time
    )

    rate = (
        count / elapsed
        if elapsed > 0
        else 0
    )

    print()
    print("=" * 60)
    print("RELATIONSHIP LOAD SUMMARY")
    print("=" * 60)

    print(
        f"Relationships loaded : "
        f"{count:,}"
    )

    print(
        f"Relationship load time: "
        f"{elapsed:.3f} seconds"
    )

    print(
        f"Relationships/second : "
        f"{rate:.2f}"
    )

    print("=" * 60)


def main():

    conn = get_connection()

    try:

        setup_age(conn)

        print(
            "✓ AGE connection successful"
        )

        print(
            f"Graph: {GRAPH_NAME}"
        )

        print(
            f"Edges file: {EDGES_FILE}"
        )

        print()

        load_relationships(conn)

    finally:

        conn.close()


if __name__ == "__main__":
    main()