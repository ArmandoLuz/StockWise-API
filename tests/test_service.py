from unittest.mock import Mock

import pytest

from app.models.schemas import RestockStatus
from app.services.inventory import InventoryService


@pytest.fixture
def mock_repository():
    return Mock()


@pytest.fixture
def service(mock_repository):
    return InventoryService(tenant_id="tenant_1", repository=mock_repository)


def test_get_inventory_returns_inventory_item_when_product_exists(
    service, mock_repository
):
    mock_repository.get_inventory.return_value = {"quantity": 10, "min_stock": 5}

    result = service.get_inventory("Produto A")

    assert result is not None
    assert result.tenant_id == "tenant_1"
    assert result.product_name == "Produto A"
    assert result.quantity == 10
    assert result.min_stock == 5
    assert result.needs_restock is False
    mock_repository.get_inventory.assert_called_once_with(
        tenant_id="tenant_1", product_name="Produto A"
    )


def test_get_inventory_returns_none_when_product_not_found(service, mock_repository):
    mock_repository.get_inventory.return_value = None

    result = service.get_inventory("Produto Inexistente")

    assert result is None


def test_get_inventory_sets_needs_restock_true_when_quantity_below_minimum(
    service, mock_repository
):
    mock_repository.get_inventory.return_value = {"quantity": 3, "min_stock": 10}

    result = service.get_inventory("Produto B")

    assert result is not None
    assert result.needs_restock is True


def test_get_all_inventory_returns_list_of_inventory_items(service, mock_repository):
    mock_repository.get_all_inventory.return_value = {
        "Produto A": {"quantity": 10, "min_stock": 5},
        "Produto B": {"quantity": 3, "min_stock": 10},
    }

    result = service.get_all_inventory()

    assert len(result) == 2
    assert all(item.tenant_id == "tenant_1" for item in result)
    product_names = [item.product_name for item in result]
    assert "Produto A" in product_names
    assert "Produto B" in product_names


def test_get_all_inventory_returns_empty_list_when_tenant_has_no_inventory(
    service, mock_repository
):
    mock_repository.get_all_inventory.return_value = None

    result = service.get_all_inventory()

    assert result == []


def test_get_low_stock_items_returns_only_items_needing_restock(
    service, mock_repository
):
    mock_repository.get_low_stock_items.return_value = {
        "Produto B": {"quantity": 3, "min_stock": 10},
    }

    result = service.get_low_stock_items()

    assert len(result) == 1
    assert result[0].product_name == "Produto B"
    assert result[0].needs_restock is True


def test_get_low_stock_items_returns_empty_list_when_no_low_stock(
    service, mock_repository
):
    mock_repository.get_low_stock_items.return_value = {}

    result = service.get_low_stock_items()

    assert result == []


def test_request_restock_returns_success_response(service):
    result = service.request_restock("Produto A", 50)

    assert result.status == RestockStatus.SUCCESS
    assert result.tenant_id == "tenant_1"
    assert result.product_name == "Produto A"
    assert result.quantity_requested == 50
    assert result.timestamp is not None


def test_request_restock_includes_descriptive_message(service):
    result = service.request_restock("Produto A", 50)

    assert "reabastecimento" in result.message.lower()