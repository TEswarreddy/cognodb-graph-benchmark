POINT_LOOKUP_QUERY = """
    MATCH (u:User {id: $node_id})
    RETURN u.id AS id
"""


def get_point_lookup_query():
    return POINT_LOOKUP_QUERY