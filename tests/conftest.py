import pytest


@pytest.fixture
def sample_product_data():
    return {"quantity": 10, "min_stock": 5}


@pytest.fixture
def sample_inventory_data():
    return {
        "tenant_1": {
            "Produto A": {"quantity": 10, "min_stock": 5},
            "Produto B": {"quantity": 3, "min_stock": 10},
        },
    }