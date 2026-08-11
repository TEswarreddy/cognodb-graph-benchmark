import csv
from pathlib import Path


EDGES_FILE = Path(
    "datasets/processed/pokec_edges_300k.csv"
)

NODES_FILE = Path(
    "datasets/processed/pokec_nodes.csv"
)


def count_csv_rows(path):
    with open(path, "r", encoding="utf-8") as file:
        return sum(1 for _ in file) - 1


def main():
    edge_count = count_csv_rows(EDGES_FILE)
    node_count = count_csv_rows(NODES_FILE)

    print("Dataset verification")
    print("====================")
    print(f"Relationships : {edge_count:,}")
    print(f"Nodes         : {node_count:,}")

    if edge_count != 300_000:
        raise ValueError(
            f"Expected 300,000 relationships, "
            f"found {edge_count:,}"
        )

    if node_count != 398_372:
        raise ValueError(
            f"Expected 398,372 nodes, "
            f"found {node_count:,}"
        )

    # Verify CSV headers
    with open(EDGES_FILE, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        header = next(reader)

    if header != ["source_id", "target_id"]:
        raise ValueError(
            f"Unexpected edge header: {header}"
        )

    with open(NODES_FILE, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        header = next(reader)

    if header != ["node_id"]:
        raise ValueError(
            f"Unexpected node header: {header}"
        )

    print()
    print("✓ Relationship count verified")
    print("✓ Node count verified")
    print("✓ CSV headers verified")
    print("✓ Dataset is ready for benchmarking")


if __name__ == "__main__":
    main()