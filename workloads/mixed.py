MIXED_READ_WRITE_QUERY = """
    MATCH (source:User {id: $source_id})
    MATCH (target:User {id: $target_id})

    CREATE (source)-[r:TEMP_CONNECTS_TO]->(target)

    DELETE r

    RETURN source.id AS source_id,
           target.id AS target_id
"""


def get_mixed_read_write_query():
    return MIXED_READ_WRITE_QUERY