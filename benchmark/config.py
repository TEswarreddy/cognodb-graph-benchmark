from dataclasses import dataclass


@dataclass(frozen=True)
class DatabaseConfig:
    name: str
    category: str
    query_language: str
    deployment: str


DATABASES = [
    DatabaseConfig(
        name="CognoDB",
        category="Graph Database",
        query_language="Cypher",
        deployment="Managed Cloud",
    ),
    DatabaseConfig(
        name="Neo4j",
        category="Graph Database",
        query_language="Cypher",
        deployment="Managed Cloud",
    ),
    DatabaseConfig(
        name="Memgraph",
        category="Graph Database",
        query_language="Cypher",
        deployment="Managed Cloud",
    ),
    DatabaseConfig(
        name="FalkorDB",
        category="Graph Database",
        query_language="Cypher",
        deployment="Managed Cloud",
    ),
    DatabaseConfig(
        name="Apache AGE",
        category="PostgreSQL Graph Extension",
        query_language="openCypher + SQL",
        deployment="Self-Hosted Docker",
    ),
]


COGNODB_RESOURCES = {
    "tier": "C0 Free",
    "vcpu": 0.5,
    "ram_mb": 256,
    "storage_gb": 1,
}