import os

from dotenv import load_dotenv
from neo4j import GraphDatabase


load_dotenv()

uri = os.getenv("COGNODB_URI")
username = os.getenv("COGNODB_USERNAME")
password = os.getenv("COGNODB_PASSWORD")


if not uri or not username or not password:
    raise ValueError("CognoDB credentials are missing from .env")


driver = GraphDatabase.driver(
    uri,
    auth=(username, password)
)


try:
    with driver.session() as session:
        result = session.run("RETURN 1 AS result")
        record = result.single()

        print("Connection successful!")
        print("Result:", record["result"])

finally:
    driver.close()