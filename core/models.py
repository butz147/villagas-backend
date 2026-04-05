from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Loja(models.Model):
    nome = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    endereco = models.CharField(max_length=255)
    taxa_entrega = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    tempo_entrega_min = models.PositiveIntegerField(default=20)
    tempo_entrega_max = models.PositiveIntegerField(default=35)
    horario_abertura = models.TimeField(default="07:00")
    horario_fechamento = models.TimeField(default="19:00")

    loja_principal = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='filiais',
        help_text="Deixe em branco se esta é uma loja principal. Selecione a principal se esta é uma filial."
    )
    ativo = models.BooleanField(default=True, help_text="Desativar impede acesso sem excluir a loja.")

    def is_principal(self):
        return self.loja_principal is None

    def __str__(self):
        return self.nome


class PerfilUsuario(models.Model):
    TIPOS_USUARIO = [
        ("funcionario", "Funcionário"),
        ("gerente", "Gerente"),
        ("admin", "Admin"),
    ]

    # ForeignKey permite um usuário ter perfis em múltiplas lojas
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='perfis')
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE, null=True, blank=True)
    tipo_usuario = models.CharField(max_length=20, choices=TIPOS_USUARIO, default="funcionario")

    class Meta:
        unique_together = ('user', 'loja')
        verbose_name = "Perfil de Usuário"
        verbose_name_plural = "Perfis de Usuários"

    def __str__(self):
        loja_nome = self.loja.nome if self.loja else "Sem loja"
        return f"{self.user.username} - {loja_nome} - {self.tipo_usuario}"


class Cliente(models.Model):
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE, null=True, blank=True)
    nome = models.CharField(max_length=120)
    telefone = models.CharField(max_length=30, blank=True)
    endereco = models.CharField(max_length=255, blank=True)
    observacoes = models.TextField(blank=True)
    observacao_comercial = models.TextField(blank=True)
    ultimo_contato = models.DateField(null=True, blank=True)
    contatado_hoje = models.BooleanField(default=False)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(default=timezone.now)
    cpf_cnpj = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    data_nascimento = models.DateField(null=True, blank=True)
    bairro = models.CharField(max_length=100, blank=True)
    cidade = models.CharField(max_length=100, blank=True)
    complemento = models.CharField(max_length=100, blank=True)
    numero = models.CharField(max_length=20, blank=True)
    tipo_cliente = models.CharField(max_length=20, choices=[("residencial", "Residencial"), ("comercial", "Comercial"), ("industrial", "Industrial")], default="residencial")

    class Meta:
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Produto(models.Model):
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE, null=True, blank=True)
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)

    estoque_cheio = models.IntegerField(default=0)
    estoque_vazio = models.IntegerField(default=0)

    alerta_estoque_minimo = models.IntegerField(default=10)
    custo_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    preco_venda = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    imagem = models.ImageField(upload_to='produtos/', blank=True, null=True)

    controla_retorno = models.BooleanField(default=True)

    class Meta:
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Venda(models.Model):
    PAGAMENTO = [
        ("dinheiro", "Dinheiro"),
        ("pix", "Pix"),
        ("credito", "Crédito"),
        ("debito", "Débito"),
        ("fiado", "Fiado"),
        ("vale_gas", "Vale Gás"),
    ]

    STATUS_CHOICES = [
        ("ativa", "Ativa"),
        ("cancelada", "Cancelada"),
    ]

    TIPO_VENDA_CHOICES = [
        ("normal", "Venda normal"),
        ("troca", "Troca com devolução"),
        ("completo", "Venda completa sem devolução"),
        ("casco", "Venda só do casco"),
    ]

    funcionario = models.ForeignKey(User, on_delete=models.CASCADE)
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE, null=True, blank=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)

    quantidade = models.IntegerField()
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    forma_pagamento_1 = models.CharField(max_length=20, choices=PAGAMENTO, default="dinheiro")
    valor_pagamento_1 = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    forma_pagamento_2 = models.CharField(max_length=20, choices=PAGAMENTO, null=True, blank=True)
    valor_pagamento_2 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    tipo_venda = models.CharField(max_length=20, choices=TIPO_VENDA_CHOICES, default="normal")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="ativa")
    data_venda = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-data_venda"]

    def total_venda(self):
        return self.quantidade * self.preco_unitario

    def __str__(self):
        return f"{self.produto} - {self.quantidade}"


class Entregador(models.Model):
    # Loja PRINCIPAL — entregador serve esta loja e todas as suas filiais
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE, null=True, blank=True)
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='entregador',
        help_text="Conta de login para acessar o Painel do Entregador."
    )
    nome = models.CharField(max_length=120)
    telefone = models.CharField(max_length=30, blank=True)
    ativo = models.BooleanField(default=True)
    cpf = models.CharField(max_length=20, blank=True)
    cnh = models.CharField(max_length=20, blank=True)
    categoria_cnh = models.CharField(max_length=5, blank=True)
    vencimento_cnh = models.DateField(null=True, blank=True)
    endereco = models.CharField(max_length=255, blank=True)
    salario_base = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    recebe_frete = models.BooleanField(default=False, help_text="Marque se recebe frete fixo por entrega.")
    valor_frete = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Valor fixo por entrega realizada (somente se recebe_frete estiver marcado)."
    )
    data_admissao = models.DateField(null=True, blank=True)
    foto = models.ImageField(upload_to='entregadores/', blank=True, null=True)

    class Meta:
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Pedido(models.Model):
    PAGAMENTO = [
        ("dinheiro", "Dinheiro"),
        ("pix", "Pix"),
        ("credito", "Crédito"),
        ("debito", "Débito"),
        ("gas_do_povo", "Gás do Povo"),
    ]

    STATUS_CHOICES = [
        ("novo", "Novo"),
        ("preparando", "Preparando"),
        ("saiu_entrega", "Saiu para entrega"),
        ("entregue", "Entregue"),
        ("cancelado", "Cancelado"),
    ]

    loja = models.ForeignKey(Loja, on_delete=models.CASCADE, null=True, blank=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    entregador = models.ForeignKey(Entregador, on_delete=models.SET_NULL, null=True, blank=True)

    quantidade = models.IntegerField(default=1)
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    frete = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    forma_pagamento = models.CharField(max_length=20, choices=PAGAMENTO, default="dinheiro")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="novo")

    observacoes = models.TextField(blank=True)
    tempo_estimado_entrega = models.PositiveIntegerField(null=True, blank=True)
    data_entrega = models.DateTimeField(null=True, blank=True)
    avaliacao_cliente = models.PositiveSmallIntegerField(null=True, blank=True)
    data_pedido = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-data_pedido"]

    def total_pedido(self):
        return self.quantidade * self.preco_unitario

    def __str__(self):
        cliente_nome = self.cliente.nome if self.cliente else "Sem cliente"
        return f"Pedido #{self.id} - {cliente_nome}"


class MovimentacaoEstoque(models.Model):
    TIPO_CHOICES = [
        ("entrada", "Entrada"),
        ("saida", "Saída"),
        ("ajuste_cheio", "Ajuste estoque cheio"),
        ("ajuste_vazio", "Ajuste estoque vazio"),
    ]

    loja = models.ForeignKey(Loja, on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    quantidade = models.IntegerField()
    motivo = models.TextField(blank=True)

    data_movimentacao = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-data_movimentacao"]

    def __str__(self):
        return f"{self.produto.nome} - {self.get_tipo_display()} - {self.quantidade}"


class Despesa(models.Model):
    CATEGORIAS = [
        ("combustivel", "Combustível"),
        ("alimentacao", "Alimentação"),
        ("manutencao", "Manutenção"),
        ("compra_estoque", "Compra de estoque"),
        ("conta", "Conta fixa"),
        ("outro", "Outro"),
    ]

    loja = models.ForeignKey(Loja, on_delete=models.CASCADE)
    funcionario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    valor = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.CharField(max_length=30, choices=CATEGORIAS)
    descricao = models.TextField(blank=True)

    data = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-data"]

    def __str__(self):
        return f"{self.get_categoria_display()} - R$ {self.valor}"


class RetiradaFuncionario(models.Model):
    TIPOS = [
        ("adiantamento", "Adiantamento"),
        ("alimentacao", "Alimentação"),
        ("vale", "Vale"),
        ("combustivel", "Combustível"),
        ("outro", "Outro"),
    ]

    loja = models.ForeignKey(Loja, on_delete=models.CASCADE)
    funcionario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="retiradas_recebidas"
    )
    registrado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="retiradas_lancadas"
    )

    valor = models.DecimalField(max_digits=10, decimal_places=2)
    tipo = models.CharField(max_length=30, choices=TIPOS)
    descricao = models.TextField(blank=True)

    data = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-data"]

    def __str__(self):
        nome = self.funcionario.username if self.funcionario else "Sem funcionário"
        return f"{nome} - {self.get_tipo_display()} - R$ {self.valor}"


class CompraEstoque(models.Model):
    STATUS_CHOICES = [
        ("pendente", "Pendente"),
        ("aprovada", "Aprovada"),
    ]

    TIPO_COMPRA_CHOICES = [
        ("troca", "Troca de vazio por cheio"),
        ("somente_cheio", "Somente entrada de cheio"),
    ]

    loja = models.ForeignKey(Loja, on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    fornecedor = models.CharField(max_length=150, blank=True)

    quantidade = models.IntegerField()
    tipo_compra = models.CharField(
        max_length=20,
        choices=TIPO_COMPRA_CHOICES,
        default="troca"
    )

    custo_unitario_compra = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    custo_total = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pendente")

    registrado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="compras_registradas"
    )

    aprovado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="compras_aprovadas"
    )

    data = models.DateTimeField(default=timezone.now)
    aprovado_em = models.DateTimeField(null=True, blank=True)
    observacoes = models.TextField(blank=True)

    class Meta:
        ordering = ["-data"]

    def __str__(self):
        return f"{self.produto.nome} - {self.quantidade} un - {self.get_status_display()}"


class ContaPagar(models.Model):
    CATEGORIAS = [
        ("aluguel", "Aluguel"),
        ("energia", "Energia"),
        ("agua", "Água"),
        ("internet", "Internet"),
        ("fornecedor", "Fornecedor"),
        ("manutencao", "Manutenção"),
        ("outro", "Outro"),
    ]

    STATUS_CHOICES = [
        ("pendente", "Pendente"),
        ("pago", "Pago"),
    ]

    loja = models.ForeignKey(Loja, on_delete=models.CASCADE)
    descricao = models.CharField(max_length=150)
    categoria = models.CharField(max_length=30, choices=CATEGORIAS)
    valor = models.DecimalField(max_digits=10, decimal_places=2)

    vencimento = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pendente")

    registrado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    criado_em = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["status", "vencimento"]

    def __str__(self):
        return f"{self.descricao} - R$ {self.valor}"


class FechamentoCaixa(models.Model):
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE)
    data = models.DateField()

    total_vendas = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_pedidos = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_despesas = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_retiradas = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_geral = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    dinheiro_vendas = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    pix_vendas = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    credito_vendas = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    debito_vendas = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    dinheiro_pedidos = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    pix_pedidos = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    credito_pedidos = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    debito_pedidos = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    criado_em = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("loja", "data")
        ordering = ["-data", "-criado_em"]

    def __str__(self):
        return f"{self.loja.nome} - {self.data.strftime('%d/%m/%Y')}"


class AuditoriaSistema(models.Model):
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE, null=True, blank=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    acao = models.CharField(max_length=150)
    descricao = models.TextField(blank=True)

    data = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-data"]

    def __str__(self):
        usuario_nome = self.usuario.username if self.usuario else "Sem usuário"
        return f"{self.acao} - {usuario_nome} - {self.data.strftime('%d/%m/%Y %H:%M')}"


class InventarioEstoque(models.Model):
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE)
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    data = models.DateTimeField(default=timezone.now)
    observacoes = models.TextField(blank=True)

    class Meta:
        ordering = ["-data"]

    def __str__(self):
        return f"Inventário #{self.id} - {self.loja.nome} - {self.data.strftime('%d/%m/%Y %H:%M')}"


class ItemInventarioEstoque(models.Model):
    inventario = models.ForeignKey(InventarioEstoque, on_delete=models.CASCADE, related_name="itens")
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)

    estoque_cheio_sistema = models.IntegerField(default=0)
    estoque_vazio_sistema = models.IntegerField(default=0)

    estoque_cheio_contado = models.IntegerField(default=0)
    estoque_vazio_contado = models.IntegerField(default=0)

    diferenca_cheio = models.IntegerField(default=0)
    diferenca_vazio = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.produto.nome} - Inventário #{self.inventario.id}"
    

class ValeGas(models.Model):
    TIPO_CHOICES = [
        ("credito", "Crédito (entrada)"),
        ("debito", "Débito (uso)"),
    ]

    loja = models.ForeignKey(Loja, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="vales_gas")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    descricao = models.TextField(blank=True)
    registrado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    data = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-data"]

    def __str__(self):
        return f"{self.cliente.nome} - {self.get_tipo_display()} - R$ {self.valor}"


class Comodato(models.Model):
    STATUS_CHOICES = [
        ("ativo", "Ativo"),
        ("devolvido", "Devolvido"),
        ("perdido", "Perdido"),
    ]

    loja = models.ForeignKey(Loja, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="comodatos")
    item = models.CharField(max_length=150)
    quantidade = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="ativo")
    observacoes = models.TextField(blank=True)
    data_saida = models.DateField(default=timezone.now)
    data_devolucao = models.DateField(null=True, blank=True)
    registrado_por = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="comodatos_registrados"
    )

    class Meta:
        ordering = ["-data_saida"]

    def __str__(self):
        return f"{self.item} - {self.cliente.nome} - {self.get_status_display()}"


class ContaReceber(models.Model):
    STATUS_CHOICES = [
        ("pendente", "Pendente"),
        ("recebido", "Recebido"),
    ]

    loja = models.ForeignKey(Loja, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="contas_receber")
    descricao = models.CharField(max_length=150)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    vencimento = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pendente")
    venda = models.ForeignKey('Venda', on_delete=models.SET_NULL, null=True, blank=True)
    registrado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    recebido_em = models.DateTimeField(null=True, blank=True)
    criado_em = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["status", "vencimento"]

    def __str__(self):
        return f"{self.cliente.nome} - R$ {self.valor} - {self.get_status_display()}"


class CupomDesconto(models.Model):
    TIPO_DESCONTO_CHOICES = [
        ("valor", "Valor fixo"),
        ("percentual", "Percentual"),
    ]

    codigo = models.CharField(max_length=50, unique=True)
    tipo_desconto = models.CharField(
        max_length=20,
        choices=TIPO_DESCONTO_CHOICES,
        default="valor"
    )
    valor_desconto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ativo = models.BooleanField(default=True)
    data_inicio = models.DateField(null=True, blank=True)
    data_fim = models.DateField(null=True, blank=True)
    uso_maximo = models.PositiveIntegerField(null=True, blank=True)
    total_usado = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.codigo


class Veiculo(models.Model):
    STATUS_CHOICES = [
        ("ativo", "Ativo"),
        ("manutencao", "Em manutenção"),
        ("inativo", "Inativo"),
    ]

    loja = models.ForeignKey(Loja, on_delete=models.CASCADE)
    placa = models.CharField(max_length=10)
    modelo = models.CharField(max_length=100)
    ano = models.PositiveIntegerField(null=True, blank=True)
    cor = models.CharField(max_length=30, blank=True)
    km_atual = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="ativo")
    motorista_padrao = models.ForeignKey(
        Entregador, on_delete=models.SET_NULL, null=True, blank=True, related_name="veiculos"
    )
    observacoes = models.TextField(blank=True)
    chassi = models.CharField(max_length=30, blank=True)
    renavam = models.CharField(max_length=20, blank=True)
    tipo_combustivel = models.CharField(max_length=30, default="gasolina")
    capacidade_tanque = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    seguro_vencimento = models.DateField(null=True, blank=True)
    ipva_vencimento = models.DateField(null=True, blank=True)
    licenciamento_vencimento = models.DateField(null=True, blank=True)
    criado_em = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["placa"]

    def __str__(self):
        return f"{self.placa} - {self.modelo}"


class AbastecimentoVeiculo(models.Model):
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE)
    veiculo = models.ForeignKey(Veiculo, on_delete=models.CASCADE, related_name="abastecimentos")
    km_abastecimento = models.PositiveIntegerField()
    litros = models.DecimalField(max_digits=8, decimal_places=2)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    tipo_combustivel = models.CharField(max_length=30, default="gasolina")
    registrado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    data = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-data"]

    def __str__(self):
        return f"{self.veiculo.placa} - {self.litros}L - R$ {self.valor_total}"


class ManutencaoVeiculo(models.Model):
    TIPO_CHOICES = [
        ("preventiva", "Preventiva"),
        ("corretiva", "Corretiva"),
        ("troca_oleo", "Troca de óleo"),
        ("pneu", "Pneu"),
        ("revisao", "Revisão"),
        ("outro", "Outro"),
    ]

    loja = models.ForeignKey(Loja, on_delete=models.CASCADE)
    veiculo = models.ForeignKey(Veiculo, on_delete=models.CASCADE, related_name="manutencoes")
    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES)
    descricao = models.TextField()
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    km_manutencao = models.PositiveIntegerField(null=True, blank=True)
    data = models.DateField(default=timezone.now)
    proxima_manutencao_km = models.PositiveIntegerField(null=True, blank=True)
    proxima_manutencao_data = models.DateField(null=True, blank=True)
    registrado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ["-data"]

    def __str__(self):
        return f"{self.veiculo.placa} - {self.get_tipo_display()} - R$ {self.valor}"


class VendaAntecipada(models.Model):
    STATUS_CHOICES = [
        ("pendente", "Pendente"),
        ("utilizada", "Utilizada"),
        ("cancelada", "Cancelada"),
    ]

    loja = models.ForeignKey(Loja, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="vendas_antecipadas")
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=1)
    valor_pago = models.DecimalField(max_digits=10, decimal_places=2)
    forma_pagamento = models.CharField(max_length=20, default="dinheiro")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pendente")
    observacoes = models.TextField(blank=True)
    registrado_por = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="vendas_antecipadas_registradas"
    )
    utilizada_em = models.DateTimeField(null=True, blank=True)
    data = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-data"]

    def __str__(self):
        return f"{self.cliente.nome} - {self.produto.nome} x{self.quantidade} - {self.get_status_display()}"


class Fornecedor(models.Model):
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE)
    nome = models.CharField(max_length=150)
    telefone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    cnpj = models.CharField(max_length=20, blank=True)
    endereco = models.CharField(max_length=255, blank=True)
    cidade = models.CharField(max_length=100, blank=True)
    contato = models.CharField(max_length=100, blank=True)
    observacoes = models.TextField(blank=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["nome"]
        verbose_name_plural = "Fornecedores"

    def __str__(self):
        return self.nome


class VeiculoRota(models.Model):
    STATUS_CHOICES = [
        ("planejada", "Planejada"),
        ("em_andamento", "Em Andamento"),
        ("concluida", "Concluída"),
        ("cancelada", "Cancelada"),
    ]

    loja = models.ForeignKey(Loja, on_delete=models.CASCADE)
    veiculo = models.ForeignKey(Veiculo, on_delete=models.CASCADE, related_name="rotas")
    entregador = models.ForeignKey(Entregador, on_delete=models.SET_NULL, null=True, blank=True)

    data_rota = models.DateField()
    nome_rota = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="planejada")

    km_inicial = models.PositiveIntegerField(null=True, blank=True)
    km_final = models.PositiveIntegerField(null=True, blank=True)

    tempo_inicio = models.TimeField(null=True, blank=True)
    tempo_fim = models.TimeField(null=True, blank=True)

    quantidade_entregas = models.PositiveIntegerField(default=0)
    quantidade_falhas = models.PositiveIntegerField(default=0)

    valor_combustivel = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    valor_entregas = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    observacoes = models.TextField(blank=True)
    criado_em = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-data_rota"]
        verbose_name = "Rota de Veículo"
        verbose_name_plural = "Rotas de Veículos"

    @property
    def km_rodado(self):
        if self.km_inicial and self.km_final:
            return self.km_final - self.km_inicial
        return 0

    @property
    def taxa_sucesso(self):
        total = self.quantidade_entregas + self.quantidade_falhas
        if total > 0:
            return round((self.quantidade_entregas / total) * 100, 1)
        return 100

    def __str__(self):
        return f"Rota {self.data_rota} - {self.veiculo.placa}"


class RotaEntrega(models.Model):
    STATUS_CHOICES = [
        ("pendente", "Pendente"),
        ("entregue", "Entregue"),
        ("falha", "Falha na entrega"),
        ("cancelada", "Cancelada"),
    ]

    rota = models.ForeignKey(VeiculoRota, on_delete=models.CASCADE, related_name="entregas")
    pedido = models.ForeignKey(Pedido, on_delete=models.SET_NULL, null=True, blank=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True)

    ordem = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pendente")
    observacoes = models.TextField(blank=True)

    hora_entrega = models.TimeField(null=True, blank=True)

    class Meta:
        ordering = ["ordem"]
        verbose_name = "Entrega da Rota"
        verbose_name_plural = "Entregas da Rota"

    def __str__(self):
        cliente_nome = self.cliente.nome if self.cliente else "Sem cliente"
        return f"#{self.ordem} - {cliente_nome}"


class MetricaEntregador(models.Model):
    PERIODO_CHOICES = [
        ("diaria", "Diária"),
        ("semanal", "Semanal"),
        ("mensal", "Mensal"),
    ]

    loja = models.ForeignKey(Loja, on_delete=models.CASCADE)
    entregador = models.ForeignKey(Entregador, on_delete=models.CASCADE, related_name="metricas")
    tipo_periodo = models.CharField(max_length=20, choices=PERIODO_CHOICES, default="diaria")
    data = models.DateField()

    total_entregas = models.PositiveIntegerField(default=0)
    total_devolucoes = models.PositiveIntegerField(default=0)
    taxa_sucesso = models.DecimalField(max_digits=5, decimal_places=2, default=100)

    km_rodado = models.PositiveIntegerField(default=0)
    tempo_total_minutos = models.PositiveIntegerField(default=0)

    valor_vendas = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    valor_combustivel = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    valor_comissao = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    custo_por_entrega = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    custo_por_km = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        ordering = ["-data"]
        unique_together = [("entregador", "data", "tipo_periodo")]
        verbose_name = "Métrica do Entregador"
        verbose_name_plural = "Métricas dos Entregadores"

    def __str__(self):
        return f"{self.entregador.nome} - {self.data} - {self.get_tipo_periodo_display()}"


class ChecklistVeiculo(models.Model):
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE)
    veiculo = models.ForeignKey(Veiculo, on_delete=models.CASCADE, related_name="checklists")
    entregador = models.ForeignKey(Entregador, on_delete=models.SET_NULL, null=True, blank=True)
    data = models.DateTimeField(default=timezone.now)

    pneus_ok = models.BooleanField(default=True)
    freios_ok = models.BooleanField(default=True)
    oleo_ok = models.BooleanField(default=True)
    agua_ok = models.BooleanField(default=True)
    luzes_ok = models.BooleanField(default=True)
    limpeza_ok = models.BooleanField(default=True)
    documentos_ok = models.BooleanField(default=True)
    extintor_ok = models.BooleanField(default=True)
    carga_ok = models.BooleanField(default=True)

    km_atual = models.PositiveIntegerField(null=True, blank=True)
    observacoes = models.TextField(blank=True)
    registrado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ["-data"]
        verbose_name = "Checklist de Veículo"
        verbose_name_plural = "Checklists de Veículos"

    @property
    def total_itens_ok(self):
        itens = [self.pneus_ok, self.freios_ok, self.oleo_ok, self.agua_ok,
                 self.luzes_ok, self.limpeza_ok, self.documentos_ok, self.extintor_ok, self.carga_ok]
        return sum(itens)

    @property
    def total_itens(self):
        return 9

    @property
    def percentual_ok(self):
        return round((self.total_itens_ok / self.total_itens) * 100, 1)

    def __str__(self):
        return f"Checklist {self.veiculo.placa} - {self.data.strftime('%d/%m/%Y')}"


class AlertaManutencao(models.Model):
    TIPO_CHOICES = [
        ("km", "Por Quilometragem"),
        ("data", "Por Data"),
        ("documento", "Documento/Licença"),
    ]

    STATUS_CHOICES = [
        ("ativo", "Ativo"),
        ("resolvido", "Resolvido"),
        ("ignorado", "Ignorado"),
    ]

    loja = models.ForeignKey(Loja, on_delete=models.CASCADE)
    veiculo = models.ForeignKey(Veiculo, on_delete=models.CASCADE, related_name="alertas")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    titulo = models.CharField(max_length=150)
    descricao = models.TextField(blank=True)

    km_alerta = models.PositiveIntegerField(null=True, blank=True)
    data_alerta = models.DateField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="ativo")
    resolvido_em = models.DateTimeField(null=True, blank=True)
    resolvido_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    criado_em = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-criado_em"]
        verbose_name = "Alerta de Manutenção"
        verbose_name_plural = "Alertas de Manutenção"

    def __str__(self):
        return f"{self.titulo} - {self.veiculo.placa}"


class Comissao(models.Model):
    STATUS_CHOICES = [
        ("pendente", "Pendente"),
        ("pago", "Pago"),
    ]

    loja = models.ForeignKey(Loja, on_delete=models.CASCADE)
    entregador = models.ForeignKey(Entregador, on_delete=models.CASCADE, related_name="comissoes")
    venda = models.ForeignKey(Venda, on_delete=models.SET_NULL, null=True, blank=True)
    pedido = models.ForeignKey(Pedido, on_delete=models.SET_NULL, null=True, blank=True)

    valor_venda = models.DecimalField(max_digits=10, decimal_places=2)
    percentual = models.DecimalField(max_digits=5, decimal_places=2)
    valor_comissao = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pendente")
    pago_em = models.DateTimeField(null=True, blank=True)

    data = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-data"]
        verbose_name = "Comissão"
        verbose_name_plural = "Comissões"

    def __str__(self):
        return f"{self.entregador.nome} - R$ {self.valor_comissao}"


class Meta_Vendas(models.Model):
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE)
    mes = models.PositiveIntegerField()
    ano = models.PositiveIntegerField()

    meta_faturamento = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    meta_quantidade_vendas = models.PositiveIntegerField(default=0)
    meta_novos_clientes = models.PositiveIntegerField(default=0)

    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    criado_em = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = [("loja", "mes", "ano")]
        ordering = ["-ano", "-mes"]
        verbose_name = "Meta de Vendas"
        verbose_name_plural = "Metas de Vendas"

    def __str__(self):
        return f"Meta {self.mes}/{self.ano} - {self.loja.nome}"


class NotificacaoSistema(models.Model):
    TIPO_CHOICES = [
        ("info", "Informação"),
        ("alerta", "Alerta"),
        ("urgente", "Urgente"),
        ("sucesso", "Sucesso"),
    ]

    loja = models.ForeignKey(Loja, on_delete=models.CASCADE, null=True, blank=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notificacoes")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default="info")
    titulo = models.CharField(max_length=150)
    mensagem = models.TextField(blank=True)
    lida = models.BooleanField(default=False)
    link = models.CharField(max_length=255, blank=True)
    criado_em = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-criado_em"]
        verbose_name = "Notificação"
        verbose_name_plural = "Notificações"

    def __str__(self):
        return f"{self.titulo} - {self.usuario.username}"