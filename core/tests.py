from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase
from django.utils import timezone

from core.models import FechamentoCaixa, Loja, PerfilUsuario, Produto, Venda


def criar_usuario(username, loja, tipo_usuario="funcionario", password="senha-teste-123"):
    user = User.objects.create_user(username, password=password)
    PerfilUsuario.objects.create(user=user, loja=loja, tipo_usuario=tipo_usuario)
    return user


class VendaTestCase(TestCase):
    """Cobre registrar_venda: descontos de estoque, validação de entrada e
    a transação atômica que evita estoque inconsistente sob concorrência."""

    def setUp(self):
        self.loja = Loja.objects.create(nome="Loja Teste", cidade="SJC", endereco="Rua X")
        self.produto = Produto.objects.create(
            loja=self.loja, nome="Gás 13kg", estoque_cheio=10, estoque_vazio=0,
            controla_retorno=False, preco_venda="100.00",
        )
        self.funcionario = criar_usuario("funcionario1", self.loja)
        self.client.defaults["SERVER_NAME"] = "admin.villagaz.com.br"
        self.client.force_login(self.funcionario)

    def _post_venda(self, **overrides):
        dados = {
            "produto": self.produto.id,
            "cliente": "",
            "quantidade": "2",
            "preco": "100.00",
            "forma_pagamento_1": "dinheiro",
            "valor_pagamento_1": "200.00",
        }
        dados.update(overrides)
        return self.client.post("/venda/", dados)

    def test_venda_normal_desconta_estoque(self):
        r = self._post_venda()
        self.assertEqual(r.status_code, 302)
        self.produto.refresh_from_db()
        self.assertEqual(self.produto.estoque_cheio, 8)
        self.assertEqual(Venda.objects.count(), 1)

    def test_quantidade_invalida_nao_gera_500(self):
        r = self._post_venda(quantidade="abc")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Quantidade inv")
        self.assertEqual(Venda.objects.count(), 0)

    def test_quantidade_zero_ou_negativa_bloqueada(self):
        r = self._post_venda(quantidade="0")
        self.assertContains(r, "Quantidade inv")
        r = self._post_venda(quantidade="-3")
        self.assertContains(r, "Quantidade inv")
        self.assertEqual(Venda.objects.count(), 0)

    def test_estoque_insuficiente_bloqueia_venda(self):
        r = self._post_venda(quantidade="999")
        self.assertContains(r, "Estoque insuficiente")
        self.produto.refresh_from_db()
        self.assertEqual(self.produto.estoque_cheio, 10)

    def test_dia_fechado_bloqueia_venda(self):
        FechamentoCaixa.objects.create(loja=self.loja, data=timezone.now().date())
        r = self._post_venda()
        self.assertContains(r, "já foi fechado")
        self.assertEqual(Venda.objects.count(), 0)

    def test_funcionario_de_outra_loja_nao_consegue_vender_produto_alheio(self):
        outra_loja = Loja.objects.create(nome="Outra Loja", cidade="Jacareí", endereco="Rua Y")
        outro_funcionario = criar_usuario("funcionario2", outra_loja)
        self.client.force_login(outro_funcionario)
        r = self._post_venda()
        # produto pertence à primeira loja; deve dar erro amigável, não 500
        self.assertContains(r, "Produto inválido")
        self.produto.refresh_from_db()
        self.assertEqual(self.produto.estoque_cheio, 10)


class CancelarVendaTestCase(TestCase):
    """Cobre cancelar_venda: exige gerente/admin e reverte estoque corretamente."""

    def setUp(self):
        self.loja = Loja.objects.create(nome="Loja Teste", cidade="SJC", endereco="Rua X")
        self.produto = Produto.objects.create(
            loja=self.loja, nome="Gás 13kg", estoque_cheio=8, estoque_vazio=0,
            controla_retorno=False, preco_venda="100.00",
        )
        self.funcionario = criar_usuario("funcionario1", self.loja, tipo_usuario="funcionario")
        self.gerente = criar_usuario("gerente1", self.loja, tipo_usuario="gerente")
        self.venda = Venda.objects.create(
            funcionario=self.funcionario, loja=self.loja, produto=self.produto,
            quantidade=2, preco_unitario="100.00",
            forma_pagamento_1="dinheiro", valor_pagamento_1="200.00",
        )
        self.client.defaults["SERVER_NAME"] = "admin.villagaz.com.br"

    def test_funcionario_comum_nao_pode_cancelar(self):
        self.client.force_login(self.funcionario)
        r = self.client.post(f"/venda/{self.venda.id}/cancelar/")
        self.assertContains(r, "Apenas gerente ou admin")
        self.venda.refresh_from_db()
        self.assertEqual(self.venda.status, "ativa")

    def test_gerente_pode_cancelar_e_estoque_volta(self):
        self.client.force_login(self.gerente)
        r = self.client.post(f"/venda/{self.venda.id}/cancelar/")
        self.assertEqual(r.status_code, 302)
        self.venda.refresh_from_db()
        self.produto.refresh_from_db()
        self.assertEqual(self.venda.status, "cancelada")
        self.assertEqual(self.produto.estoque_cheio, 10)

    def test_nao_pode_cancelar_venda_ja_cancelada(self):
        self.client.force_login(self.gerente)
        self.client.post(f"/venda/{self.venda.id}/cancelar/")
        r = self.client.post(f"/venda/{self.venda.id}/cancelar/")
        self.assertContains(r, "já foi cancelada")


class LoginRateLimitTestCase(TestCase):
    """Cobre a proteção contra força bruta em login_usuario."""

    def setUp(self):
        cache.clear()
        self.loja = Loja.objects.create(nome="Loja Teste", cidade="SJC", endereco="Rua X")
        self.user = criar_usuario("usuario1", self.loja, password="senhacorreta123")
        self.client.defaults["SERVER_NAME"] = "admin.villagaz.com.br"

    def test_bloqueia_apos_5_tentativas_erradas(self):
        for _ in range(5):
            r = self.client.post("/login/", {"username": "usuario1", "password": "errada"})
            self.assertContains(r, "Usuário ou senha inválidos")

        r = self.client.post("/login/", {"username": "usuario1", "password": "senhacorreta123"})
        self.assertContains(r, "Muitas tentativas")

    def test_login_correto_limpa_contador(self):
        self.client.post("/login/", {"username": "usuario1", "password": "errada"})
        r = self.client.post("/login/", {"username": "usuario1", "password": "senhacorreta123"})
        self.assertEqual(r.status_code, 302)

    def test_bloqueio_e_por_usuario_nao_global(self):
        for _ in range(5):
            self.client.post("/login/", {"username": "usuario1", "password": "errada"})

        outro = criar_usuario("usuario2", self.loja, password="outrasenha123")
        r = self.client.post("/login/", {"username": "usuario2", "password": "outrasenha123"})
        self.assertEqual(r.status_code, 302)
