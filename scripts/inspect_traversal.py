import csv
import os
import random

from dotenv import load_dotenv
from neo4j import GraphDatabase


load_dotenv()

URI = os.getenv("COGNODB_URI")
USERNAME = os.getenv("COGNODB_USERNAME")
PASSWORD = os.getenv("COGNODB_PASSWORD")

NODES_FILE = "datasets/processed/pokec_nodes.csv"

RANDOM_SEED = 42
SAMPLE_SIZE = 100


QUERIES = {
    1: """
        MATCH (start:User {id: $start_id})
              -[:CONNECTS_TO]->
              (node)
        RETURN count(node) AS result
    """,

    2: """
        MATCH (start:User {id: $start_id})
              -[:CONNECTS_TO]->
              ()
              -[:CONNECTS_TO]->
              (node)
        RETURN count(node) AS result
    """,

    3: """
        MATCH (start:User {id: $start_id})
              -[:CONNECTS_TO]->
              ()
              -[:CONNECTS_TO]->
              ()
              -[:CONNECTS_TO]->
              (node)
        RETURN count(node) AS result
    """,
}


def load_node_ids():
    node_ids = []

    with open(
        NODES_FILE,
        "r",
        encoding="utf-8",
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:
            node_ids.append(int(row["node_id"]))

    return node_ids


def main():

    node_ids = load_node_ids()

    random.seed(RANDOM_SEED)

    start_nodes = random.sample(
        node_ids,
        SAMPLE_SIZE,
    )

    driver = GraphDatabase.driver(
        URI,
        auth=(USERNAME, PASSWORD),
    )

    try:

        driver.verify_connectivity()

        print("=" * 60)
        print("Traversal Diagnostic")
        print("=" * 60)

        with driver.session() as session:

            for depth, query in QUERIES.items():

                results = []

                for start_id in start_nodes:

                    record = session.run(
                        query,
                        start_id=start_id,
                    ).single()

                    results.append(
                        record["result"]
                    )

                nonzero = sum(
                    1
                    for value in results
                    if value > 0
                )

                zero = sum(
                    1
                    for value in results
                    if value == 0
                )

                print()
                print(f"{depth}-hop traversal")
                print("-" * 30)

                print(
                    f"Zero-result starts : {zero}"
                )

                print(
                    f"Non-zero starts   : {nonzero}"
                )

                print(
                    f"Minimum results   : {min(results)}"
                )

                print(
                    f"Maximum results   : {max(results)}"
                )

                print(
                    f"Average results   : "
                    f"{sum(results) / len(results):.2f}"
                )

    finally:
        driver.close()


if __name__ == "__main__":
    main()