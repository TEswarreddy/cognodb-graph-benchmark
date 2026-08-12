import psycopg


conn = psycopg.connect(
    host="localhost",
    port=5455,
    dbname="graphdb",
    user="postgres",
    password="benchmark_password",
)

conn.autocommit = True

try:
    with conn.cursor() as cursor:

        cursor.execute("LOAD 'age'")

        cursor.execute(
            """
            SET search_path =
                ag_catalog,
                "$user",
                public
            """
        )

        cursor.execute(
            """
            SELECT *
            FROM cypher(
                'pokec',
                $$
                MATCH (n:User)
                RETURN count(n)
                $$
            ) AS (count agtype)
            """
        )

        node_count = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT *
            FROM cypher(
                'pokec',
                $$
                MATCH ()-[r:CONNECTS_TO]->()
                RETURN count(r)
                $$
            ) AS (count agtype)
            """
        )

        relationship_count = cursor.fetchone()[0]

        print("=" * 60)
        print("Apache AGE Graph Status")
        print("=" * 60)
        print(f"Nodes         : {node_count}")
        print(f"Relationships : {relationship_count}")
        print("=" * 60)

finally:
    conn.close()