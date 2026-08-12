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

ALREADY_LOADED = 2000
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


def main():

    print("=" * 60)
    print("Apache AGE Relationship Resume Loader")
    print("=" * 60)

    print(
        f"Previously loaded : "
        f"{ALREADY_LOADED:,}"
    )

    print(
        "Skipping first 2,000 CSV rows..."
    )

    conn = get_connection()

    try:

        setup_age(conn)

        print(
            "✓ AGE connection successful"
        )

        start_time = time.perf_counter()

        new_count = 0
        batch = []

        with conn.cursor() as cursor:

            with open(
                EDGES_FILE,
                "r",
                encoding="utf-8",
                newline="",
            ) as file:

                reader = csv.DictReader(file)

                for _ in range(
                    ALREADY_LOADED
                ):
                    next(reader)

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

                        conn.commit()

                        new_count += len(batch)

                        batch.clear()

                        if new_count % 5000 == 0:

                            elapsed = (
                                time.perf_counter()
                                - start_time
                            )

                            rate = (
                                new_count / elapsed
                                if elapsed > 0
                                else 0
                            )

                            print(
                                f"New relationships loaded: "
                                f"{new_count:,}/"
                                f"{300000 - ALREADY_LOADED:,} "
                                f"({rate:.2f}/sec)"
                            )

                if batch:

                    insert_edge_batch(
                        cursor,
                        batch,
                    )

                    conn.commit()

                    new_count += len(batch)

        elapsed = (
            time.perf_counter()
            - start_time
        )

        rate = (
            new_count / elapsed
            if elapsed > 0
            else 0
        )

        print()
        print("=" * 60)
        print("RESUME SUMMARY")
        print("=" * 60)

        print(
            f"Previously loaded : "
            f"{ALREADY_LOADED:,}"
        )

        print(
            f"Newly loaded      : "
            f"{new_count:,}"
        )

        print(
            f"Final relationships: "
            f"{ALREADY_LOADED + new_count:,}"
        )

        print(
            f"Elapsed time      : "
            f"{elapsed:.3f} sec"
        )

        print(
            f"Relationships/sec : "
            f"{rate:.2f}"
        )

        print("=" * 60)

    finally:
        conn.close()


if __name__ == "__main__":
    main()