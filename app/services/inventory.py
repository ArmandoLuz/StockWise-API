import logging
from datetime import datetime
from typing import Optional, List

from app.models.schemas import InventoryItem, RestockResponse, RestockStatus
from app.repositories.inventory_repository import InventoryRepository

logger = logging.getLogger(__name__)


class InventoryService:
    def __init__(
        self,
        tenant_id: str,
        repository: InventoryRepository,
    ):
        self.tenant_id: str = tenant_id
        self.repository: InventoryRepository = repository

    def get_inventory(self, product_name: str) -> Optional[InventoryItem]:
        """
        Consulta o estoque de um produto.

        Args:
            product_name: Nome do produto a consultar

        Returns:
            InventoryItem com os dados do estoque ou None se não encontrado
        """
        logger.info(
            f"[INVENTORY SERVICE] Consultando estoque - Tenant: {self.tenant_id}, Produto: {product_name}",
            extra={
                "tenant_id": self.tenant_id,
                "product_name": product_name,
            },
        )
        product_data = self.repository.get_inventory(
            tenant_id=self.tenant_id, product_name=product_name
        )

        if not product_data:
            logger.warning(
                f"[INVENTORY SERVICE] Produto não encontrado - Tenant: {self.tenant_id}, Produto: {product_name}",
                extra={
                    "tenant_id": self.tenant_id,
                    "product_name": product_name,
                },
            )
            return None

        quantity = product_data.get("quantity")
        min_stock = product_data.get("min_stock")
        needs_restock = quantity < min_stock

        logger.info(
            f"[INVENTORY] Estoque encontrado - Tenant: {self.tenant_id}, "
            f"Produto: {product_name}, Qtd: {quantity}, Min: {min_stock}, "
            f"Precisa reabastecimento: {needs_restock}",
            extra={
                "tenant_id": self.tenant_id,
                "product_name": product_name,
            },
        )

        return InventoryItem(
            tenant_id=self.tenant_id,
            product_name=product_name,
            quantity=quantity,
            min_stock=min_stock,
            needs_restock=needs_restock,
        )

    def get_all_inventory(self) -> List[InventoryItem]:
        """
        Retorna todo o inventário.

        Returns:
            Lista de InventoryItem com todos os produtos do tenant
        """
        logger.info(
            f"[INVENTORY SERVICE] Listando todo estoque - Tenant: {self.tenant_id}",
            extra={"tenant_id": self.tenant_id},
        )
        tenant_inventory = self.repository.get_all_inventory(self.tenant_id)
        if not tenant_inventory:
            logger.warning(
                f"[INVENTORY SERVICE] Tenant não encontrado: {self.tenant_id}",
                extra={"tenant_id": self.tenant_id},
            )
            return []

        items = []
        for product_name, product_data in tenant_inventory.items():
            quantity = product_data.get("quantity")
            min_stock = product_data.get("min_stock")

            items.append(
                InventoryItem(
                    tenant_id=self.tenant_id,
                    product_name=product_name,
                    quantity=quantity,
                    min_stock=min_stock,
                    needs_restock=quantity < min_stock,
                )
            )

        logger.info(
            f"[INVENTORY] Retornando {len(items)} produtos para tenant {self.tenant_id}",
            extra={"tenant_id": self.tenant_id},
        )
        return items

    def get_low_stock_items(self) -> List[InventoryItem]:
        """
        Retorna apenas os itens com estoque abaixo do mínimo.

        Returns:
            Lista de InventoryItem com produtos que precisam de reabastecimento
        """
        logger.info(
            f"[INVENTORY SERVICE] Listando itens com estoque baixo - Tenant: {self.tenant_id}",
            extra={"tenant_id": self.tenant_id},
        )
        all_items = self.repository.get_low_stock_items(tenant_id=self.tenant_id)
        return [
            InventoryItem(
                tenant_id=self.tenant_id,
                product_name=product_name,
                quantity=data.get("quantity"),
                min_stock=data.get("min_stock"),
                needs_restock=True,
            )
            for product_name, data in all_items.items()
        ]

    def request_restock(self, product_name: str, quantity: int) -> RestockResponse:
        """
        Dispara de uma ação de reabastecimento, logando a ação
        e retornando um status de sucesso.

        Args:
            product_name: Nome do produto a reabastecer
            quantity: Quantidade a ser solicitada

        Returns:
            RestockResponse com o status da solicitação
        """
        # Log da ação de reabastecimento (simulando integração com ERP)
        logger.info(
            f"[INVENTORY SERVICE] {self.tenant_id} solicitou reabastecimento de "
            f"{quantity} unidades de {product_name}.",
            extra={"tenant_id": self.tenant_id, "product_name": product_name},
        )

        # Simula envio para sistema externo
        logger.info(
            f"[INVENTORY SERVICE] {self.tenant_id} solicitou reabastecimento de "
            f"{quantity} unidades de {product_name}.",
            extra={"tenant_id": self.tenant_id, "product_name": product_name},
        )

        return RestockResponse(
            status=RestockStatus.SUCCESS,
            message="Solicitação de reabastecimento enviada com sucesso para o sistema ERP",
            tenant_id=self.tenant_id,
            product_name=product_name,
            quantity_requested=quantity,
            timestamp=datetime.now(),
        )
