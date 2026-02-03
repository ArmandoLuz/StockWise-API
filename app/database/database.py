# Base de dados mockada para simular multi-tenancy
# Cada tenant tem seu próprio inventário com dados diferentes
MOCK_INVENTORY_DB = {
    "LojaA": {
        "Parafuso M8": {"quantity": 15, "min_stock": 50},
        "Porca Sextavada": {"quantity": 200, "min_stock": 100},
        "Arruela de Pressão": {"quantity": 5, "min_stock": 30},
        "Broca 6mm": {"quantity": 45, "min_stock": 20},
        "Chave de Fenda": {"quantity": 12, "min_stock": 15},
    },
    "LojaB": {
        "Parafuso M8": {"quantity": 150, "min_stock": 50},
        "Porca Sextavada": {"quantity": 80, "min_stock": 100},
        "Arruela de Pressão": {"quantity": 500, "min_stock": 200},
        "Broca 6mm": {"quantity": 10, "min_stock": 25},
        "Martelo": {"quantity": 30, "min_stock": 10},
    },
    "LojaC": {
        "Parafuso M8": {"quantity": 75, "min_stock": 60},
        "Prego 2 polegadas": {"quantity": 1000, "min_stock": 500},
        "Serra Manual": {"quantity": 8, "min_stock": 5},
        "Fita Isolante": {"quantity": 25, "min_stock": 40},
        "Alicate": {"quantity": 18, "min_stock": 10},
    },
}

# Base de tenants mockada para validação de existência
MOCK_TENANTS_DB = list(MOCK_INVENTORY_DB.keys())
