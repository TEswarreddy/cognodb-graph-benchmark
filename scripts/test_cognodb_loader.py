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
        auth=(USERNAME, PASSWORD)
    )

    try:
        driver.verify_connectivity()

        print("✓ Connected to CognoDB")

        with driver.session() as session:

            # Create a tiny test graph
            session.run(
                """
                CREATE (a:User {id: -1})
                CREATE (b:User {id: -2})
                CREATE (a)-[:CONNECTS_TO]->(b)
                """
            ).consume()

            result = session.run(
                """
                MATCH (a:User {id: -1})
                      -[:CONNECTS_TO]->
                      (b:User {id: -2})
                RETURN a.id AS source,
                       b.id AS target
                """
            )

            record = result.single()

            if record:
                print(
                    f"✓ Test relationship verified: "
                    f"{record['source']} -> "
                    f"{record['target']}"
                )

    finally:

        # Remove only our test nodes
        with driver.session() as session:
            session.run(
                """
                MATCH (u:User)
                WHERE u.id IN [-1, -2]
                DETACH DELETE u
                """
            ).consume()

        driver.close()

        print("✓ Test data removed")


if __name__ == "__main__":
    main()