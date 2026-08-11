import os

from dotenv import load_dotenv
from neo4j import GraphDatabase


load_dotenv()


URI = os.getenv("COGNODB_URI")
USERNAME = os.getenv("COGNODB_USERNAME")
PASSWORD = os.getenv("COGNODB_PASSWORD")


EXPECTED_NODES = 398_372
EXPECTED_RELATIONSHIPS = 300_000


def main():

    driver = GraphDatabase.driver(
        URI,
        auth=(USERNAME, PASSWORD),
        connection_timeout=30,
    )

    try:
        driver.verify_connectivity()

        print("✓ Connected to CognoDB")
        print()

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

            distinct_source_count = session.run(
                """
                MATCH (u:User)-[:CONNECTS_TO]->()
                RETURN count(DISTINCT u) AS count
                """
            ).single()["count"]

            distinct_target_count = session.run(
                """
                MATCH ()-[:CONNECTS_TO]->(u:User)
                RETURN count(DISTINCT u) AS count
                """
            ).single()["count"]

        print("=" * 60)
        print("CognoDB Graph Verification")
        print("=" * 60)

        print(
            f"Nodes                 : {node_count:,}"
        )

        print(
            f"Relationships         : "
            f"{relationship_count:,}"
        )

        print(
            f"Distinct source nodes : "
            f"{distinct_source_count:,}"
        )

        print(
            f"Distinct target nodes : "
            f"{distinct_target_count:,}"
        )

        print("=" * 60)

        if node_count != EXPECTED_NODES:
            raise AssertionError(
                f"Expected {EXPECTED_NODES:,} nodes, "
                f"found {node_count:,}"
            )

        if relationship_count != EXPECTED_RELATIONSHIPS:
            raise AssertionError(
                f"Expected {EXPECTED_RELATIONSHIPS:,} "
                f"relationships, found "
                f"{relationship_count:,}"
            )

        print("✓ Node count is correct")
        print("✓ Relationship count is correct")
        print("✓ Graph is ready for benchmarking")

    finally:
        driver.close()


if __name__ == "__main__":
    main()