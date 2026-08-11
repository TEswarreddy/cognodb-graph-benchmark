import csv
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from neo4j import GraphDatabase


load_dotenv()


COGNODB_URI = os.getenv("COGNODB_URI")
COGNODB_USERNAME = os.getenv("COGNODB_USERNAME")
COGNODB_PASSWORD = os.getenv("COGNODB_PASSWORD")

NODES_FILE = Path(
    "datasets/processed/pokec_nodes.csv"
)

EDGES_FILE = Path(
    "datasets/processed/pokec_edges_300k.csv"
)

NODE_BATCH_SIZE = 5_000
EDGE_BATCH_SIZE = 5_000


def create_driver():
    if not COGNODB_URI:
        raise ValueError("COGNODB_URI is missing")

    if not COGNODB_USERNAME:
        raise ValueError("COGNODB_USERNAME is missing")

    if not COGNODB_PASSWORD:
        raise ValueError("COGNODB_PASSWORD is missing")

    return GraphDatabase.driver(
        COGNODB_URI,
        auth=(
            COGNODB_USERNAME,
            COGNODB_PASSWORD,
        ),
    )


def create_index(driver):
    print("Creating index on User.id...")

    with driver.session() as session:
        session.run(
            """
            CREATE INDEX user_id_index IF NOT EXISTS
            FOR (u:User)
            ON (u.id)
            """
        ).consume()

    print("Index created/verified.")


def load_nodes(driver):
    print()
    print("Loading nodes...")

    total_nodes = 0
    start_time = time.perf_counter()

    with open(
        NODES_FILE,
        "r",
        encoding="utf-8",
    ) as file:

        reader = csv.DictReader(file)
        batch = []

        with driver.session() as session:

            for row in reader:
                batch.append(
                    {
                        "id": int(row["node_id"])
                    }
                )

                if len(batch) >= NODE_BATCH_SIZE:

                    session.run(
                        """
                        UNWIND $nodes AS node
                        CREATE (:User {id: node.id})
                        """,
                        nodes=batch,
                    ).consume()

                    total_nodes += len(batch)

                    print(
                        f"Nodes loaded: {total_nodes:,}",
                        end="\r",
                    )

                    batch = []

            if batch:
                session.run(
                    """
                    UNWIND $nodes AS node
                    CREATE (:User {id: node.id})
                    """,
                    nodes=batch,
                ).consume()

                total_nodes += len(batch)

    elapsed = time.perf_counter() - start_time

    nodes_per_second = (
        total_nodes / elapsed
        if elapsed > 0
        else 0
    )

    print()
    print(
        f"Nodes loaded       : {total_nodes:,}"
    )
    print(
        f"Node load time     : {elapsed:.3f} seconds"
    )
    print(
        f"Nodes/second       : {nodes_per_second:,.2f}"
    )

    return {
        "count": total_nodes,
        "elapsed": elapsed,
        "per_second": nodes_per_second,
    }


def load_edges(driver):
    print()
    print("Loading relationships...")

    total_edges = 0
    start_time = time.perf_counter()

    with open(
        EDGES_FILE,
        "r",
        encoding="utf-8",
    ) as file:

        reader = csv.DictReader(file)
        batch = []

        with driver.session() as session:

            for row in reader:
                batch.append(
                    {
                        "source": int(row["source_id"]),
                        "target": int(row["target_id"]),
                    }
                )

                if len(batch) >= EDGE_BATCH_SIZE:

                    session.run(
                        """
                        UNWIND $edges AS edge

                        MATCH (source:User {id: edge.source})
                        MATCH (target:User {id: edge.target})

                        CREATE (source)-[:CONNECTS_TO]->(target)
                        """,
                        edges=batch,
                    ).consume()

                    total_edges += len(batch)

                    print(
                        f"Relationships loaded: "
                        f"{total_edges:,}",
                        end="\r",
                    )

                    batch = []

            if batch:
                session.run(
                    """
                    UNWIND $edges AS edge

                    MATCH (source:User {id: edge.source})
                    MATCH (target:User {id: edge.target})

                    CREATE (source)-[:CONNECTS_TO]->(target)
                    """,
                    edges=batch,
                ).consume()

                total_edges += len(batch)

    elapsed = time.perf_counter() - start_time

    edges_per_second = (
        total_edges / elapsed
        if elapsed > 0
        else 0
    )

    print()
    print(
        f"Relationships loaded : {total_edges:,}"
    )
    print(
        f"Relationship time    : {elapsed:.3f} seconds"
    )
    print(
        f"Relationships/second : {edges_per_second:,.2f}"
    )

    return {
        "count": total_edges,
        "elapsed": elapsed,
        "per_second": edges_per_second,
    }


def verify_database(driver):
    print()
    print("Verifying CognoDB...")

    with driver.session() as session:

        node_result = session.run(
            """
            MATCH (u:User)
            RETURN count(u) AS count
            """
        )

        node_count = node_result.single()["count"]

        edge_result = session.run(
            """
            MATCH ()-[r:CONNECTS_TO]->()
            RETURN count(r) AS count
            """
        )

        edge_count = edge_result.single()["count"]

    print(
        f"Database nodes         : {node_count:,}"
    )
    print(
        f"Database relationships : {edge_count:,}"
    )

    return node_count, edge_count


def main():
    print("=" * 60)
    print("CognoDB Dataset Loader")
    print("=" * 60)

    driver = create_driver()

    try:
        driver.verify_connectivity()

        print("✓ CognoDB connection successful")

        create_index(driver)

        total_start = time.perf_counter()

        node_stats = load_nodes(driver)
        edge_stats = load_edges(driver)

        total_elapsed = (
            time.perf_counter() - total_start
        )

        node_count, edge_count = verify_database(
            driver
        )

        print()
        print("=" * 60)
        print("LOAD SUMMARY")
        print("=" * 60)

        print(
            f"Nodes                 : {node_count:,}"
        )

        print(
            f"Relationships         : {edge_count:,}"
        )

        print(
            f"Node load time        : "
            f"{node_stats['elapsed']:.3f} sec"
        )

        print(
            f"Relationship load time: "
            f"{edge_stats['elapsed']:.3f} sec"
        )

        print(
            f"Total load time       : "
            f"{total_elapsed:.3f} sec"
        )

        print(
            f"Nodes/sec             : "
            f"{node_stats['per_second']:,.2f}"
        )

        print(
            f"Relationships/sec     : "
            f"{edge_stats['per_second']:,.2f}"
        )

        print("=" * 60)

    finally:
        driver.close()


if __name__ == "__main__":
    main()