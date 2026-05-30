from collections.abc import Iterable
from contextlib import contextmanager
from typing import Any

from neo4j import Driver, GraphDatabase, Record

from app.core.metrics import metrics


class Neo4jClient:
    def __init__(self, uri: str, user: str, password: str, database: str) -> None:
        self._driver: Driver = GraphDatabase.driver(uri, auth=(user, password))
        self._database = database

    def close(self) -> None:
        self._driver.close()

    @contextmanager
    def session(self):
        with self._driver.session(database=self._database) as session:
            yield session

    def execute_write(self, query_name: str, query: str, parameters: dict[str, Any] | None = None) -> list[Record]:
        metrics.record_graph_query(query_name)
        with self.session() as session:
            result = session.execute_write(lambda tx: tx.run(query, parameters or {}))
            return list(result)

    def execute_read(self, query_name: str, query: str, parameters: dict[str, Any] | None = None) -> list[Record]:
        metrics.record_graph_query(query_name)
        with self.session() as session:
            result = session.execute_read(lambda tx: tx.run(query, parameters or {}))
            return list(result)

    def run_statements(self, query_name: str, statements: Iterable[str]) -> None:
        with self.session() as session:
            metrics.record_graph_query(query_name)
            for statement in statements:
                session.run(statement).consume()
