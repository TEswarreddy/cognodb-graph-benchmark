from neo4j import GraphDatabase


URI = "bolt://localhost:7688"


def main():

    driver = GraphDatabase.driver(
        URI,
        auth=None,
    )

    try:

        driver.verify_connectivity()

        print("✓ Connected to Memgraph")

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

            indexes = list(
                session.run(
                    """
                    SHOW INDEX INFO
                    """
                )
            )

        print()
        print("=" * 60)
        print("Memgraph Verification")
        print("=" * 60)

        print(
            f"Nodes         : {node_count:,}"
        )

        print(
            f"Relationships : "
            f"{relationship_count:,}"
        )

        print()
        print("Indexes:")

        for index in indexes:
            print(dict(index))

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
        print("✓ Memgraph is ready for benchmarking")

    finally:
        driver.close()


if __name__ == "__main__":
    main()