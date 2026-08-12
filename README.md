# Graph Database Benchmarking

A performance benchmarking project comparing **Neo4j, Memgraph, FalkorDB, and Apache AGE** using the same graph dataset and standardized workloads.

The benchmark evaluates graph databases across traversal, point lookup, aggregation, and mixed read/write workloads using latency metrics such as **p50, p95, mean, minimum, and maximum latency**.

---

## 1. Project Overview

The objective of this project is to evaluate and compare the performance of different graph database technologies under identical workloads.

The databases evaluated are:

- **Neo4j 5.26 Community**
- **Memgraph**
- **FalkorDB**
- **Apache AGE 1.7.0**

The benchmark uses a common graph dataset containing:

- **398,372 nodes**
- **300,000 relationships**

Each database is loaded with the same logical dataset and tested using the same benchmark methodology.

### Main objectives

The benchmark evaluates:

1. 1-hop graph traversal
2. 2-hop graph traversal
3. 3-hop graph traversal
4. Point lookup
5. Aggregation
6. Mixed read/write operations

The goal is not to identify one universally best database, but to determine how each database performs under different workload types.

---

## 2. Technologies Used

| Component | Technology |
|---|---|
| Programming Language | Python 3.12 |
| Containerization | Docker / Docker Compose |
| Neo4j | 5.26 Community |
| Memgraph | Latest |
| FalkorDB | Latest |
| Apache AGE | 1.7.0 |
| PostgreSQL | 18.1 |
| Benchmark iterations | 100 |
| Warm-up iterations | 20 |
| Dataset | Pokec-derived graph |
| Operating System | Windows |
| Shell | PowerShell |

---

## 3. Project Structure

The project follows a structure similar to:

```
cognodb-graph-benchmark/
│
├── benchmark/
│   └── statistics.py
│
├── databases/
│   ├── neo4j/
│   │   └── docker-compose.yml
│   │
│   ├── memgraph/
│   │   └── docker-compose.yml
│   │
│   ├── falkordb/
│   │   └── docker-compose.yml
│   │
│   └── age/
│       └── docker-compose.yml
│
├── datasets/
│   └── processed/
│       ├── pokec_nodes.csv
│       ├── pokec_edges_300k.csv
│       └── age/
│           ├── users.csv
│           └── connects_to.csv
│
├── loaders/
│   ├── ...
│   └── age_relationship_loader.py
│
├── scripts/
│   ├── check_*.py
│   ├── setup_age.py
│   ├── benchmark_*.py
│   └── ...
│
├── workloads/
│   ├── traversal.py
│   ├── lookup.py
│   ├── aggregation.py
│   └── ...
│
├── results/
│   └── benchmark_results.csv
│
└── README.md
```

---

## 4. Dataset

The benchmark uses a processed graph dataset based on the Pokec social-network dataset.

The final benchmark dataset contains:

```
Nodes         : 398,372
Relationships : 300,000
```

The node CSV contains:

```
node_id
7
10
13
...
```

The relationship CSV contains:

```
source_id,target_id
612820,290349
81414,372823
16381,290855
...
```

The graph model uses:

```
(:User)-[:CONNECTS_TO]->(:User)
```

Therefore, a typical graph relationship is:

```
User ──CONNECTS_TO──> User
```

---

## 5. Dataset Verification

Before benchmarking each database, the node and relationship counts were verified.

Expected dataset:

```
Nodes         : 398,372
Relationships : 300,000
```

Apache AGE verification:

```
============================================================
Apache AGE Graph Status
============================================================
Nodes         : 398372
Relationships : 300000
============================================================
```

The same logical dataset was loaded into the other databases.

---

## 6. Benchmark Methodology

Every workload follows the same general benchmark methodology.

### Warm-up

Before measurements, the benchmark executes:

```
20 warm-up iterations
```

Warm-up iterations help reduce the effect of initial startup, query compilation, connection initialization, and cold-cache effects.

### Measurement

After warm-up:

```
100 measured iterations
```

are executed.

### Metrics

The following metrics are collected:

**p50** — The median latency. 50% of measured operations completed within this time.

**p95** — The latency below which approximately 95% of operations completed. This is useful for evaluating tail latency.

**Mean** — Average latency across all measured operations.

**Minimum** — Fastest observed execution.

**Maximum** — Slowest observed execution.

All latency measurements are reported in:

```
milliseconds (ms)
```

### Performance interpretation

For all latency metrics:

> **Lower is better.**

---

## 7. Workloads

### 7.1 1-Hop Traversal

Measures the time required to traverse one relationship from a starting node.

Conceptually:

```
MATCH (u:User)-[:CONNECTS_TO]->(v)
RETURN v
```

This evaluates basic graph traversal performance.

### 7.2 2-Hop Traversal

Measures traversal across two relationships.

Conceptually:

```
MATCH (u:User)-[:CONNECTS_TO]->()-[:CONNECTS_TO]->(v)
RETURN v
```

This evaluates slightly deeper graph navigation.

### 7.3 3-Hop Traversal

Measures traversal across three relationships.

Conceptually:

```
MATCH (u:User)
      -[:CONNECTS_TO]->
      ()
      -[:CONNECTS_TO]->
      ()
      -[:CONNECTS_TO]->
      (v)
RETURN v
```

This evaluates deeper multi-hop graph traversal.

### 7.4 Point Lookup

Point lookup retrieves a specific user/node.

Conceptually:

```
MATCH (u:User)
WHERE u.id = <node_id>
RETURN u
```

The benchmark uses a pool of selected nodes and repeatedly performs lookups.

### 7.5 Aggregation

The aggregation workload calculates the number of outgoing relationships for users and returns the top 100 users.

Query:

```
MATCH (u:User)-[:CONNECTS_TO]->()
RETURN u.id AS node_id,
       count(*) AS connection_count
ORDER BY connection_count DESC
LIMIT 100
```

This workload evaluates:

- Relationship counting
- Grouping
- Sorting
- Aggregation
- Query execution over a larger portion of the graph

### 7.6 Mixed Read/Write

The mixed workload performs a read followed by a write operation.

Conceptually:

```
READ User
     ↓
WRITE User
```

For Apache AGE, a temporary benchmark property was used:

```
benchmark_value
```

The property was removed after the benchmark.

This workload evaluates performance under a combination of read and write operations.

---

## 8. Database Setup

### 8.1 Neo4j

Neo4j was run using Docker.

Check the running container:

```
docker ps
```

Expected container:

```
graph-benchmark-neo4j
```

Neo4j ports:

```
7474 → Neo4j Browser
7687 → Bolt
```

---

## 9. Memgraph Setup

Memgraph was run using Docker.

Expected container:

```
graph-benchmark-memgraph
```

Ports:

```
3000 → Memgraph Lab
7688 → Bolt
```

Verify:

```
docker ps
```

The database was verified before benchmarking:

```
✓ Connected to Memgraph

Nodes         : 398,372
Relationships : 300,000

✓ Node count verified
✓ Relationship count verified
✓ Memgraph is ready for benchmarking
```

---

## 10. FalkorDB Setup

FalkorDB was deployed using Docker Compose.

Start:

```
docker compose -f databases/falkordb/docker-compose.yml up -d
```

Check:

```
docker ps
```

Expected container:

```
graph-benchmark-falkordb
```

FalkorDB Python client:

```
python -m pip install falkordb
```

Test connection:

```
python scripts/test_falkordb.py
```

Expected:

```
✓ Connected to FalkorDB
Result: 1
```

Dataset verification:

```
python scripts/check_falkordb.py
```

Expected:

```
✓ Connected to FalkorDB

============================================================
FalkorDB Graph Verification
============================================================
Nodes         : 398,372
Relationships : 300,000
============================================================
✓ Node count verified
✓ Relationship count verified
✓ FalkorDB is ready for benchmarking
```

---

## 11. Apache AGE Setup

Apache AGE runs as a PostgreSQL extension.

Docker Compose:

```
docker compose -f databases/age/docker-compose.yml up -d
```

The AGE container exposes PostgreSQL on:

```
localhost:5455
```

Connection configuration:

```
Host     : localhost
Port     : 5455
Database : graphdb
User     : postgres
Password : benchmark_password
```

Install Python PostgreSQL driver:

```
python -m pip install "psycopg[binary]"
```

Test:

```
python scripts/test_age.py
```

Expected:

```
✓ Connected to Apache AGE PostgreSQL
Result: 1
```

---

## 12. Apache AGE Extension Setup

Run:

```
python scripts/setup_age.py
```

Expected:

```
============================================================
Apache AGE Setup
============================================================
✓ AGE extension created/verified
✓ AGE library loaded
✓ AGE search path configured
✓ AGE version: 1.7.0
============================================================
```

The installed AGE version was:

```
1.7.0
```

---

## 13. Apache AGE Graph

The benchmark graph is:

```
pokec
```

The graph was created using:

```
SELECT ag_catalog.create_graph('pokec');
```

The AGE graph was verified with:

```
SELECT name FROM ag_catalog.ag_graph;
```

The graph list included:

```
pokec
```

---

## 14. Apache AGE Data Loading

AGE requires graph-compatible CSV files.

The CSV preparation script:

```
python scripts/prepare_age_csv.py
```

produces:

```
datasets\processed\age\users.csv
datasets\processed\age\connects_to.csv
```

The files were copied into the container:

```
docker exec graph-benchmark-age mkdir -p /tmp/age_data
docker cp datasets\processed\age\users.csv graph-benchmark-age:/tmp/age_data/users.csv
docker cp datasets\processed\age\connects_to.csv graph-benchmark-age:/tmp/age_data/connects_to.csv
```

AGE supports:

```
ag_catalog.load_labels_from_file
ag_catalog.load_edges_from_file
```

The final graph was verified:

```
Nodes         : 398372
Relationships : 300000
```

---

## 15. Running the Benchmarks — Memgraph

### Traversal

```
python -m scripts.benchmark_memgraph_traversal
```

### Point lookup

```
python -m scripts.benchmark_memgraph_lookup
```

### Aggregation

```
python -m scripts.benchmark_memgraph_aggregation
```

### Mixed

```
python -m scripts.benchmark_memgraph_mixed
```

---

## 16. FalkorDB Benchmarks

### Traversal

```
python -m scripts.benchmark_falkordb_traversal
```

### Point lookup

```
python -m scripts.benchmark_falkordb_lookup
```

### Aggregation

```
python -m scripts.benchmark_falkordb_aggregation
```

### Mixed

```
python -m scripts.benchmark_falkordb_mixed
```

---

## 17. Apache AGE Benchmarks

### Traversal

```
python -m scripts.benchmark_age_traversal
```

### Point lookup

```
python -m scripts.benchmark_age_lookup
```

### Aggregation

```
python -m scripts.benchmark_age_aggregation
```

### Mixed

```
python -m scripts.benchmark_age_mixed
```

---

## 18. Final Benchmark Results

### 18.1 Complete p50 Results (ms)

Lower is better.

| Workload | Neo4j | Memgraph | FalkorDB | Apache AGE |
|---|---|---|---|---|
| 1-hop traversal | 14.298 | 2.209 | **2.087** | 126.919 |
| 2-hop traversal | 7.723 | 2.138 | **2.003** | 128.994 |
| 3-hop traversal | 5.452 | 2.159 | **2.102** | 131.247 |
| Point lookup | 5.855 | 2.206 | **1.999** | 172.436 |
| Aggregation | **414.571** | 790.678 | 841.798 | 1392.303 |
| Mixed read/write | 7.680 | **2.446** | 3.612 | 570.759 |

---

## 19. Memgraph Results

| Workload | p50 | p95 | Mean | Min | Max |
|---|---|---|---|---|---|
| 1-hop traversal | 2.209 | 2.720 | 2.271 | 1.711 | 4.794 |
| 2-hop traversal | 2.138 | 2.586 | 2.166 | 1.609 | 3.210 |
| 3-hop traversal | 2.159 | 2.546 | 2.165 | 1.683 | 2.986 |
| Point lookup | 2.206 | 3.000 | 2.338 | 1.801 | 7.471 |
| Aggregation | 790.678 | 969.099 | 812.187 | 642.107 | 1133.244 |
| Mixed read/write | **2.446** | **3.112** | **2.539** | 2.017 | 6.792 |

---

## 20. FalkorDB Results

| Workload | p50 | p95 | Mean | Min | Max |
|---|---|---|---|---|---|
| 1-hop traversal | **2.087** | **2.558** | **2.118** | 1.565 | 2.859 |
| 2-hop traversal | **2.003** | **2.338** | **2.035** | 1.669 | 2.762 |
| 3-hop traversal | **2.102** | 2.615 | 2.157 | 1.801 | 3.311 |
| Point lookup | **1.999** | **2.479** | **2.052** | 1.644 | 2.807 |
| Aggregation | 841.798 | 956.434 | 860.930 | 800.639 | 1018.923 |
| Mixed read/write | 3.612 | 23.162 | 11.813 | 1.986 | **162.811** |

---

## 21. Neo4j Results

| Workload | p50 | p95 | Mean | Min | Max |
|---|---|---|---|---|---|
| 1-hop traversal | 14.298 | 28.606 | 15.453 | 8.452 | 37.051 |
| 2-hop traversal | 7.723 | 11.514 | 8.055 | 5.427 | 15.118 |
| 3-hop traversal | 5.452 | 8.818 | 5.860 | 4.045 | 13.261 |
| Point lookup | 5.855 | 7.029 | 5.986 | 4.843 | 11.174 |
| Aggregation | **414.571** | **530.202** | **428.155** | 357.222 | 744.608 |
| Mixed read/write | 7.680 | 9.675 | 7.937 | 6.229 | 13.537 |

---

## 22. Apache AGE Results

| Workload | p50 | p95 | Mean | Min | Max |
|---|---|---|---|---|---|
| 1-hop traversal | 126.919 | 172.367 | 129.830 | 102.862 | 188.533 |
| 2-hop traversal | 128.994 | 155.089 | 128.920 | 104.475 | 184.709 |
| 3-hop traversal | 131.247 | 158.664 | 132.421 | 107.781 | 190.945 |
| Point lookup | 172.436 | 221.760 | 174.850 | 130.815 | 252.968 |
| Aggregation | 1392.303 | 1531.511 | 1394.213 | 1265.706 | 1599.526 |
| Mixed read/write | 570.759 | 634.768 | 574.628 | 525.016 | 668.881 |

---

## 23. Overall Performance Analysis

### 23.1 Traversal

FalkorDB produced the lowest p50 latency for:

- 1-hop
- 2-hop
- 3-hop

Results:

```
1-hop : 2.087 ms
2-hop : 2.003 ms
3-hop : 2.102 ms
```

Memgraph was extremely close:

```
1-hop : 2.209 ms
2-hop : 2.138 ms
3-hop : 2.159 ms
```

Neo4j was slower than Memgraph and FalkorDB for these workloads.

Apache AGE showed substantially higher traversal latency in this benchmark configuration.

---

## 24. Point Lookup Analysis

FalkorDB achieved the best point lookup performance:

```
FalkorDB : 1.999 ms
Memgraph : 2.206 ms
Neo4j    : 5.855 ms
AGE      : 172.436 ms
```

Therefore:

> FalkorDB demonstrated the lowest median point-lookup latency in the measured configuration.

---

## 25. Aggregation Analysis

Aggregation produced a different ranking.

```
Neo4j    : 414.571 ms
Memgraph : 790.678 ms
FalkorDB : 841.798 ms
AGE      : 1392.303 ms
```

Neo4j was clearly the fastest database for this aggregation workload.

This demonstrates that a database that performs very well for simple graph traversal does not necessarily perform best for large aggregation operations.

---

## 26. Mixed Read/Write Analysis

The mixed read/write results were:

```
Memgraph : 2.446 ms
FalkorDB : 3.612 ms
Neo4j    : 7.680 ms
AGE      : 570.759 ms
```

Memgraph produced the lowest p50 latency.

FalkorDB had a relatively high maximum:

```
162.811 ms
```

compared with:

```
Memgraph : 6.792 ms
Neo4j    : 13.537 ms
AGE      : 668.881 ms
```

This indicates that although FalkorDB had excellent median performance, it experienced a larger latency spike in one measured iteration.

---

## 27. Summary of Winners

| Workload | Best Database | Best p50 |
|---|---|---|
| 1-hop traversal | **FalkorDB** | 2.087 ms |
| 2-hop traversal | **FalkorDB** | 2.003 ms |
| 3-hop traversal | **FalkorDB** | 2.102 ms |
| Point lookup | **FalkorDB** | 1.999 ms |
| Aggregation | **Neo4j** | 414.571 ms |
| Mixed read/write | **Memgraph** | 2.446 ms |

### Overall observation

There is **no single universal winner across every workload**.

The results show:

```
FalkorDB  → strongest traversal + point lookup
Memgraph  → strongest mixed read/write
Neo4j     → strongest aggregation
AGE       → highest latency among tested databases
```

---

## 28. Important Benchmark Limitation

These results should be interpreted as results from **this particular benchmark environment and configuration**.

Performance can change depending on:

- Hardware
- CPU
- RAM
- Disk
- Docker configuration
- Database configuration
- Cache state
- Indexes
- Query plans
- Dataset characteristics
- Database versions
- Network overhead
- Concurrent workloads

Therefore, the results should not be interpreted as universal performance rankings for every deployment.

A more accurate conclusion is:

> Under the tested hardware, Docker configuration, dataset, database versions, and workload definitions, FalkorDB achieved the lowest median latency for traversal and point lookup, Memgraph achieved the lowest median latency for mixed read/write operations, and Neo4j achieved the lowest median latency for aggregation.

---

## 29. Reproducibility

To reproduce the benchmark:

### Step 1 — Start Docker databases

Start each database using its Docker Compose configuration.

Example:

```
docker compose -f databases/falkordb/docker-compose.yml up -d
docker compose -f databases/age/docker-compose.yml up -d
```

Verify:

```
docker ps
```

### Step 2 — Activate Python environment

```
.venv\Scripts\Activate.ps1
```

Verify:

```
python --version
```

### Step 3 — Install dependencies

```
python -m pip install falkordb
python -m pip install "psycopg[binary]"
```

Install the remaining project dependencies if a `requirements.txt` file is available:

```
python -m pip install -r requirements.txt
```

### Step 4 — Verify databases

Run the corresponding check scripts:

```
python scripts/check_memgraph.py
python scripts/check_falkordb.py
python scripts/check_age_counts.py
```

Verify that each database contains:

```
398,372 nodes
300,000 relationships
```

### Step 5 — Run benchmarks

Run all workloads for each database.

Example:

```
python -m scripts.benchmark_falkordb_traversal
python -m scripts.benchmark_falkordb_lookup
python -m scripts.benchmark_falkordb_aggregation
python -m scripts.benchmark_falkordb_mixed
```

AGE:

```
python -m scripts.benchmark_age_traversal
python -m scripts.benchmark_age_lookup
python -m scripts.benchmark_age_aggregation
python -m scripts.benchmark_age_mixed
```

---

## 30. Results CSV Format

The final results should be stored in:

```
results/benchmark_results.csv
```

Format:

```
database,workload,iterations,warmup_iterations,p50_ms,p95_ms,mean_ms,min_ms,max_ms
```

Each database contributes six workload rows.

Total:

```
4 databases × 6 workloads = 24 benchmark records
```

---

## 31. Final Conclusion

This benchmark evaluated four graph database technologies using a common dataset containing **398,372 nodes and 300,000 relationships**.

Six workloads were evaluated:

- 1-hop traversal
- 2-hop traversal
- 3-hop traversal
- Point lookup
- Aggregation
- Mixed read/write

Each workload used **20 warm-up iterations and 100 measured iterations**.

The benchmark demonstrates that database performance is strongly workload-dependent.

**FalkorDB** achieved the best median latency for 1-hop, 2-hop, and 3-hop traversal as well as point lookup.

**Memgraph** achieved the best median latency for the mixed read/write workload.

**Neo4j** achieved the best median latency for aggregation.

**Apache AGE** showed higher latency across the tested workloads, although it provides the advantage of integrating graph capabilities directly into PostgreSQL.

Therefore, the benchmark does not identify a single universally superior database. Instead, the results demonstrate that the appropriate graph database depends on the application's workload characteristics and performance requirements.

---

## 32. Final Result

```
============================================================
GRAPH DATABASE BENCHMARK — FINAL SUMMARY
============================================================

Dataset
------------------------------------------------------------
Nodes         : 398,372
Relationships : 300,000

Benchmark
------------------------------------------------------------
Warm-up       : 20 iterations
Measurement   : 100 iterations
Workloads     : 6

Best Results
------------------------------------------------------------
Traversal     : FalkorDB
Point Lookup  : FalkorDB
Aggregation   : Neo4j
Mixed R/W     : Memgraph

============================================================
```

> **Note:** This comparison includes the four databases with complete results supplied in this conversation — Neo4j, Memgraph, FalkorDB, and Apache AGE. Earlier CognoDB numbers are not included here because the complete raw CognoDB result set was not available; adding those figures without re-verifying the original outputs would risk introducing incorrect results into the assignment.
