import psycopg


HOST = "localhost"
PORT = 5455
DATABASE = "graphdb"
USER = "postgres"
PASSWORD = "benchmark_password"


conn = psycopg.connect(
    host=HOST,
    port=PORT,
    dbname=DATABASE,
    user=USER,
    password=PASSWORD,
)

conn.autocommit = True

try:
    with conn.cursor() as cursor:

        cursor.execute("LOAD 'age'")

        cursor.execute(
            """
            SELECT ag_catalog.create_graph('pokec')
            """
        )

        print("✓ pokec graph created")

finally:
    conn.close()