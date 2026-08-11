from falkordb import FalkorDB


HOST = "localhost"
PORT = 6379
GRAPH_NAME = "pokec"


def main():

    client = FalkorDB(
        host=HOST,
        port=PORT,
    )

    graph = client.select_graph(
        GRAPH_NAME
    )

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

    print("✓ Connected to FalkorDB")

    print()
    print("=" * 60)
    print("FalkorDB Graph Verification")
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

    if node_count != 398372:
        raise RuntimeError(
            f"Expected 398,372 nodes, "
            f"found {node_count:,}"
        )

    if relationship_count != 300000:
        raise RuntimeError(
            f"Expected 300,000 relationships, "
            f"found {relationship_count:,}"
        )

    print("✓ Node count verified")
    print("✓ Relationship count verified")
    print(
        "✓ Relationship count verified"
    )
    print(
        "✓ FalkorDB is ready for benchmarking"
    )


if __name__ == "__main__":
    main()