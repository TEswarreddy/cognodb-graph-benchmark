# CognoDB Benchmark Methodology

## Dataset

Dataset: SNAP soc-Pokec

Original graph:
- Nodes: 1,632,803
- Relationships: 30,622,564
- Directed graph

Benchmark sample:
- Nodes: 398,372
- Relationships: 300,000
- Sampling seed: 42

The same processed dataset is used as the benchmark input.

## CognoDB Environment

Database: CognoDB C0

The benchmark was executed against the configured CognoDB cloud instance.

## Graph Model

Node:

(:User {id: <node_id>})

Relationship:

(:User)-[:CONNECTS_TO]->(:User)

Index:

User.id

## Traversal

Workloads:
- 1-hop traversal
- 2-hop traversal
- 3-hop traversal

For each depth:
- 100 randomly selected eligible start nodes
- Random seed: 42
- 20 warm-up iterations
- 100 measured iterations

Eligible start nodes were determined from the fixed benchmark edge dataset.

## Point Lookup

Query:
MATCH (u:User {id: $node_id})
RETURN u.id

The User.id property is indexed.

- 20 warm-up iterations
- 100 measured iterations

## Aggregation

The workload counts outgoing CONNECTS_TO relationships per User,
orders by relationship count, and returns the top 100 results.

- 20 warm-up iterations
- 100 measured iterations

## Mixed Read/Write

Each iteration:
1. Looks up two User nodes by indexed ID.
2. Creates a temporary relationship.
3. Deletes the temporary relationship.

The temporary relationship is removed so that the benchmark dataset
remains unchanged.

- 20 warm-up iterations
- 100 measured iterations

## Metrics

For each workload:
- Minimum latency
- Maximum latency
- Mean latency
- p50 latency
- p95 latency

Latency is measured client-side from query submission through complete
result consumption.

## Notes

The CognoDB C0 environment produced substantial fixed remote latency.
Traversal and point lookup workloads had p50 latencies around 400 ms,
while aggregation was substantially slower.

An initial traversal experiment sampled from all nodes and produced many
zero-result traversals. The final traversal methodology therefore uses
randomly selected nodes from depth-appropriate eligible populations.

An initial full ingestion attempt lost the Bolt connection during
relationship loading after 295,000 relationships. The remaining 5,000
relationships were successfully loaded using smaller batches. The final
graph was verified at exactly 398,372 nodes and 300,000 relationships.