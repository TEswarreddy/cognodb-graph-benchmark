import csv
from pathlib import Path


NODES_INPUT = Path(
    "datasets/processed/pokec_nodes.csv"
)

EDGES_INPUT = Path(
    "datasets/processed/pokec_edges_300k.csv"
)

OUTPUT_DIR = Path(
    "datasets/processed/age"
)

NODES_OUTPUT = OUTPUT_DIR / "users.csv"
EDGES_OUTPUT = OUTPUT_DIR / "connects_to.csv"


def prepare_nodes():
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    count = 0

    with open(
        NODES_INPUT,
        "r",
        encoding="utf-8",
        newline="",
    ) as source:

        reader = csv.DictReader(source)

        with open(
            NODES_OUTPUT,
            "w",
            encoding="utf-8",
            newline="",
        ) as target:

            writer = csv.writer(target)

            # AGE requires id as the first column.
            writer.writerow(["id"])

            for row in reader:
                writer.writerow([
                    row["node_id"]
                ])

                count += 1

    print(f"Nodes prepared: {count:,}")


def prepare_edges():
    count = 0

    with open(
        EDGES_INPUT,
        "r",
        encoding="utf-8",
        newline="",
    ) as source:

        reader = csv.DictReader(source)

        with open(
            EDGES_OUTPUT,
            "w",
            encoding="utf-8",
            newline="",
        ) as target:

            writer = csv.writer(target)

            # AGE edge CSV format:
            # start_id,start_vertex_type,end_id,end_vertex_type
            writer.writerow([
                "start_id",
                "start_vertex_type",
                "end_id",
                "end_vertex_type",
            ])

            for row in reader:
                writer.writerow([
                    row["source_id"],
                    "User",
                    row["target_id"],
                    "User",
                ])

                count += 1

    print(f"Edges prepared: {count:,}")


def main():
    print("=" * 60)
    print("Preparing Apache AGE CSV files")
    print("=" * 60)

    prepare_nodes()
    prepare_edges()

    print("=" * 60)
    print("Preparation complete")
    print("=" * 60)


if __name__ == "__main__":
    main()