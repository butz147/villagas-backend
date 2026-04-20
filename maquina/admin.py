from django.contrib import admin
from django.utils.html import format_html
from .models import Maquina, MaquinaEvento


@admin.register(Maquina)
class MaquinaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'loja', 'produto', 'estoque_atual', 'estoque_minimo',
                    'status_estoque', 'ativa', 'ultimo_acesso']
    list_filter = ['ativa', 'loja']
    readonly_fields = ['api_key', 'ultimo_acesso', 'criado_em']
    fieldsets = (
        ('Identificação', {
            'fields': ('nome', 'loja', 'produto', 'ativa')
        }),
        ('Preços', {
            'fields': ('preco_troca', 'preco_avulso')
        }),
        ('Estoque', {
            'fields': ('estoque_atual', 'estoque_minimo')
        }),
        ('Acesso (API)', {
            'fields': ('api_key',),
            'classes': ('collapse',),
            'description': 'Chave de autenticação usada pelo Raspberry Pi. Não compartilhe.',
        }),
        ('Info', {
            'fields': ('versao_firmware', 'ultimo_acesso', 'criado_em'),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Estoque')
    def status_estoque(self, obj):
        if obj.estoque_atual <= 0:
            return format_html('<span style="color:red;font-weight:bold">⚠ ZERADO</span>')
        if obj.estoque_atual <= obj.estoque_minimo:
            return format_html('<span style="color:orange;font-weight:bold">⚡ BAIXO ({})</span>', obj.estoque_atual)
        return format_html('<span style="color:green">✓ OK ({})</span>', obj.estoque_atual)


@admin.register(MaquinaEvento)
class MaquinaEventoAdmin(admin.ModelAdmin):
    list_display = ['maquina', 'tipo', 'severidade_badge', 'mensagem', 'resolvido', 'criado_em']
    list_filter = ['maquina', 'tipo', 'severidade', 'resolvido']
    list_editable = ['resolvido']
    readonly_fields = ['maquina', 'tipo', 'severidade', 'mensagem', 'dados_extras', 'criado_em']
    ordering = ['-criado_em']

    @admin.display(description='Severidade')
    def severidade_badge(self, obj):
        cores = {'critico': 'red', 'aviso': 'orange', 'info': 'gray'}
        cor = cores.get(obj.severidade, 'gray')
        return format_html(
            '<span style="color:{};font-weight:bold">{}</span>',
            cor, obj.get_severidade_display()
        )
