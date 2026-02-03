import pytest

from app.repositories.inventory_repository import InventoryRepository


@pytest.fixture
def sample_inventory():
    return {
        "tenant_1": {
            "Produto A": {"quantity": 10, "min_stock": 5},
            "Produto B": {"quantity": 3, "min_stock": 10},
            "Produto C": {"quantity": 100, "min_stock": 50},
        },
        "tenant_2": {
            "Produto X": {"quantity": 50, "min_stock": 20},
        },
    }


@pytest.fixture
def repository(sample_inventory):
    return InventoryRepository(session=sample_inventory)


def test_get_inventory_returns_product_data(repository):
    result = repository.get_inventory("tenant_1", "Produto A")

    assert result is not None
    assert result["quantity"] == 10
    assert result["min_stock"] == 5


def test_get_inventory_returns_none_for_nonexistent_product(repository):
    result = repository.get_inventory("tenant_1", "Produto Inexistente")

    assert result is None


def test_get_inventory_returns_none_for_nonexistent_tenant(repository):
    result = repository.get_inventory("tenant_inexistente", "Produto A")

    assert result is None


def test_get_all_inventory_returns_all_products_for_tenant(repository):
    result = repository.get_all_inventory("tenant_1")

    assert result is not None
    assert len(result) == 3
    assert "Produto A" in result
    assert "Produto B" in result
    assert "Produto C" in result


def test_get_all_inventory_returns_none_for_nonexistent_tenant(repository):
    result = repository.get_all_inventory("tenant_inexistente")

    assert not result


def test_get_low_stock_items_returns_only_items_below_minimum(repository):
    result = repository.get_low_stock_items("tenant_1")

    assert result is not None
    assert len(result) == 1
    assert "Produto B" in result
    assert result["Produto B"]["quantity"] == 3
    assert result["Produto B"]["min_stock"] == 10


def test_get_low_stock_items_returns_empty_when_all_items_have_sufficient_stock(
    repository,
):
    result = repository.get_low_stock_items("tenant_2")

    assert result == {}


def test_repository_isolates_data_between_tenants(repository):
    result_tenant_1 = repository.get_inventory("tenant_1", "Produto A")
    result_tenant_2 = repository.get_inventory("tenant_2", "Produto A")

    assert result_tenant_1 is not None
    assert result_tenant_2 is None