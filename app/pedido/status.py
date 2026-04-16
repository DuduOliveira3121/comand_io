# ============================================
# CONSTANTES DE STATUS DO PEDIDO
# ============================================

STATUS_CRIADO = "criado"
STATUS_EM_PREPARO = "em_preparo"
STATUS_PRONTO = "pronto"
STATUS_ENTREGUE = "entregue"
STATUS_ABERTO = "aberto"

# Lista de valores válidos
STATUS_VALIDOS = [
    STATUS_CRIADO,
    STATUS_EM_PREPARO,
    STATUS_PRONTO,
    STATUS_ENTREGUE,
    STATUS_ABERTO,
]

# Mapeamento de status para descrições amigáveis
STATUS_DESCRICOES = {
    STATUS_CRIADO: "Criado",
    STATUS_EM_PREPARO: "Em Preparo",
    STATUS_PRONTO: "Pronto",
    STATUS_ENTREGUE: "Entregue",
    STATUS_ABERTO: "Aberto",
}
