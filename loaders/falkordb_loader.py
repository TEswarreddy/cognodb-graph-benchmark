import csv
import time
from pathlib import Path

from falkordb import FalkorDB


HOST = "localhost"
PORT = 6379

GRAPH_NAME = "pokec"

NODES_FILE = Path(
    "datasets/processed/pokec_nodes.csv"
)

EDGES_FILE = Path(
    "datasets/processed/pokec_edges_300k.csv"
)

BATCH_SIZE = 5000


def create_graph():

    client = FalkorDB(
        host=HOST,
        port=PORT,
    )

    return client.select_graph(
        GRAPH_NAME
    )


def create_index(graph):

    print("Creating index on User.id...")

    try:

        graph.query(
            "CREATE INDEX FOR (u:User) ON (u.id)"
        )

    except Exception as error:

        # The index may already exist.
        if "already indexed" not in str(
            error
        ).lower():

            raise

    print("Index created/verified.")


def load_nodes(graph):

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
                int(row["node_id"])
            )

            if len(nodes) >= BATCH_SIZE:

                query = """
                UNWIND $nodes AS node_id
                CREATE (:User {id: node_id})
                """

                graph.query(
                    query,
                    params={
                        "nodes": nodes
                    },
                )

                total_loaded += len(nodes)

                print(
                    f"Nodes loaded: "
                    f"{total_loaded:,}",
                    end="\r",
                )

                nodes = []

        if nodes:

            graph.query(
                """
                UNWIND $nodes AS node_id
                CREATE (:User {id: node_id})
                """,
                params={
                    "nodes": nodes
                },
            )

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


def load_edges(graph):

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

                graph.query(
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
                    params={
                        "edges": edges
                    },
                )

                total_loaded += len(edges)

                print(
                    f"Relationships loaded: "
                    f"{total_loaded:,}",
                    end="\r",
                )

                edges = []

        if edges:

            graph.query(
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
                params={
                    "edges": edges
                },
            )

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


def verify_counts(graph):

    node_result = graph.query(
        """
        MATCH (u:User)
        RETURN count(u)
        """
    )

    relationship_result = graph.query(
        """
        MATCH ()-[r:CONNECTS_TO]->()
        RETURN count(r)
        """
    )

    node_count = (
        node_result.result_set[0][0]
    )

    relationship_count = (
        relationship_result.result_set[0][0]
    )

    print()
    print("=" * 60)
    print("FalkorDB Dataset Verification")
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
    print("FalkorDB Dataset Loader")
    print("=" * 60)

    graph = create_graph()

    print(
        "✓ FalkorDB connection successful"
    )

    create_index(graph)

    node_count = load_nodes(graph)

    edge_count = load_edges(graph)

    actual_nodes, actual_edges = (
        verify_counts(graph)
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


if __name__ == "__main__":
    main()