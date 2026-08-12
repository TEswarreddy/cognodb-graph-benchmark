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

NODES_FILE = Path(
    "datasets/processed/pokec_nodes.csv"
)

EDGES_FILE = Path(
    "datasets/processed/pokec_edges_300k.csv"
)

NODE_BATCH_SIZE = 1000
EDGE_BATCH_SIZE = 1000


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
        cursor.execute(
            "CREATE EXTENSION IF NOT EXISTS age"
        )

        cursor.execute(
            "LOAD 'age'"
        )

        cursor.execute(
            """
            SET search_path =
                ag_catalog,
                "$user",
                public
            """
        )


def graph_exists(conn):
    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT 1
            FROM ag_catalog.ag_graph
            WHERE name = %s
            """,
            (GRAPH_NAME,),
        )

        return cursor.fetchone() is not None


def create_graph(conn):
    if graph_exists(conn):
        print(
            f"✓ AGE graph already exists: {GRAPH_NAME}"
        )
        return

    with conn.cursor() as cursor:
        cursor.execute(
            f"""
            SELECT create_graph('{GRAPH_NAME}')
            """
        )

    print(
        f"✓ AGE graph created: {GRAPH_NAME}"
    )


def cypher_query(cursor, cypher):
    query = f"""
        SELECT *
        FROM cypher(
            '{GRAPH_NAME}',
            $$
            {cypher}
            $$
        ) AS (result agtype)
    """

    cursor.execute(query)


def load_nodes(conn):
    print()
    print("Loading nodes...")

    start = time.perf_counter()
    count = 0

    with conn.cursor() as cursor:
        with open(
            NODES_FILE,
            "r",
            encoding="utf-8",
        ) as file:

            reader = csv.DictReader(file)

            batch = []

            for row in reader:
                node_id = int(row["node_id"])
                batch.append(node_id)

                if len(batch) >= NODE_BATCH_SIZE:
                    insert_node_batch(
                        cursor,
                        batch,
                    )

                    count += len(batch)
                    batch.clear()

                    if count % 5000 == 0:
                        print(
                            f"Nodes loaded: {count:,}"
                        )

            if batch:
                insert_node_batch(
                    cursor,
                    batch,
                )

                count += len(batch)

    conn.commit()

    elapsed = time.perf_counter() - start

    rate = (
        count / elapsed
        if elapsed > 0
        else 0
    )

    print()
    print(
        f"Nodes loaded       : {count:,}"
    )
    print(
        f"Node load time     : {elapsed:.3f} seconds"
    )
    print(
        f"Nodes/second       : {rate:.2f}"
    )

    return count


def insert_node_batch(cursor, node_ids):

    values = ",".join(
        f"{{id: {node_id}}}"
        for node_id in node_ids
    )

    cypher = f"""
        UNWIND [{values}] AS props
        CREATE (u:User)
        SET u.id = props.id
        RETURN count(u)
    """

    cypher_query(
        cursor,
        cypher,
    )


def load_edges(conn):
    print()
    print("Loading relationships...")

    start = time.perf_counter()
    count = 0

    with conn.cursor() as cursor:
        with open(
            EDGES_FILE,
            "r",
            encoding="utf-8",
        ) as file:

            reader = csv.DictReader(file)

            batch = []

            for row in reader:

                source_id = int(
                    row["source"]
                )

                target_id = int(
                    row["target"]
                )

                batch.append(
                    (
                        source_id,
                        target_id,
                    )
                )

                if len(batch) >= EDGE_BATCH_SIZE:

                    insert_edge_batch(
                        cursor,
                        batch,
                    )

                    count += len(batch)
                    batch.clear()

                    if count % 5000 == 0:
                        print(
                            f"Relationships loaded: "
                            f"{count:,}"
                        )

            if batch:
                insert_edge_batch(
                    cursor,
                    batch,
                )

                count += len(batch)

    conn.commit()

    elapsed = time.perf_counter() - start

    rate = (
        count / elapsed
        if elapsed > 0
        else 0
    )

    print()
    print(
        f"Relationships loaded : {count:,}"
    )
    print(
        f"Relationship load time: "
        f"{elapsed:.3f} seconds"
    )
    print(
        f"Relationships/second: "
        f"{rate:.2f}"
    )

    return count


def insert_edge_batch(cursor, edges):

    rows = ",".join(
        f"({source_id},{target_id})"
        for source_id, target_id in edges
    )

    cypher = f"""
        UNWIND [
            {rows}
        ] AS edge

        MATCH (a:User {{id: edge[0]}})
        MATCH (b:User {{id: edge[1]}})

        CREATE (a)-[:CONNECTS_TO]->(b)

        RETURN count(*)
    """

    cypher_query(
        cursor,
        cypher,
    )


def main():

    print("=" * 60)
    print("Apache AGE Dataset Loader")
    print("=" * 60)

    conn = get_connection()

    try:

        setup_age(conn)

        print(
            "✓ AGE connection successful"
        )

        create_graph(conn)

        node_count = load_nodes(
            conn
        )

        edge_count = load_edges(
            conn
        )

        print()
        print("=" * 60)
        print("AGE LOAD SUMMARY")
        print("=" * 60)

        print(
            f"Nodes loaded         : "
            f"{node_count:,}"
        )

        print(
            f"Relationships loaded : "
            f"{edge_count:,}"
        )

        print("=" * 60)

    finally:
        conn.close()


if __name__ == "__main__":
    main()