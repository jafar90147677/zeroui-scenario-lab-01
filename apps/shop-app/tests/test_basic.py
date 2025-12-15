from __future__ import annotations

import pytest

from apps.shop_app.app import app


@pytest.fixture()
def client():
    with app.test_client() as client:
        yield client


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok", "service": "shop-app"}

