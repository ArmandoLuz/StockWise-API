import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def valid_headers():
    return {"X-Tenant-ID": "LojaA"}


# --- Autenticação ---


def test_request_without_tenant_header_returns_422(client):
    response = client.get("/api/v1/inventory/Parafuso M8")

    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any("x-tenant-id" in str(error.get("loc", [])) for error in errors)


def test_invalid_tenant_returns_403(client):
    response = client.get(
        "/api/v1/inventory/Parafuso M8",
        headers={"X-Tenant-ID": "TenantInvalido"},
    )

    assert response.status_code == 403
    assert "não autorizado" in response.json()["detail"]


def test_valid_tenant_is_accepted(client, valid_headers):
    response = client.get("/api/v1/inventory/Parafuso M8", headers=valid_headers)

    assert response.status_code == 200


# --- GET /inventory/{product_name} ---


def test_get_inventory_returns_product_data(client, valid_headers):
    response = client.get("/api/v1/inventory/Parafuso M8", headers=valid_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["tenant_id"] == "LojaA"
    assert data["product_name"] == "Parafuso M8"
    assert data["quantity"] == 15
    assert data["min_stock"] == 50


def test_get_inventory_returns_404_for_nonexistent_product(client, valid_headers):
    response = client.get("/api/v1/inventory/ProdutoInexistente", headers=valid_headers)

    assert response.status_code == 404


def test_get_inventory_needs_restock_true_when_quantity_below_minimum(
    client, valid_headers
):
    response = client.get("/api/v1/inventory/Parafuso M8", headers=valid_headers)

    data = response.json()
    assert data["needs_restock"] is True
    assert data["quantity"] < data["min_stock"]


def test_get_inventory_needs_restock_false_when_quantity_above_minimum(
    client, valid_headers
):
    response = client.get("/api/v1/inventory/Porca Sextavada", headers=valid_headers)

    data = response.json()
    assert data["needs_restock"] is False
    assert data["quantity"] >= data["min_stock"]


# --- GET /inventory ---


def test_list_inventory_returns_all_products_for_tenant(client, valid_headers):
    response = client.get("/api/v1/inventory", headers=valid_headers)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 5


def test_list_inventory_all_items_belong_to_tenant(client, valid_headers):
    response = client.get("/api/v1/inventory", headers=valid_headers)

    data = response.json()
    assert all(item["tenant_id"] == "LojaA" for item in data)


# --- GET /inventory/alerts/low-stock ---


def test_low_stock_returns_only_items_needing_restock(client, valid_headers):
    response = client.get("/api/v1/inventory/alerts/low-stock", headers=valid_headers)

    assert response.status_code == 200
    data = response.json()
    assert all(item["needs_restock"] is True for item in data)
    assert all(item["quantity"] < item["min_stock"] for item in data)


# --- POST /inventory/restock ---


def test_request_restock_returns_201_on_success(client, valid_headers):
    response = client.post(
        "/api/v1/inventory/restock",
        headers=valid_headers,
        json={"product_name": "Parafuso M8", "quantity": 35},
    )

    assert response.status_code == 201


def test_request_restock_returns_correct_data(client, valid_headers):
    response = client.post(
        "/api/v1/inventory/restock",
        headers=valid_headers,
        json={"product_name": "Parafuso M8", "quantity": 35},
    )

    data = response.json()
    assert data["status"] == "success"
    assert data["tenant_id"] == "LojaA"
    assert data["product_name"] == "Parafuso M8"
    assert data["quantity_requested"] == 35
    assert "timestamp" in data


def test_request_restock_returns_422_for_zero_quantity(client, valid_headers):
    response = client.post(
        "/api/v1/inventory/restock",
        headers=valid_headers,
        json={"product_name": "Parafuso M8", "quantity": 0},
    )

    assert response.status_code == 422


def test_request_restock_returns_422_for_negative_quantity(client, valid_headers):
    response = client.post(
        "/api/v1/inventory/restock",
        headers=valid_headers,
        json={"product_name": "Parafuso M8", "quantity": -5},
    )

    assert response.status_code == 422


def test_request_restock_returns_422_for_empty_product_name(client, valid_headers):
    response = client.post(
        "/api/v1/inventory/restock",
        headers=valid_headers,
        json={"product_name": "", "quantity": 10},
    )

    assert response.status_code == 422


# --- Multi-tenancy ---


def test_different_tenants_get_different_data(client):
    response_a = client.get(
        "/api/v1/inventory/Parafuso M8",
        headers={"X-Tenant-ID": "LojaA"},
    )
    response_b = client.get(
        "/api/v1/inventory/Parafuso M8",
        headers={"X-Tenant-ID": "LojaB"},
    )

    assert response_a.json()["quantity"] == 15
    assert response_b.json()["quantity"] == 150


def test_tenant_cannot_access_other_tenant_exclusive_product(client):
    response_a = client.get(
        "/api/v1/inventory/Martelo",
        headers={"X-Tenant-ID": "LojaA"},
    )
    response_b = client.get(
        "/api/v1/inventory/Martelo",
        headers={"X-Tenant-ID": "LojaB"},
    )

    assert response_a.status_code == 404
    assert response_b.status_code == 200


# --- Health endpoints ---


def test_root_endpoint_returns_healthy(client):
    response = client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "StockWise API"


def test_health_endpoint_returns_healthy(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"