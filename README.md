# Graph Data Platform Demo

A production-style graph data platform built with FastAPI, Neo4j and Docker.

This repository demonstrates graph modelling, relationship traversal, analytics APIs and backend engineering patterns commonly used in modern data platforms.

## Tech Stack

- Python
- FastAPI
- Neo4j
- Docker
- Pytest

## Example Graph Model

```text
(Company)-[:OWNS]->(Domain)
(Employee)-[:WORKS_FOR]->(Company)
(Employee)-[:USES]->(Domain)
(Threat)-[:TARGETS]->(Company)
(Project)-[:BELONGS_TO]->(Company)
```

## Planned Features

- Graph-based entity modelling
- Company and employee relationship mapping
- Threat intelligence relationship analysis
- REST APIs with FastAPI
- Dockerised deployment
- Swagger/OpenAPI documentation
- Automated testing

## Example Use Cases

- Threat intelligence platforms
- Relationship discovery systems
- Internal data platforms
- Knowledge graph applications
- Graph analytics workloads

## Repository Structure

```text
app/
routes/
services/
tests/
data/
docs/
```

## Why This Project?

The goal of this repository is to demonstrate practical backend engineering, graph database modelling and API design using Python and Neo4j.
