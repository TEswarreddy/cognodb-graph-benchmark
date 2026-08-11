import time

from neo4j import GraphDatabase


URI = "bolt://localhost:7688"


def main():

    driver = GraphDatabase.driver(
        URI,
        auth=None,
    )

    try:

        for attempt in range(10):

            try:

                driver.verify_connectivity()

                print("✓ Connected to Memgraph")

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
            "Unable to connect to Memgraph."
        )

    finally:
        driver.close()


if __name__ == "__main__":
    main()