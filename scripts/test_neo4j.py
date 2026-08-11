import time

from neo4j import GraphDatabase


URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "benchmark_password"


def main():

    driver = GraphDatabase.driver(
        URI,
        auth=(USERNAME, PASSWORD),
    )

    try:

        for attempt in range(10):

            try:

                driver.verify_connectivity()

                print("✓ Connected to Neo4j")

                with driver.session() as session:

                    result = session.run(
                        "RETURN 1 AS result"
                    )

                    value = result.single()["result"]

                    print(
                        f"Result: {value}"
                    )

                return

            except Exception as error:

                print(
                    f"Attempt {attempt + 1}/10 failed: "
                    f"{error}"
                )

                time.sleep(3)

        raise RuntimeError(
            "Unable to connect to Neo4j."
        )

    finally:
        driver.close()


if __name__ == "__main__":
    main()