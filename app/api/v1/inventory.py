import http
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies.inventory_dependencies import get_inventory_dependency
from app.models.schemas import (
    ErrorResponse,
    InventoryItem,
    RestockRequest,
    RestockResponse,
)
from app.services.inventory import InventoryService

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.get(
    "/{product_name}",
    response_model=InventoryItem,
    status_code=http.HTTPStatus.OK,
    summary="Consultar estoque de um produto",
    description="Retorna os dados de estoque de um produto específico para o tenant autenticado.",
    responses={
        http.HTTPStatus.NOT_FOUND: {
            "model": ErrorResponse,
            "description": "Produto não encontrado",
        },
        http.HTTPStatus.UNAUTHORIZED: {
            "model": ErrorResponse,
            "description": "Não autenticado",
        },
        http.HTTPStatus.FORBIDDEN: {
            "model": ErrorResponse,
            "description": "Tenant não autorizado",
        },
    },
)
async def get_inventory(
    product_name: str,
    inventory_service: Annotated[InventoryService, Depends(get_inventory_dependency)],
) -> InventoryItem:
    """
    Consulta o estoque de um produto específico.

    Args:
        product_name: Nome do produto a ser consultado
        inventory_service: Serviço de inventário injetado pela dependência

    Returns:
        InventoryItem com os dados do estoque do produto
    """
    item = inventory_service.get_inventory(product_name=product_name)

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Produto '{product_name}' não encontrado no estoque",
        )

    return item


@router.get(
    "",
    response_model=List[InventoryItem],
    status_code=http.HTTPStatus.OK,
    summary="Listar todo o estoque",
    description="Retorna todos os produtos do estoque do tenant autenticado.",
    responses={
        http.HTTPStatus.UNAUTHORIZED: {
            "model": ErrorResponse,
            "description": "Não autenticado",
        },
        http.HTTPStatus.FORBIDDEN: {
            "model": ErrorResponse,
            "description": "Tenant não autorizado",
        },
    },
)
async def list_inventory(
    inventory_service: Annotated[InventoryService, Depends(get_inventory_dependency)],
) -> list[InventoryItem]:
    """
    Lista todos os produtos do estoque do tenant.

    Args:
        inventory_service: Serviço de inventário injetado pela dependência

    Returns:
        Lista de InventoryItem com todos os produtos do estoque
    """
    return inventory_service.get_all_inventory()


@router.get(
    "/alerts/low-stock",
    response_model=List[InventoryItem],
    status_code=http.HTTPStatus.OK,
    summary="Listar produtos com estoque baixo",
    description="Retorna apenas os produtos com quantidade abaixo do nível mínimo.",
    responses={
        http.HTTPStatus.UNAUTHORIZED: {
            "model": ErrorResponse,
            "description": "Não autenticado",
        },
        http.HTTPStatus.FORBIDDEN: {
            "model": ErrorResponse,
            "description": "Tenant não autorizado",
        },
    },
)
async def get_low_stock_alerts(
    inventory_service: Annotated[InventoryService, Depends(get_inventory_dependency)],
) -> list[InventoryItem]:
    """
    Lista apenas os itens onde sua quantidade é menor que o atributo indicador de quantidade mínima.

    Args:
        inventory_service: Serviço de inventário injetado pela dependência

    Returns:
        Lista de InventoryItem com produtos que precisam de reabastecimento
    """
    return inventory_service.get_low_stock_items()


@router.post(
    "/restock",
    response_model=RestockResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Solicitar reabastecimento",
    description="Dispara uma solicitação de reabastecimento para o sistema ERP externo.",
    responses={
        http.HTTPStatus.UNAUTHORIZED: {
            "model": ErrorResponse,
            "description": "Não autenticado",
        },
        http.HTTPStatus.FORBIDDEN: {
            "model": ErrorResponse,
            "description": "Tenant não autorizado",
        },
        http.HTTPStatus.UNPROCESSABLE_CONTENT: {
            "model": ErrorResponse,
            "description": "Dados inválidos",
        },
    },
)
async def request_restock(
    restock_request: RestockRequest,
    inventory_service: Annotated[InventoryService, Depends(get_inventory_dependency)],
) -> RestockResponse:
    """
    Dispara uma ação para o sistema ERP externo solicitando
    o reabastecimento da quantidade especificada.

    Args:
        restock_request: Dados da requisição de reabastecimento
        inventory_service: Serviço de inventário injetado pela dependência

    Returns:
        RestockResponse com o status da solicitação
    """
    return inventory_service.request_restock(
        product_name=restock_request.product_name,
        quantity=restock_request.quantity,
    )
