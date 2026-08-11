import csv
import gzip
import random
from pathlib import Path


INPUT_FILE = Path(
    "datasets/raw/soc-pokec-relationships.txt.gz"
)

OUTPUT_DIR = Path("datasets/processed")

EDGES_OUTPUT = OUTPUT_DIR / "pokec_edges_300k.csv"
NODES_OUTPUT = OUTPUT_DIR / "pokec_nodes.csv"

SAMPLE_SIZE = 300_000
RANDOM_SEED = 42


def read_edges():
    """Read valid directed edges from the SNAP file."""

    edges = []

    with gzip.open(INPUT_FILE, "rt", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            # Skip comments and empty lines
            if not line or line.startswith("#"):
                continue

            parts = line.split()

            if len(parts) < 2:
                continue

            source = int(parts[0])
            target = int(parts[1])

            edges.append((source, target))

    return edges


def create_sample(edges):
    """Create a deterministic random sample."""

    if len(edges) < SAMPLE_SIZE:
        raise ValueError(
            f"Dataset contains only {len(edges)} edges, "
            f"but {SAMPLE_SIZE} are required."
        )

    random.seed(RANDOM_SEED)

    return random.sample(edges, SAMPLE_SIZE)


def save_edges(edges):
    """Save sampled edges to CSV."""

    with open(
        EDGES_OUTPUT,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.writer(file)

        writer.writerow(
            ["source_id", "target_id"]
        )

        writer.writerows(edges)


def save_nodes(edges):
    """Extract and save unique node IDs."""

    nodes = set()

    for source, target in edges:
        nodes.add(source)
        nodes.add(target)

    with open(
        NODES_OUTPUT,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.writer(file)

        writer.writerow(["node_id"])

        for node_id in sorted(nodes):
            writer.writerow([node_id])

    return nodes


def main():
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    print("Reading SNAP soc-Pokec dataset...")

    edges = read_edges()

    print(f"Original edges read: {len(edges):,}")

    print(
        f"Creating deterministic sample "
        f"of {SAMPLE_SIZE:,} edges..."
    )

    sampled_edges = create_sample(edges)

    save_edges(sampled_edges)

    nodes = save_nodes(sampled_edges)

    print()
    print("Sample creation completed!")
    print("--------------------------------")
    print(f"Original edges : {len(edges):,}")
    print(f"Sample edges   : {len(sampled_edges):,}")
    print(f"Sample nodes   : {len(nodes):,}")
    print(f"Random seed    : {RANDOM_SEED}")
    print()
    print(f"Edges file     : {EDGES_OUTPUT}")
    print(f"Nodes file     : {NODES_OUTPUT}")


if __name__ == "__main__":
    main()