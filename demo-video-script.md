# Demo Video Script

## Title

Neo4j Fraud Detection Graph Demo

## Target Length

2 to 3 minutes

## Goal

Explain:

- what the project does
- how the graph model works
- how to run it
- what the output means

## Scene 1: Intro

### On screen

- Open the repository root
- Show [README.md](./README.md)

### Narration

Hi, this project is a fraud-detection prototype built with Neo4j, Python, and Cypher. The main idea is to model users, transactions, cards, devices, IP addresses, and merchants as a graph so we can detect suspicious patterns that are hard to spot in relational tables.

## Scene 2: Project Structure

### On screen

- Show the `cypher/` folder
- Show `src/app.py`
- Show `docker-compose.yml`

### Narration

The project has three main parts. First, the Cypher scripts define the schema, sample data, and fraud-detection queries. Second, the Python app connects to Neo4j, loads the graph, and runs the queries. Third, Docker Compose starts a local Neo4j instance so the whole demo is easy to reproduce.

## Scene 3: Graph Model

### On screen

- Open [README.md](./README.md)
- Scroll to the `What It Models` section

### Narration

The graph models users and transactions, plus shared entities like cards, devices, and IP addresses. That matters for fraud detection because suspicious behavior often appears through connections. For example, different users may look independent in a table, but in a graph we can quickly see that they reuse the same device or payment card.

## Scene 4: Detection Queries

### On screen

- Open [cypher/detection_queries.cypher](./cypher/detection_queries.cypher)

### Narration

These Cypher queries look for suspicious multi-hop patterns. One query finds users who share both a device and a card. Another finds indirect links between accounts within a few hops. There are also queries for cards reused across multiple users and transactions that share both device and IP infrastructure.

## Scene 5: How to Run It

### On screen

- Open a terminal in the repo
- Run:

```bash
docker compose up -d
.venv\Scripts\python.exe src\app.py
```

### Narration

To run the project, first start Neo4j with Docker Compose. Then run the Python script. The script creates the schema, loads the sample graph data, and executes the detection queries automatically.

## Scene 6: Output

### On screen

- Open [demo-output.png](./demo-output.png)

### Narration

This is the output from the demo run. Here we can see accounts like U100 and U300 sharing the same device and card, which is a strong fraud signal. We can also see indirect multi-hop links between users, reused cards across multiple accounts, and transactions connected through shared device and IP infrastructure.

## Scene 7: Code Flow

### On screen

- Open [src/app.py](./src/app.py)

### Narration

The Python runner is intentionally simple. It connects to Neo4j, waits for the database to be ready, applies the schema, loads the sample data, runs each Cypher query, and prints the results in a readable format. That makes it easy to swap in new fraud rules later.

## Scene 8: Wrap Up

### On screen

- Show repo root again

### Narration

This project shows how Neo4j can be used for fraud detection by modeling relationships directly and querying suspicious connection patterns across multiple hops. It is a good example of graph-based risk analysis, reproducible data loading, and Cypher-driven investigation workflows.

## Quick Recording Tips

- Keep the video between 2 and 3 minutes.
- Zoom in enough so terminal text is easy to read.
- Pause briefly on `demo-output.png` so viewers can absorb the results.
- If you want a stronger portfolio demo, record Neo4j Browser alongside the terminal and run one Cypher query live.

