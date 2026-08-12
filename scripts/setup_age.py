import psycopg


HOST = "localhost"
PORT = 5455
DATABASE = "graphdb"
USER = "postgres"
PASSWORD = "benchmark_password"


def main():

    print("=" * 60)
    print("Apache AGE Setup")
    print("=" * 60)

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

            # Verify/create AGE extension
            cursor.execute(
                "CREATE EXTENSION IF NOT EXISTS age"
            )

            print(
                "✓ AGE extension created/verified"
            )

            # Load AGE library
            cursor.execute(
                "LOAD 'age'"
            )

            print(
                "✓ AGE library loaded"
            )

            # Configure AGE search path
            cursor.execute(
                """
                SET search_path =
                    ag_catalog,
                    "$user",
                    public
                """
            )

            print(
                "✓ AGE search path configured"
            )

            # Verify AGE version
            cursor.execute(
                """
                SELECT extversion
                FROM pg_extension
                WHERE extname = 'age'
                """
            )

            row = cursor.fetchone()

            if row:
                print(
                    f"✓ AGE version: {row[0]}"
                )
            else:
                raise RuntimeError(
                    "AGE extension was not found."
                )

    finally:
        conn.close()

    print("=" * 60)
    print("✓ Apache AGE setup completed successfully")
    print("=" * 60)


if __name__ == "__main__":
    main()