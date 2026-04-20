"""
python manage.py criar_dados_teste

Cria os dados mínimos para testar a API da máquina localmente:
- Loja "VillaGás Teste"
- Produto "Botijão P13"
- User "maquina_glp"
- Maquina "Máquina Teste" (imprime a api_key no final)
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Loja, Produto
from maquina.models import Maquina


class Command(BaseCommand):
    help = 'Cria dados de teste para a API da máquina GLP'

    def handle(self, *args, **options):
        loja, _ = Loja.objects.get_or_create(
            nome='VillaGás Teste',
            defaults={'cidade': 'São José dos Campos', 'endereco': 'Rua Teste, 1'},
        )
        self.stdout.write(f'✓ Loja: {loja.nome} (id={loja.id})')

        produto, _ = Produto.objects.get_or_create(
            nome='Botijão P13',
            loja=loja,
            defaults={
                'estoque_cheio': 10,
                'estoque_vazio': 0,
                'preco_venda': 120.00,
                'custo_unitario': 80.00,
                'alerta_estoque_minimo': 2,
                'controla_retorno': True,
            },
        )
        self.stdout.write(f'✓ Produto: {produto.nome} (estoque_cheio={produto.estoque_cheio})')

        user, criado = User.objects.get_or_create(
            username='maquina_glp',
            defaults={'is_staff': False, 'is_active': True},
        )
        if criado:
            user.set_unusable_password()
            user.save()
        self.stdout.write(f'✓ User: maquina_glp (criado={criado})')

        maquina, criada = Maquina.objects.get_or_create(
            nome='Máquina Teste',
            defaults={
                'loja': loja,
                'produto': produto,
                'preco_troca': 100.00,
                'preco_avulso': 140.00,
                'estoque_atual': 8,
                'estoque_minimo': 2,
                'ativa': True,
            },
        )
        if not criada:
            # garante que está vinculada à loja e produto corretos
            maquina.loja = loja
            maquina.produto = produto
            maquina.save()

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('═' * 50))
        self.stdout.write(self.style.SUCCESS('  DADOS DE TESTE CRIADOS'))
        self.stdout.write(self.style.SUCCESS('═' * 50))
        self.stdout.write(f'  API_TOKEN = {maquina.api_key}')
        self.stdout.write(self.style.SUCCESS('═' * 50))
        self.stdout.write('')
        self.stdout.write('Cole esse token no arquivo .env do rpi-controller:')
        self.stdout.write(f'  API_TOKEN={maquina.api_key}')
        self.stdout.write('')
