from django.contrib import admin
from django.urls import path, include
from core import views
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render, redirect, get_object_or_404


from core.views import (
    # acesso
    login_usuario,
    logout_usuario,
    inicio,

    # operação
    registrar_venda,
    pedidos,
    atualizar_status_pedido,
    painel_entregador,
    entregar_pedido,
    historico_produto,
    historico_produto_excel,

    # clientes
    lista_clientes,
    historico_cliente,
    clientes_recompra,
    historico_cliente_excel,
    clientes_excel,
    editar_cliente,
    novo_cliente,
    editar_cliente,
    inativar_cliente,
    buscar_clientes_ajax,

    # estoque
    movimentar_estoque,
    estoque_admin,
    inventario_estoque,
    detalhe_inventario_estoque,
    lista_produtos,

    # compras
    compras_estoque,
    aprovar_compra_estoque,

    # financeiro
    despesas,
    retiradas_funcionarios,
    contas_pagar,
    pagar_conta,
    contas_receber,
    receber_conta,

    # vale gás e comodato
    vale_gas,
    comodatos,

    # veículos
    veiculos,
    editar_veiculo,

    # vendas antecipadas
    vendas_antecipadas,

    # dashboards e gestão
    dashboard,
    admin_geral,
    lucro_diario,
    dre_mensal,
    comparativo_mensal,

    # fechamento e caixa
    fechamento_caixa,
    salvar_fechamento_caixa,
    historico_fechamentos,
    saldo_caixa,
    reabrir_fechamento,
    fechamento_caixa_pdf,
    fechamento_caixa_excel,
    cancelar_venda,
    relatorio_vendas,
    auditoria_sistema,

    # rotas e frota
    rotas,
    detalhe_rota,
    checklist_veiculo,
    alertas_manutencao,

    # fornecedores
    fornecedores,
    editar_fornecedor,

    # comissões
    comissoes,

    # metas
    metas,

    # métricas
    metricas_entregadores,

    # notificações
    notificacoes,
)

from core.views import notificacoes_json

urlpatterns = [
    # admin django
    path('admin/', admin.site.urls),
    path('api/pedidos/', include('pedidos.urls')),

    # acesso
    path('login/', login_usuario),
    path('logout/', logout_usuario, name='logout'),
    path('', inicio),
    path('accounts/login/', lambda request: redirect('/login/?next=' + request.GET.get('next', ''))),

    # operação
    path('venda/', registrar_venda, name='vendas'),
    path('pedidos/', pedidos, name='pedidos'),
    path('pedido/<int:pedido_id>/status/', atualizar_status_pedido, name='atualizar_status_pedido'),
    path('painel-entregador/', painel_entregador),
    path('entregar-pedido/<int:pedido_id>/', entregar_pedido),
    path('produto/<int:produto_id>/historico/', historico_produto, name='historico_produto'),
    path('produto/<int:produto_id>/historico/excel/', historico_produto_excel, name='historico_produto_excel'),
    path("api/pedidos/criar-pedido-site/", views.criar_pedido_site, name="criar_pedido_site"),
    path("api/produtos/", views.listar_produtos_site, name="listar_produtos_site"),
    path("api/pedidos/painel/", views.pedidos_json, name="pedidos_json"),
    path("api/pedidos/acompanhar/", views.acompanhar_pedido_site, name="acompanhar_pedido_site"),
    path(
    "pedidos/<int:pedido_id>/status/<str:novo_status>/",
    views.alterar_status_pedido,
    name="alterar_status_pedido",
    ),
    
    # clientes
    path('clientes/', lista_clientes, name='lista_clientes'),
    path('clientes/excel/', clientes_excel, name='clientes_excel'),  
    path('cliente/novo/', novo_cliente, name='novo_cliente'),
    path('cliente/<int:cliente_id>/editar/', editar_cliente, name='editar_cliente'),
    path('cliente/<int:cliente_id>/inativar/', inativar_cliente, name='inativar_cliente'),
    path('cliente/<int:cliente_id>/historico/', historico_cliente, name='historico_cliente'),
    path('cliente/<int:cliente_id>/historico/excel/', historico_cliente_excel, name='historico_cliente_excel'),
    path('clientes-recompra/', clientes_recompra, name='clientes_recompra'),
    path('clientes/buscar/ajax/', buscar_clientes_ajax, name='buscar_clientes_ajax'),

    # estoque
    path('movimentacao-estoque/', movimentar_estoque),
    path('estoque-admin/', estoque_admin),
    path('inventario-estoque/', inventario_estoque),
    path('inventario-estoque/<int:inventario_id>/', detalhe_inventario_estoque),
    path('produtos/', lista_produtos, name='produtos'),

    # compras de estoque
    path('compras-estoque/', compras_estoque),
    path('compras-estoque/<int:compra_id>/aprovar/', aprovar_compra_estoque),

    # financeiro
    path('despesas/', despesas),
    path('retiradas-funcionarios/', retiradas_funcionarios),
    path('contas-pagar/', contas_pagar),
    path('contas-pagar/<int:conta_id>/pagar/', pagar_conta),
    path('contas-receber/', contas_receber),
    path('contas-receber/<int:conta_id>/receber/', receber_conta),

    # vale gás e comodato
    path('vale-gas/', vale_gas),
    path('comodatos/', comodatos),

    # veículos
    path('veiculos/', veiculos),
    path('veiculos/<int:veiculo_id>/editar/', editar_veiculo),

    # vendas antecipadas
    path('vendas-antecipadas/', vendas_antecipadas),

    # dashboards e gestão
    path('dashboard/', views.admin_geral, name='dashboard'),
    path('admin-geral/', admin_geral),
    path('lucro-diario/', lucro_diario),
    path('dre-mensal/', dre_mensal),
    path('comparativo-mensal/', comparativo_mensal),

    # fechamento e caixa
    path('fechamento-caixa/', fechamento_caixa),
    path('fechamento-caixa/salvar/', salvar_fechamento_caixa),
    path('historico-fechamentos/', historico_fechamentos),
    path('historico-fechamentos/<int:fechamento_id>/reabrir/', reabrir_fechamento),
    path('saldo-caixa/', saldo_caixa),
    path('fechamento-caixa/pdf/', fechamento_caixa_pdf),
    path('fechamento-caixa/excel/', fechamento_caixa_excel),
    path('venda/<int:venda_id>/cancelar/', cancelar_venda),
    path('relatorio/', relatorio_vendas),
    path('auditoria-sistema/', auditoria_sistema),

    # rotas e frota
    path('rotas/', rotas),
    path('rotas/<int:rota_id>/', detalhe_rota),
    path('checklist-veiculo/', checklist_veiculo),
    path('alertas-manutencao/', alertas_manutencao),

    # fornecedores
    path('fornecedores/', fornecedores),
    path('fornecedores/<int:fornecedor_id>/editar/', editar_fornecedor),

    # comissões e metas
    path('comissoes/', comissoes),
    path('metas/', metas),

    # métricas
    path('metricas-entregadores/', metricas_entregadores),

    # notificações
    path('notificacoes/', notificacoes),
    path('api/notificacoes/', notificacoes_json),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
