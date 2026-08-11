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
    )

    try:
        driver.verify_connectivity()

        with driver.session() as session:

            result = session.run(
                "SHOW INDEXES"
            )

            print("CognoDB indexes")
            print("=" * 60)

            for record in result:

                name = record.get("name")
                state = record.get("state")
                index_type = record.get("type")
                labels = record.get("labelsOrTypes")
                properties = record.get("properties")

                print(
                    f"Name       : {name}"
                )
                print(
                    f"State      : {state}"
                )
                print(
                    f"Type       : {index_type}"
                )
                print(
                    f"Labels     : {labels}"
                )
                print(
                    f"Properties : {properties}"
                )
                print("-" * 60)

    finally:
        driver.close()


if __name__ == "__main__":
    main()