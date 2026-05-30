from dataclasses import dataclass, field
from threading import Lock


@dataclass
class Metrics:
    http_requests_total: int = 0
    graph_queries_total: int = 0
    _lock: Lock = field(default_factory=Lock)

    def record_http_request(self, _method: str, _path: str, _status_code: int) -> None:
        with self._lock:
            self.http_requests_total += 1

    def record_graph_query(self, _query_name: str) -> None:
        with self._lock:
            self.graph_queries_total += 1

    def snapshot(self) -> dict[str, int]:
        with self._lock:
            return {
                "http_requests_total": self.http_requests_total,
                "graph_queries_total": self.graph_queries_total,
            }


metrics = Metrics()
