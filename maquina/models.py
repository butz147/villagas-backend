import secrets
from django.db import models
from django.utils import timezone
from core.models import Loja, Produto


class Maquina(models.Model):
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE, related_name='maquinas')
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT, related_name='maquinas',
                                help_text='Produto P13 que esta maquina vende')
    nome = models.CharField(max_length=100, help_text='Ex: Maquina GLP - Patio Principal')
    api_key = models.CharField(max_length=64, unique=True, blank=True)
    ativa = models.BooleanField(default=True)

    preco_troca = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                      help_text='Preco com devolucao do vasilhame')
    preco_avulso = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                       help_text='Preco sem devolucao do vasilhame')

    estoque_atual = models.IntegerField(default=0)
    estoque_minimo = models.IntegerField(default=2, help_text='Alerta quando atingir este nivel')

    versao_firmware = models.CharField(max_length=20, blank=True)
    ultimo_acesso = models.DateTimeField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Máquina'
        verbose_name_plural = 'Máquinas'
        ordering = ['nome']

    def save(self, *args, **kwargs):
        if not self.api_key:
            self.api_key = secrets.token_hex(32)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome


class MaquinaEvento(models.Model):
    TIPO_CHOICES = [
        ('alarme_gas', 'Alarme de Gás'),
        ('abertura_nao_autorizada', 'Abertura Não Autorizada'),
        ('estoque_baixo', 'Estoque Baixo'),
        ('falha_sensor', 'Falha de Sensor'),
        ('falha_pagamento', 'Falha de Pagamento'),
        ('queda_energia', 'Queda de Energia'),
        ('reconexao', 'Reconexão'),
        ('manutencao', 'Manutenção'),
        ('info', 'Informativo'),
        ('erro', 'Erro'),
    ]

    SEVERIDADE_CHOICES = [
        ('critico', 'Crítico'),
        ('aviso', 'Aviso'),
        ('info', 'Info'),
    ]

    maquina = models.ForeignKey(Maquina, on_delete=models.CASCADE, related_name='eventos')
    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES)
    severidade = models.CharField(max_length=10, choices=SEVERIDADE_CHOICES, default='info')
    mensagem = models.TextField()
    dados_extras = models.JSONField(null=True, blank=True)
    resolvido = models.BooleanField(default=False)
    criado_em = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Evento da Máquina'
        verbose_name_plural = 'Eventos da Máquina'
        ordering = ['-criado_em']

    def __str__(self):
        return f'{self.maquina.nome} — {self.get_tipo_display()} ({self.criado_em:%d/%m/%Y %H:%M})'
