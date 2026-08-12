import psycopg


HOST = "localhost"
PORT = 5455
DATABASE = "graphdb"
USER = "postgres"
PASSWORD = "benchmark_password"

GRAPH_NAME = "pokec_test"


def main():

    conn = psycopg.connect(
        host=HOST,
        port=PORT,
        dbname=DATABASE,
        user=USER,
        password=PASSWORD,
    )

    try:

        conn.autocommit = True

        with conn.cursor() as cursor:

            cursor.execute(
                "LOAD 'age'"
            )

            cursor.execute(
                """
                SET search_path =
                    ag_catalog,
                    "$user",
                    public
                """
            )

            # Create test graph if it does not exist
            cursor.execute(
                """
                SELECT 1
                FROM ag_catalog.ag_graph
                WHERE name = %s
                """,
                (GRAPH_NAME,),
            )

            if not cursor.fetchone():

                cursor.execute(
                    f"""
                    SELECT create_graph('{GRAPH_NAME}')
                    """
                )

                print(
                    f"✓ Created test graph: {GRAPH_NAME}"
                )

            else:

                print(
                    f"✓ Test graph already exists: "
                    f"{GRAPH_NAME}"
                )

            # AGE requires the graph name to be a
            # literal name in cypher(), not a
            # PostgreSQL parameter.
            cursor.execute(
                f"""
                SELECT *
                FROM cypher(
                    '{GRAPH_NAME}',
                    $$
                    CREATE (:User {{id: 999999999}})
                    $$
                ) AS (
                    result agtype
                )
                """
            )

        print(
            "✓ AGE graph operation successful"
        )

    finally:

        conn.close()


if __name__ == "__main__":
    main()