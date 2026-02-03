import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class InventoryRepository:
    def __init__(self, session: Dict[str, Any]):
        self.session = session

    def get_inventory(
        self, tenant_id: str, product_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Consulta o estoque de um produto específico para um tenant.

        Args:
            tenant_id: Identificador do tenant
            product_name: Nome do produto a ser consultado

        Returns:
            Dicionário com os dados do produto ou None se não encontrado
        """
        tenant_inventory = self.session.get(tenant_id, {})
        return tenant_inventory.get(product_name)

    def get_all_inventory(self, tenant_id: str) -> Optional[Dict[str, Any]]:
        """
        Consulta todo o estoque para um tenant.

        Args:
            tenant_id: Identificador do tenant

        Returns:
            Dicionário com todos os produtos do estoque do tenant
        """
        return self.session.get(tenant_id, {})

    def get_low_stock_items(self, tenant_id: str) -> Optional[Dict[str, Any]]:
        """
        Consulta os produtos com estoque abaixo do mínimo para um tenant.

        Args
            tenant_id: Identificador do tenant

        Returns:
            Dicionário com os produtos que estão com estoque baixo
        """
        tenant_inventory = self.session.get(tenant_id, {})

        low_stock_items = {
            product_name: data
            for product_name, data in tenant_inventory.items()
            if data["quantity"] < data["min_stock"]
        }
        return low_stock_items
