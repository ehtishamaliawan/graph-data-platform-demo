import os
import uuid

import pytest
from fastapi.testclient import TestClient

from app.main import app

pytestmark = pytest.mark.integration


def test_company_create_get_and_risk_flow() -> None:
    if os.getenv("RUN_INTEGRATION_TESTS", "false").lower() != "true":
        pytest.skip("Set RUN_INTEGRATION_TESTS=true to run integration tests")

    with TestClient(app) as client:
        create_resp = client.post("/api/v1/companies", json={"name": "Acme Corp"})
        assert create_resp.status_code == 201
        company = create_resp.json()

        company_id = company["id"]
        uuid.UUID(company_id)

        get_resp = client.get(f"/api/v1/companies/{company_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["name"] == "Acme Corp"

        risk_resp = client.get(f"/api/v1/companies/{company_id}/risk", params={"max_paths": 5})
        assert risk_resp.status_code == 200
        payload = risk_resp.json()
        assert payload["company_id"] == company_id
        assert payload["path_count"] >= 0
