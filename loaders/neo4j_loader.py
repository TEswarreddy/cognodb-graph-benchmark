import csv
import time
from pathlib import Path

from neo4j import GraphDatabase


URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "benchmark_password"

NODES_FILE = Path(
    "datasets/processed/pokec_nodes.csv"
)

EDGES_FILE = Path(
    "datasets/processed/pokec_edges_300k.csv"
)

BATCH_SIZE = 5000


def create_driver():
    return GraphDatabase.driver(
        URI,
        auth=(USERNAME, PASSWORD),
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

    start_time = time.perf_counter()

    nodes = []

    total_loaded = 0

    with open(
        NODES_FILE,
        "r",
        encoding="utf-8",
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            nodes.append(
                {
                    "id": int(row["node_id"])
                }
            )

            if len(nodes) >= BATCH_SIZE:

                with driver.session() as session:

                    session.run(
                        """
                        UNWIND $nodes AS node

                        MERGE (
                            u:User {
                                id: node.id
                            }
                        )
                        """,
                        nodes=nodes,
                    ).consume()

                total_loaded += len(nodes)

                print(
                    f"Nodes loaded: "
                    f"{total_loaded:,}",
                    end="\r",
                )

                nodes = []

        if nodes:

            with driver.session() as session:

                session.run(
                    """
                    UNWIND $nodes AS node

                    MERGE (
                        u:User {
                            id: node.id
                        }
                    )
                    """,
                    nodes=nodes,
                ).consume()

            total_loaded += len(nodes)

    elapsed = (
        time.perf_counter()
        - start_time
    )

    print()
    print(
        f"Nodes loaded       : "
        f"{total_loaded:,}"
    )

    print(
        f"Node load time     : "
        f"{elapsed:.3f} seconds"
    )

    if elapsed > 0:

        print(
            f"Nodes/second       : "
            f"{total_loaded / elapsed:.2f}"
        )

    return total_loaded


def load_edges(driver):

    print()
    print("Loading relationships...")

    start_time = time.perf_counter()

    edges = []

    total_loaded = 0

    with open(
        EDGES_FILE,
        "r",
        encoding="utf-8",
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            edges.append(
                {
                    "source": int(
                        row["source_id"]
                    ),
                    "target": int(
                        row["target_id"]
                    ),
                }
            )

            if len(edges) >= BATCH_SIZE:

                with driver.session() as session:

                    session.run(
                        """
                        UNWIND $edges AS edge

                        MATCH (
                            source:User {
                                id: edge.source
                            }
                        )

                        MATCH (
                            target:User {
                                id: edge.target
                            }
                        )

                        CREATE (
                            source
                        )-[:CONNECTS_TO]->(
                            target
                        )
                        """,
                        edges=edges,
                    ).consume()

                total_loaded += len(edges)

                print(
                    f"Relationships loaded: "
                    f"{total_loaded:,}",
                    end="\r",
                )

                edges = []

        if edges:

            with driver.session() as session:

                session.run(
                    """
                    UNWIND $edges AS edge

                    MATCH (
                        source:User {
                            id: edge.source
                        }
                    )

                    MATCH (
                        target:User {
                            id: edge.target
                        }
                    )

                    CREATE (
                        source
                    )-[:CONNECTS_TO]->(
                        target
                    )
                    """,
                    edges=edges,
                ).consume()

            total_loaded += len(edges)

    elapsed = (
        time.perf_counter()
        - start_time
    )

    print()
    print(
        f"Relationships loaded : "
        f"{total_loaded:,}"
    )

    print(
        f"Relationship load time: "
        f"{elapsed:.3f} seconds"
    )

    if elapsed > 0:

        print(
            f"Relationships/second  : "
            f"{total_loaded / elapsed:.2f}"
        )

    return total_loaded


def verify_counts(driver):

    with driver.session() as session:

        node_count = session.run(
            """
            MATCH (u:User)
            RETURN count(u) AS count
            """
        ).single()["count"]

        relationship_count = session.run(
            """
            MATCH ()-[r:CONNECTS_TO]->()
            RETURN count(r) AS count
            """
        ).single()["count"]

    print()
    print("=" * 60)
    print("Neo4j Dataset Verification")
    print("=" * 60)

    print(
        f"Nodes         : "
        f"{node_count:,}"
    )

    print(
        f"Relationships : "
        f"{relationship_count:,}"
    )

    print("=" * 60)

    return (
        node_count,
        relationship_count,
    )


def main():

    print("=" * 60)
    print("Neo4j Dataset Loader")
    print("=" * 60)

    driver = create_driver()

    try:

        driver.verify_connectivity()

        print(
            "✓ Neo4j connection successful"
        )

        create_index(driver)

        node_count = load_nodes(driver)

        edge_count = load_edges(driver)

        actual_nodes, actual_edges = (
            verify_counts(driver)
        )

        print()
        print("=" * 60)
        print("LOAD SUMMARY")
        print("=" * 60)

        print(
            f"Nodes loaded        : "
            f"{node_count:,}"
        )

        print(
            f"Relationships loaded: "
            f"{edge_count:,}"
        )

        if actual_nodes == 398372:
            print(
                "✓ Node count verified"
            )
        else:
            print(
                "✗ Node count mismatch"
            )

        if actual_edges == 300000:
            print(
                "✓ Relationship count verified"
            )
        else:
            print(
                "✗ Relationship count mismatch"
            )

        print("=" * 60)

    finally:
        driver.close()


if __name__ == "__main__":
    main()