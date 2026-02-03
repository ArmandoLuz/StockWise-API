import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import inventory

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Criação da aplicação FastAPI
app = FastAPI(
    title="StockWise API",
    version="1.0.0",
)

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro das rotas
app.include_router(inventory.router, prefix="/api/v1")


@app.get("/", tags=["Health"])
async def root():
    """Endpoint raiz para verificação de saúde da API."""
    return {
        "service": "StockWise API",
        "status": "healthy",
        "version": "1.0.0",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint para monitoramento."""
    return {"status": "healthy"}
