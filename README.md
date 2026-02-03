# StockWise API

Serviço de backend multi-tenant para gestão de estoque inteligente, projetado para integração com sistemas de IA Agêntica.

## Arquitetura

```
StockWise-API/
├── app/
│   ├── api/v1/
│   │   └── inventory.py          # Endpoints REST
│   ├── database/
│   │   └── database.py           # Dados mockados
│   ├── dependencies/
│   │   ├── auth_dependency.py    # Autenticação multi-tenant
│   │   └── inventory_dependencies.py
│   ├── models/
│   │   └── schemas.py            # Modelos Pydantic
│   ├── repositories/
│   │   └── inventory_repository.py  # Acesso a dados
│   ├── services/
│   │   └── inventory.py          # Lógica de negócio
│   └── main.py                   # Configuração FastAPI
├── tests/
│   ├── test_api.py               # Testes de integração (API)
│   ├── test_service.py           # Testes unitários (Service)
│   ├── test_repository.py        # Testes unitários (Repository)
│   └── conftest.py               # Fixtures compartilhadas
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml
```

## Funcionalidades

- **Multi-tenancy**: Isolamento completo de dados entre tenants (lojas)
- **Consulta de Estoque**: Verificar quantidade e níveis mínimos de produtos
- **Alertas de Estoque Baixo**: Identificar produtos que precisam reabastecimento
- **Solicitação de Reabastecimento**: Disparar ações para sistemas ERP externos

## Requisitos

- Python 3.12+
- Docker (opcional)

## Instalação e Execução

### Opção 1: Docker (Recomendado)

```bash
# Construir e executar
docker-compose up --build

# Ou apenas executar (se já construído)
docker-compose up
```

### Opção 2: Execução Local

```bash
# Instalar dependências
uv sync

# Executar servidor
uv run uvicorn app.main:app --reload
```

A API estará disponível em `http://localhost:8000`

## Documentação da API

Acesse a documentação interativa:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Testando Multi-tenancy

### Tenants Disponíveis

| Tenant | Descrição |
|--------|-----------|
| `LojaA` | Loja com estoque baixo de parafusos |
| `LojaB` | Loja com estoque alto de parafusos |
| `LojaC` | Loja com produtos diferentes |

### Exemplos com cURL

#### 1. Consultar estoque de um produto

```bash
# LojaA - Parafuso M8 (15 unidades, precisa reabastecimento)
curl -X GET "http://localhost:8000/api/v1/inventory/Parafuso%20M8" \
  -H "X-Tenant-ID: LojaA"

# LojaB - Parafuso M8 (150 unidades, estoque OK)
curl -X GET "http://localhost:8000/api/v1/inventory/Parafuso%20M8" \
  -H "X-Tenant-ID: LojaB"
```

**Resposta LojaA:**
```json
{
  "tenant_id": "LojaA",
  "product_name": "Parafuso M8",
  "quantity": 15,
  "min_stock": 50,
  "needs_restock": true
}
```

**Resposta LojaB:**
```json
{
  "tenant_id": "LojaB",
  "product_name": "Parafuso M8",
  "quantity": 150,
  "min_stock": 50,
  "needs_restock": false
}
```

#### 2. Listar todo o estoque de um tenant

```bash
curl -X GET "http://localhost:8000/api/v1/inventory" \
  -H "X-Tenant-ID: LojaA"
```

#### 3. Listar apenas produtos com estoque baixo

```bash
curl -X GET "http://localhost:8000/api/v1/inventory/alerts/low-stock" \
  -H "X-Tenant-ID: LojaA"
```

#### 4. Solicitar reabastecimento

```bash
curl -X POST "http://localhost:8000/api/v1/inventory/restock" \
  -H "X-Tenant-ID: LojaA" \
  -H "Content-Type: application/json" \
  -d '{"product_name": "Parafuso M8", "quantity": 35}'
```

**Resposta:**
```json
{
  "status": "success",
  "message": "Solicitação de reabastecimento enviada com sucesso para o sistema ERP",
  "tenant_id": "LojaA",
  "product_name": "Parafuso M8",
  "quantity_requested": 35,
  "timestamp": "2024-01-31T10:30:00.000000"
}
```

**Log no servidor:**
```
[INVENTORY SERVICE] LojaA solicitou reabastecimento de 35 unidades de Parafuso M8.
```

### Testando Erros de Autenticação

```bash
# Sem header X-Tenant-ID (422 Unprocessable Entity)
curl -X GET "http://localhost:8000/api/v1/inventory/Parafuso%20M8"

# Tenant inválido (403 Forbidden)
curl -X GET "http://localhost:8000/api/v1/inventory/Parafuso%20M8" \
  -H "X-Tenant-ID: LojaInvalida"
```

## Executando Testes

```bash
# Executar todos os testes
uv run pytest

# Executar com cobertura
uv run pytest --cov=app --cov-report=term-missing

# Executar testes por camada
uv run pytest tests/test_api.py -v        # Testes de API
uv run pytest tests/test_service.py -v    # Testes de Service
uv run pytest tests/test_repository.py -v # Testes de Repository
```

## Endpoints da API

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/v1/inventory/{product_name}` | Consultar estoque de um produto |
| GET | `/api/v1/inventory` | Listar todo o estoque |
| GET | `/api/v1/inventory/alerts/low-stock` | Listar produtos com estoque baixo |
| POST | `/api/v1/inventory/restock` | Solicitar reabastecimento |
| GET | `/health` | Health check |

## Produtos Disponíveis por Tenant

### LojaA
| Produto | Quantidade | Mínimo | Precisa Reabastecimento |
|---------|------------|--------|-------------------------|
| Parafuso M8 | 15 | 50 | ✅ Sim |
| Porca Sextavada | 200 | 100 | ❌ Não |
| Arruela de Pressão | 5 | 30 | ✅ Sim |
| Broca 6mm | 45 | 20 | ❌ Não |
| Chave de Fenda | 12 | 15 | ✅ Sim |

### LojaB
| Produto | Quantidade | Mínimo | Precisa Reabastecimento |
|---------|------------|--------|-------------------------|
| Parafuso M8 | 150 | 50 | ❌ Não |
| Porca Sextavada | 80 | 100 | ✅ Sim |
| Arruela de Pressão | 500 | 200 | ❌ Não |
| Broca 6mm | 10 | 25 | ✅ Sim |
| Martelo | 30 | 10 | ❌ Não |

### LojaC
| Produto | Quantidade | Mínimo | Precisa Reabastecimento |
|---------|------------|--------|-------------------------|
| Parafuso M8 | 75 | 60 | ❌ Não |
| Prego 2 polegadas | 1000 | 500 | ❌ Não |
| Serra Manual | 8 | 5 | ❌ Não |
| Fita Isolante | 25 | 40 | ✅ Sim |
| Alicate | 18 | 10 | ❌ Não |

## Critérios de Qualidade Implementados

### I. Multi-tenancy e Segurança
- Header `X-Tenant-ID` obrigatório para todas as requisições
- Isolamento completo: cada tenant só acessa seus próprios dados
- Validação de tenant antes de qualquer operação

### II. Qualidade do Código e API Design
- Modelos Pydantic com validação automática
- Código modularizado em camadas (API, Service, Repository)
- Injeção de dependências para facilitar testes
- Tratamento de erros com códigos HTTP apropriados
- Type hints em todo o código

### III. Lógica de Negócio
- `get_inventory`: Retorna dados mockados específicos por tenant
- `request_restock`: Loga ação e retorna status de sucesso
- Cálculo automático de `needs_restock`

### IV. Documentação e Setup
- README detalhado com exemplos
- Docker para setup simplificado
- Documentação OpenAPI automática
- Testes automatizados por camada (36 testes, 99% cobertura)

