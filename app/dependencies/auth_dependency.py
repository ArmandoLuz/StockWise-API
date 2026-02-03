from typing import Annotated, Dict

from fastapi import Depends, Header, HTTPException
from starlette import status

from app.database.database import MOCK_TENANTS_DB


async def get_tenant_id(
    x_tenant_id: Annotated[str, Header(description="Identificador do tenant")],
    database_session: Dict = Depends(lambda: MOCK_TENANTS_DB),
) -> str:
    """
    Dependência para extrair e validar o tenant_id do header da requisição.

    Args:
        x_tenant_id: Header X-Tenant-ID da requisição
        database_session: Sessão de banco de dados contendo tenants válidos

    Returns:
        tenant_id validado

    Raises:
        HTTPException: Se o header não for fornecido ou tenant inválido
    """

    if x_tenant_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Header X-Tenant-ID é obrigatório para autenticação",
        )

    if x_tenant_id not in database_session:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Tenant '{x_tenant_id}' não autorizado ou não existe",
        )

    return x_tenant_id
