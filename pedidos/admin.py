from django.contrib import admin
from .models import Pedido


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'telefone', 'produto', 'status', 'criado_em')
    list_filter = ('produto', 'status', 'criado_em')
    search_fields = ('nome', 'telefone', 'endereco')