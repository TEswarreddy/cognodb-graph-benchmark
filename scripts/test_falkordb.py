from falkordb import FalkorDB


HOST = "localhost"
PORT = 6379
GRAPH_NAME = "pokec"


def main():

    client = FalkorDB(
        host=HOST,
        port=PORT,
    )

    graph = client.select_graph(
        GRAPH_NAME
    )

    result = graph.query(
        "RETURN 1 AS result"
    )

    # FalkorDB returns a result object.
    # Convert the first record to verify connectivity.
    rows = result.result_set

    print("✓ Connected to FalkorDB")

    if rows:
        print(
            f"Result: {rows[0][0]}"
        )
    else:
        raise RuntimeError(
            "FalkorDB returned no result."
        )


if __name__ == "__main__":
    main()