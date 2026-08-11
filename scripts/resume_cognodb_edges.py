import csv
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, SessionExpired


load_dotenv()


URI = os.getenv("COGNODB_URI")
USERNAME = os.getenv("COGNODB_USERNAME")
PASSWORD = os.getenv("COGNODB_PASSWORD")

EDGES_FILE = Path(
    "datasets/processed/pokec_edges_300k.csv"
)

BATCH_SIZE = 500
EXPECTED_EDGES = 300_000

MAX_RETRIES = 5


def create_driver():
    return GraphDatabase.driver(
        URI,
        auth=(USERNAME, PASSWORD),
        connection_timeout=30,
        max_connection_lifetime=300,
        max_connection_pool_size=5,
    )


def get_edge_count(driver):
    with driver.session() as session:
        result = session.run(
            """
            MATCH ()-[r:CONNECTS_TO]->()
            RETURN count(r) AS count
            """
        )
        return result.single()["count"]


def load_batch(driver, batch):
    query = """
    UNWIND $edges AS edge

    MATCH (source:User {id: edge.source})
    MATCH (target:User {id: edge.target})

    CREATE (source)-[:CONNECTS_TO]->(target)
    """

    for attempt in range(1, MAX_RETRIES + 1):

        try:
            with driver.session() as session:
                session.run(
                    query,
                    edges=batch,
                ).consume()

            return True

        except (
            ServiceUnavailable,
            SessionExpired,
            OSError,
        ) as error:

            print()
            print(
                f"Connection error on attempt "
                f"{attempt}/{MAX_RETRIES}: {error}"
            )

            if attempt == MAX_RETRIES:
                raise

            time.sleep(3)

            print("Reconnecting...")

    return False


def main():

    print("=" * 60)
    print("CognoDB Relationship Resume Loader")
    print("=" * 60)

    driver = create_driver()

    try:

        driver.verify_connectivity()

        print("✓ CognoDB connection successful")

        current_count = get_edge_count(driver)

        print(
            f"Current relationships : "
            f"{current_count:,}"
        )

        if current_count >= EXPECTED_EDGES:
            print()
            print(
                "✓ All relationships are already loaded."
            )
            return

        if current_count > EXPECTED_EDGES:
            raise RuntimeError(
                f"Database contains {current_count:,} "
                f"relationships, which exceeds the "
                f"expected {EXPECTED_EDGES:,}."
            )

        remaining = EXPECTED_EDGES - current_count

        print(
            f"Relationships remaining: "
            f"{remaining:,}"
        )

        print()
        print(
            f"Reading dataset and skipping "
            f"first {current_count:,} rows..."
        )

        start_time = time.perf_counter()

        skipped = 0
        loaded = 0
        batch = []

        with open(
            EDGES_FILE,
            "r",
            encoding="utf-8",
        ) as file:

            reader = csv.DictReader(file)

            for row in reader:

                # Skip already committed relationships
                if skipped < current_count:
                    skipped += 1
                    continue

                # Stop after expected dataset size
                if loaded >= remaining:
                    break

                batch.append(
                    {
                        "source": int(row["source_id"]),
                        "target": int(row["target_id"]),
                    }
                )

                if len(batch) >= BATCH_SIZE:

                    load_batch(
                        driver,
                        batch,
                    )

                    loaded += len(batch)

                    print(
                        f"New relationships loaded: "
                        f"{loaded:,}/{remaining:,}",
                        end="\r",
                    )

                    batch = []

            # Remaining partial batch
            if batch:
                load_batch(
                    driver,
                    batch,
                )

                loaded += len(batch)

        elapsed = time.perf_counter() - start_time

        print()
        print()

        final_count = get_edge_count(driver)

        print("=" * 60)
        print("RESUME SUMMARY")
        print("=" * 60)

        print(
            f"Previously loaded : {current_count:,}"
        )

        print(
            f"Newly loaded      : {loaded:,}"
        )

        print(
            f"Final relationships: {final_count:,}"
        )

        print(
            f"Elapsed time      : {elapsed:.3f} sec"
        )

        if loaded > 0:
            print(
                f"Relationships/sec : "
                f"{loaded / elapsed:,.2f}"
            )

        print("=" * 60)

        if final_count == EXPECTED_EDGES:
            print(
                "✓ All 300,000 relationships are loaded."
            )
        else:
            print(
                "⚠ Relationship count does not match "
                "the expected value."
            )

    finally:
        driver.close()


if __name__ == "__main__":
    main()
    