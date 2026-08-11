# cognodb-graph-benchmark
Reproducible benchmarking of CognoDB Cloud and managed graph databases under comparable resources.

## Test CognoDB Connection

    python scripts/test_cognodb.py

## Resource parity: 

CognoDB was benchmarked on its C0 free tier. Other platforms were benchmarked on their closest available free tier or on resource-capped self-hosted deployments where applicable. Any unavoidable differences are treated as methodology limitations rather than hidden.

## Download automatically

    scripts/download_dataset.py

## Create the reproducible 300,000-edge sample
pipeline:

soc-pokec-relationships.txt.gz
              │
              ▼
       Read original edges
              │
              ▼
    Deterministic sampling
       random seed = 42
              │
              ▼
       300,000 edges
              │
              ▼
   pokec_edges_300k.csv
              │
              ▼
    Extract participating
          node IDs
              │
              ▼
       pokec_nodes.csv

Run:

    python scripts/create_sample.py


## Verify the dataset

    python scripts/verify_dataset.py

## CognoDB Load

    python scripts/test_cognodb_loader.py
    
    python loaders/cognodb_loader.py