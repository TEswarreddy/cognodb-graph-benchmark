TRAVERSAL_QUERIES = {
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


def get_traversal_query(depth):
    if depth not in TRAVERSAL_QUERIES:
        raise ValueError(
            f"Unsupported traversal depth: {depth}"
        )

    return TRAVERSAL_QUERIES[depth]