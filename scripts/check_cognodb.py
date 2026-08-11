import os

from dotenv import load_dotenv
from neo4j import GraphDatabase


load_dotenv()

URI = os.getenv("COGNODB_URI")
USERNAME = os.getenv("COGNODB_USERNAME")
PASSWORD = os.getenv("COGNODB_PASSWORD")


def main():
    driver = GraphDatabase.driver(
        URI,
        auth=(USERNAME, PASSWORD),
        connection_timeout=30,
        max_connection_lifetime=300,
    )

    try:
        driver.verify_connectivity()
        print("✓ Connected to CognoDB")

        with driver.session() as session:
            node_count = session.run(
                """
                MATCH (u:User)
                RETURN count(u) AS count
                """
            ).single()["count"]

            edge_count = session.run(
                """
                MATCH ()-[r:CONNECTS_TO]->()
                RETURN count(r) AS count
                """
            ).single()["count"]

        print(f"Nodes         : {node_count:,}")
        print(f"Relationships : {edge_count:,}")

    finally:
        driver.close()


if __name__ == "__main__":
    main()