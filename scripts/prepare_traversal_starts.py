import csv
import random
from collections import defaultdict
from pathlib import Path


EDGES_FILE = Path(
    "datasets/processed/pokec_edges_300k.csv"
)

OUTPUT_DIR = Path(
    "datasets/processed"
)

RANDOM_SEED = 42
SAMPLE_SIZE = 100


def load_graph():
    """
    Load the benchmark graph from the fixed CSV dataset.

    The dataset contains directed edges:
        source_id -> target_id
    """

    adjacency = defaultdict(set)

    with open(
        EDGES_FILE,
        "r",
        encoding="utf-8",
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            source = int(row["source_id"])
            target = int(row["target_id"])

            adjacency[source].add(target)

    return adjacency


def has_path_of_length(adjacency, start, depth):
    """
    Determine whether at least one path of the requested
    length exists from the start node.

    Example:

    depth=1:
        A -> B

    depth=2:
        A -> B -> C

    depth=3:
        A -> B -> C -> D
    """

    current = {start}

    for _ in range(depth):

        next_nodes = set()

        for node in current:
            next_nodes.update(
                adjacency.get(node, ())
            )

        if not next_nodes:
            return False

        current = next_nodes

    return True


def find_eligible_nodes(adjacency, depth):
    """
    Find nodes with at least one reachable path
    of the requested depth.
    """

    eligible = []

    for start in adjacency:

        if has_path_of_length(
            adjacency,
            start,
            depth,
        ):
            eligible.append(start)

    return eligible


def save_nodes(depth, nodes):

    output_file = (
        OUTPUT_DIR
        / f"traversal_starts_{depth}hop.csv"
    )

    with open(
        output_file,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.writer(file)

        writer.writerow(["node_id"])

        for node_id in nodes:
            writer.writerow([node_id])

    return output_file


def main():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("=" * 60)
    print("Preparing traversal start-node pools")
    print("=" * 60)

    print()
    print("Loading benchmark graph from CSV...")

    adjacency = load_graph()

    print(
        f"Nodes with outgoing edges: "
        f"{len(adjacency):,}"
    )

    random.seed(RANDOM_SEED)

    for depth in [1, 2, 3]:

        print()
        print(
            f"Finding eligible {depth}-hop "
            f"start nodes locally..."
        )

        eligible_nodes = find_eligible_nodes(
            adjacency,
            depth,
        )

        print(
            f"Eligible nodes: "
            f"{len(eligible_nodes):,}"
        )

        if len(eligible_nodes) < SAMPLE_SIZE:

            raise ValueError(
                f"Only {len(eligible_nodes)} "
                f"eligible nodes found for "
                f"{depth}-hop traversal."
            )

        selected_nodes = random.sample(
            eligible_nodes,
            SAMPLE_SIZE,
        )

        selected_nodes.sort()

        output_file = save_nodes(
            depth,
            selected_nodes,
        )

        print(
            f"Selected nodes: "
            f"{len(selected_nodes):,}"
        )

        print(
            f"Saved to: "
            f"{output_file}"
        )

    print()
    print("=" * 60)
    print("Traversal start-node preparation complete")
    print("=" * 60)


if __name__ == "__main__":
    main()