"""
Listas fixas de categorias usadas no sistema.

Para adicionar, remover ou renomear uma categoria, basta editar as listas
abaixo. Elas são a única fonte da verdade — o restante do código (models,
rotas e frontend) consulta esses valores.
"""

# Categorias de PRODUTO usadas apenas para popular a tabela `categorias`
# na primeira execução (seed). Depois disso, as categorias são gerenciadas
# pelo banco de dados via CRUD em /categorias/.
CATEGORIAS_PRODUTO = [
    "Bebidas",
    "Entradas",
    "Pratos Principais",
    "Sobremesas",
    "Porções",
]

# Tipos de PEDIDO (comanda)
CATEGORIAS_PEDIDO = [
    "Mesa",
    "Balcão",
    "Delivery",
    "Viagem",
]

# Tipo padrão de um pedido quando nenhum (ou um inválido) é informado
CATEGORIA_PEDIDO_PADRAO = "Mesa"


def normalizar_categoria_pedido(valor):
    """Retorna um tipo de pedido válido (ou o padrão)."""
    if valor in CATEGORIAS_PEDIDO:
        return valor
    return CATEGORIA_PEDIDO_PADRAO
