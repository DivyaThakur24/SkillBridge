# Neo4j Fraud Link Analysis

Suggested GitHub repository name: `neo4j-fraud-link-analysis`

A small fraud-detection prototype that uses Neo4j to model relationships between users, payment instruments, devices, IP addresses, and transactions.

The graph structure makes it easier to detect suspicious multi-hop patterns such as:

- Multiple users sharing the same device and card
- Transaction chains connected through shared infrastructure
- Accounts indirectly linked through cards, devices, or IPs within a few hops

## Stack

- Neo4j 5
- Python 3.11+
- Cypher
- Docker Compose

## Resume-Ready Project Bullets

- Built a fraud-detection prototype in Neo4j to model relationships between users, transactions, cards, devices, IP addresses, and merchants.
- Wrote Cypher queries to surface suspicious multi-hop relationship patterns, including shared devices, reused cards, and indirectly linked accounts.
- Automated graph setup and rule execution with Python and Docker Compose, making the investigation workflow reproducible end to end.

## Repository Layout

```text
.
|-- cypher
|   |-- detection_queries.cypher
|   |-- sample_data.cypher
|   `-- schema.cypher
|-- src
|   `-- app.py
|-- docker-compose.yml
|-- requirements.txt
`-- README.md
```

## What It Models

Nodes:

- `User`
- `Transaction`
- `Card`
- `Device`
- `IPAddress`
- `Merchant`

Relationships:

- `(:User)-[:MADE]->(:Transaction)`
- `(:Transaction)-[:USED_CARD]->(:Card)`
- `(:Transaction)-[:USED_DEVICE]->(:Device)`
- `(:Transaction)-[:USED_IP]->(:IPAddress)`
- `(:Transaction)-[:AT_MERCHANT]->(:Merchant)`
- `(:User)-[:OWNS_CARD]->(:Card)`
- `(:User)-[:REGISTERED_DEVICE]->(:Device)`

## Quick Start

### 1. Start Neo4j

```bash
docker compose up -d
```

Neo4j Browser:

- URL: `http://localhost:7474`
- Username: `neo4j`
- Password: `fraudproto123`

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Load the graph and run detections

```bash
python src/app.py
```

The script will:

1. Create constraints
2. Insert sample fraud-oriented data
3. Run multi-hop Cypher detection queries
4. Print suspicious patterns to the console

## Example Detection Logic

This prototype includes Cypher queries for:

- Users sharing cards, devices, and IPs
- Indirect user-to-user links across 2 to 4 hops
- Transaction clusters routed through shared cards or devices
- Accounts connected to the same merchant through overlapping infrastructure

## Why Neo4j Fits This Use Case

Fraud investigations are highly relationship-driven. A graph model helps surface hidden links that are hard to spot in flat tables, especially when suspicious behavior emerges through shared entities and multi-hop traversal.

## Notes

- The included dataset is synthetic and designed for demonstration.
- You can extend the graph with geolocation, chargebacks, phone numbers, or watchlist entities.
- The queries in `cypher/detection_queries.cypher` are a good starting point for risk rules and investigation workflows.

## Demo Assets

- Screenshot: `demo-output.png`
- Console output: `demo-output.txt`
- Video walkthrough script: `demo-video-script.md`
- Short narration script: `demo-video-short-script.txt`

## License

This project is available under the MIT License. See `LICENSE`.
