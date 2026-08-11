AGGREGATION_QUERY = """
    MATCH (u:User)-[:CONNECTS_TO]->()
    RETURN u.id AS node_id,
           count(*) AS connection_count
    ORDER BY connection_count DESC
    LIMIT 100
"""


def get_aggregation_query():
    return AGGREGATION_QUERY