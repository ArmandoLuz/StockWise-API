from pydantic import BaseModel, Field
from typing import Optional, TypeVar
from datetime import datetime
from enum import Enum


class RestockStatus(str, Enum):
    """Status possíveis para uma solicitação de reabastecimento."""

    SUCCESS = "success"
    PENDING = "pending"
    FAILED = "failed"


class InventoryItem(BaseModel):
    """Modelo de resposta para dados de estoque."""

    tenant_id: str = Field(..., description="Identificador do tenant (loja)")
    product_name: str = Field(..., description="Nome do produto")
    quantity: int = Field(..., ge=0, description="Quantidade atual em estoque")
    min_stock: int = Field(..., ge=0, description="Nível mínimo de estoque")
    needs_restock: bool = Field(..., description="Indica se precisa de reabastecimento")


class RestockRequest(BaseModel):
    """Modelo de requisição para solicitação de reabastecimento."""

    product_name: str = Field(..., min_length=1, description="Nome do produto")
    quantity: int = Field(..., gt=0, description="Quantidade a ser solicitada")


class RestockResponse(BaseModel):
    """Modelo de resposta para solicitação de reabastecimento."""

    status: RestockStatus = Field(..., description="Status da solicitação")
    message: str = Field(..., description="Mensagem descritiva")
    tenant_id: str = Field(..., description="Identificador do tenant")
    product_name: str = Field(..., description="Nome do produto")
    quantity_requested: int = Field(..., description="Quantidade solicitada")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Data/hora da solicitação"
    )


class ErrorResponse(BaseModel):
    """Modelo de resposta para erros."""

    detail: str = Field(..., description="Descrição do erro")
    error_code: Optional[str] = Field(None, description="Código do erro")
