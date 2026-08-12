import psycopg


HOST = "localhost"
PORT = 5455
DATABASE = "graphdb"
USER = "postgres"
PASSWORD = "benchmark_password"


def main():

    conn = psycopg.connect(
        host=HOST,
        port=PORT,
        dbname=DATABASE,
        user=USER,
        password=PASSWORD,
    )

    try:

        with conn.cursor() as cursor:

            cursor.execute(
                "SELECT 1"
            )

            result = cursor.fetchone()[0]

        print(
            "✓ Connected to Apache AGE PostgreSQL"
        )

        print(
            f"Result: {result}"
        )

    finally:

        conn.close()


if __name__ == "__main__":
    main()