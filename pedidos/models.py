from django.db import models


class Pedido(models.Model):
    PRODUTO_CHOICES = [
        ('gas', 'Botijão de gás'),
        ('agua', 'Água mineral'),
    ]

    nome = models.CharField(max_length=150)
    telefone = models.CharField(max_length=20)
    endereco = models.CharField(max_length=255)
    produto = models.CharField(max_length=20, choices=PRODUTO_CHOICES)
    observacoes = models.TextField(blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=30, default='novo')

    def __str__(self):
        return f'{self.nome} - {self.get_produto_display()}'