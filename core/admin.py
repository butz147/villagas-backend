from django.contrib import admin
from .models import (
    Loja,
    PerfilUsuario,
    Cliente,
    Produto,
    Venda,
    Pedido,
    MovimentacaoEstoque,
    Entregador,
    Despesa,
    RetiradaFuncionario,
    CompraEstoque,
    ContaPagar,
    FechamentoCaixa,
    AuditoriaSistema,
    InventarioEstoque,
    ItemInventarioEstoque,
    CupomDesconto,
    ValeGas,
    Comodato,
    ContaReceber,
    Veiculo,
    AbastecimentoVeiculo,
    ManutencaoVeiculo,
    VendaAntecipada,
    Fornecedor,
    VeiculoRota,
    RotaEntrega,
    MetricaEntregador,
    ChecklistVeiculo,
    AlertaManutencao,
    Comissao,
    Meta_Vendas,
    NotificacaoSistema,
)


@admin.register(Loja)
class LojaAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "nome",
        "cidade",
        "taxa_entrega",
        "tempo_entrega_min",
        "tempo_entrega_max",
        "horario_abertura",
        "horario_fechamento",
    )
    search_fields = ("nome", "cidade")


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ("user", "loja", "tipo_usuario")
    list_filter = ("tipo_usuario", "loja")
    search_fields = ("user__username",)


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "telefone",
        "endereco",
        "loja",
        "ultimo_contato",
        "contatado_hoje",
    )
    list_filter = ("loja", "contatado_hoje")
    search_fields = ("nome", "telefone", "endereco")


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "nome",
        "loja",
        "estoque_cheio",
        "estoque_vazio",
        "alerta_estoque_minimo",
        "custo_unitario",
        "preco_venda",
        "controla_retorno",
    )
    list_filter = ("loja", "controla_retorno")
    search_fields = ("nome",)


@admin.register(Venda)
class VendaAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "produto",
        "cliente",
        "loja",
        "funcionario",
        "quantidade",
        "preco_unitario",
        "tipo_venda",
        "forma_pagamento_1",
        "valor_pagamento_1",
        "forma_pagamento_2",
        "valor_pagamento_2",
        "status",
        "data_venda",
    )
    list_filter = ("loja", "tipo_venda", "status", "data_venda")
    search_fields = ("produto__nome", "cliente__nome", "funcionario__username")


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "cliente",
        "produto",
        "loja",
        "entregador",
        "quantidade",
        "preco_unitario",
        "forma_pagamento",
        "status",
        "data_pedido",
    )
    list_filter = ("loja", "status", "forma_pagamento", "data_pedido")
    search_fields = ("cliente__nome", "produto__nome")


@admin.register(MovimentacaoEstoque)
class MovimentacaoEstoqueAdmin(admin.ModelAdmin):
    list_display = (
        "produto",
        "loja",
        "tipo",
        "quantidade",
        "usuario",
        "data_movimentacao",
    )
    list_filter = ("loja", "tipo", "data_movimentacao")
    search_fields = ("produto__nome", "usuario__username", "motivo")


@admin.register(Entregador)
class EntregadorAdmin(admin.ModelAdmin):
    list_display = ("nome", "telefone", "loja", "ativo")
    list_filter = ("loja", "ativo")
    search_fields = ("nome", "telefone")


@admin.register(Despesa)
class DespesaAdmin(admin.ModelAdmin):
    list_display = ("categoria", "valor", "funcionario", "loja", "data")
    list_filter = ("loja", "categoria", "data")
    search_fields = ("descricao", "funcionario__username")


@admin.register(RetiradaFuncionario)
class RetiradaFuncionarioAdmin(admin.ModelAdmin):
    list_display = (
        "funcionario",
        "tipo",
        "valor",
        "registrado_por",
        "loja",
        "data",
    )
    list_filter = ("loja", "tipo", "data")
    search_fields = (
        "funcionario__username",
        "registrado_por__username",
        "descricao",
    )


@admin.register(CompraEstoque)
class CompraEstoqueAdmin(admin.ModelAdmin):
    list_display = (
        "produto",
        "fornecedor",
        "quantidade",
        "tipo_compra",
        "status",
        "custo_unitario_compra",
        "custo_total",
        "loja",
        "registrado_por",
        "aprovado_por",
        "data",
        "aprovado_em",
    )
    list_filter = ("loja", "status", "tipo_compra", "data", "fornecedor")
    search_fields = ("produto__nome", "fornecedor")


@admin.register(ContaPagar)
class ContaPagarAdmin(admin.ModelAdmin):
    list_display = (
        "descricao",
        "categoria",
        "valor",
        "vencimento",
        "status",
        "loja",
        "registrado_por",
    )
    list_filter = ("loja", "categoria", "status", "vencimento")
    search_fields = ("descricao",)


@admin.register(FechamentoCaixa)
class FechamentoCaixaAdmin(admin.ModelAdmin):
    list_display = (
        "loja",
        "data",
        "total_vendas",
        "total_pedidos",
        "total_despesas",
        "total_retiradas",
        "total_geral",
        "criado_por",
    )
    list_filter = ("loja", "data")


@admin.register(AuditoriaSistema)
class AuditoriaSistemaAdmin(admin.ModelAdmin):
    list_display = ("acao", "usuario", "loja", "data")
    list_filter = ("loja", "acao", "data")
    search_fields = ("acao", "descricao", "usuario__username")


@admin.register(InventarioEstoque)
class InventarioEstoqueAdmin(admin.ModelAdmin):
    list_display = ("id", "loja", "criado_por", "data")
    list_filter = ("loja", "data")
    search_fields = ("loja__nome", "criado_por__username", "observacoes")


@admin.register(ItemInventarioEstoque)
class ItemInventarioEstoqueAdmin(admin.ModelAdmin):
    list_display = (
        "inventario",
        "produto",
        "estoque_cheio_sistema",
        "estoque_cheio_contado",
        "diferenca_cheio",
        "estoque_vazio_sistema",
        "estoque_vazio_contado",
        "diferenca_vazio",
    )
    list_filter = ("inventario", "produto")
    search_fields = ("produto__nome",)


@admin.register(ValeGas)
class ValeGasAdmin(admin.ModelAdmin):
    list_display = ("cliente", "tipo", "valor", "loja", "registrado_por", "data")
    list_filter = ("loja", "tipo", "data")
    search_fields = ("cliente__nome", "descricao")


@admin.register(Comodato)
class ComodatoAdmin(admin.ModelAdmin):
    list_display = ("item", "cliente", "quantidade", "status", "loja", "data_saida", "data_devolucao")
    list_filter = ("loja", "status", "data_saida")
    search_fields = ("item", "cliente__nome")


@admin.register(ContaReceber)
class ContaReceberAdmin(admin.ModelAdmin):
    list_display = ("cliente", "descricao", "valor", "vencimento", "status", "loja", "registrado_por")
    list_filter = ("loja", "status", "vencimento")
    search_fields = ("cliente__nome", "descricao")


@admin.register(CupomDesconto)
class CupomDescontoAdmin(admin.ModelAdmin):
    list_display = (
        "codigo",
        "tipo_desconto",
        "valor_desconto",
        "ativo",
        "data_inicio",
        "data_fim",
        "uso_maximo",
        "total_usado",
    )
    list_filter = ("ativo", "tipo_desconto")
    search_fields = ("codigo",)


@admin.register(Veiculo)
class VeiculoAdmin(admin.ModelAdmin):
    list_display = ("placa", "modelo", "ano", "km_atual", "status", "motorista_padrao", "loja")
    list_filter = ("loja", "status")
    search_fields = ("placa", "modelo")


@admin.register(AbastecimentoVeiculo)
class AbastecimentoVeiculoAdmin(admin.ModelAdmin):
    list_display = ("veiculo", "km_abastecimento", "litros", "valor_total", "tipo_combustivel", "data")
    list_filter = ("loja", "tipo_combustivel", "data")
    search_fields = ("veiculo__placa",)


@admin.register(ManutencaoVeiculo)
class ManutencaoVeiculoAdmin(admin.ModelAdmin):
    list_display = ("veiculo", "tipo", "descricao", "valor", "km_manutencao", "data")
    list_filter = ("loja", "tipo", "data")
    search_fields = ("veiculo__placa", "descricao")


@admin.register(VendaAntecipada)
class VendaAntecipadaAdmin(admin.ModelAdmin):
    list_display = ("cliente", "produto", "quantidade", "valor_pago", "forma_pagamento", "status", "data")
    list_filter = ("loja", "status", "data")
    search_fields = ("cliente__nome", "produto__nome")


@admin.register(Fornecedor)
class FornecedorAdmin(admin.ModelAdmin):
    list_display = ("nome", "telefone", "cnpj", "cidade", "ativo", "loja")
    list_filter = ("loja", "ativo")
    search_fields = ("nome", "cnpj", "telefone")


@admin.register(VeiculoRota)
class VeiculoRotaAdmin(admin.ModelAdmin):
    list_display = ("data_rota", "nome_rota", "veiculo", "entregador", "status", "quantidade_entregas", "loja")
    list_filter = ("loja", "status", "data_rota")
    search_fields = ("nome_rota", "veiculo__placa", "entregador__nome")


@admin.register(RotaEntrega)
class RotaEntregaAdmin(admin.ModelAdmin):
    list_display = ("rota", "ordem", "cliente", "status", "hora_entrega")
    list_filter = ("status",)
    search_fields = ("cliente__nome",)


@admin.register(MetricaEntregador)
class MetricaEntregadorAdmin(admin.ModelAdmin):
    list_display = ("entregador", "data", "tipo_periodo", "total_entregas", "taxa_sucesso", "valor_vendas", "valor_comissao")
    list_filter = ("loja", "tipo_periodo", "data")
    search_fields = ("entregador__nome",)


@admin.register(ChecklistVeiculo)
class ChecklistVeiculoAdmin(admin.ModelAdmin):
    list_display = ("veiculo", "entregador", "data", "km_atual", "registrado_por")
    list_filter = ("loja", "data")
    search_fields = ("veiculo__placa",)


@admin.register(AlertaManutencao)
class AlertaManutencaoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "veiculo", "tipo", "status", "data_alerta", "km_alerta")
    list_filter = ("loja", "tipo", "status")
    search_fields = ("titulo", "veiculo__placa")


@admin.register(Comissao)
class ComissaoAdmin(admin.ModelAdmin):
    list_display = ("entregador", "valor_venda", "percentual", "valor_comissao", "status", "data")
    list_filter = ("loja", "status", "data")
    search_fields = ("entregador__nome",)


@admin.register(Meta_Vendas)
class MetaVendasAdmin(admin.ModelAdmin):
    list_display = ("loja", "mes", "ano", "meta_faturamento", "meta_quantidade_vendas", "meta_novos_clientes")
    list_filter = ("loja", "ano")


@admin.register(NotificacaoSistema)
class NotificacaoSistemaAdmin(admin.ModelAdmin):
    list_display = ("titulo", "tipo", "usuario", "lida", "criado_em")
    list_filter = ("tipo", "lida", "loja")
    search_fields = ("titulo", "mensagem", "usuario__username")