from typing import Dict

from fastapi import Depends

from app.database.database import MOCK_INVENTORY_DB
from app.dependencies.auth_dependency import get_tenant_id
from app.repositories.inventory_repository import InventoryRepository
from app.services.inventory import InventoryService


async def get_inventory_dependency(
    x_tenant_id: str = Depends(get_tenant_id),
    database_session: Dict = Depends(lambda: MOCK_INVENTORY_DB),
) -> InventoryService:
    """
    Dependência para fornecer uma instância do InventoryService configurada
    para o tenant autenticado.

    Args:
        x_tenant_id: Identificador do tenant autenticado
        database_session: Sessão de banco de dados para operações de inventário
        erp_client: Cliente para comunicação com o sistema ERP

    Returns:
        Instância do InventoryService para o tenant
    """
    return InventoryService(
        tenant_id=x_tenant_id,
        repository=InventoryRepository(session=database_session),
    )
