from django.urls import path
from . import views

urlpatterns = [
    path('status/', views.status, name='maquina_status'),
    path('cliente/', views.buscar_cliente, name='maquina_buscar_cliente'),
    path('cliente/criar/', views.criar_cliente, name='maquina_criar_cliente'),
    path('venda/', views.registrar_venda, name='maquina_registrar_venda'),
    path('evento/', views.registrar_evento, name='maquina_registrar_evento'),
    path('reposicao/', views.registrar_reposicao, name='maquina_reposicao'),
    path('pagamento/criar/', views.criar_pagamento, name='maquina_criar_pagamento'),
    path('pagamento/<int:pagamento_id>/status/', views.status_pagamento, name='maquina_status_pagamento'),
    path('webhook/stone/', views.webhook_stone, name='maquina_webhook_stone'),
]
