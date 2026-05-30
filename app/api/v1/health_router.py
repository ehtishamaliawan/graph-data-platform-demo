from fastapi import APIRouter

from app.core.metrics import metrics

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/metrics")
def get_metrics() -> dict[str, int]:
    return metrics.snapshot()
