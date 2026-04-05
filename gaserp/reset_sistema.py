import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gaserp.settings")
django.setup()

from core.models import (
    Venda,
    Pedido,
    MovimentacaoEstoque,
    Produto,
    Cliente,
    PerfilUsuario,
    Loja,
    Entregador,
)


def listar_lojas():
    lojas = Loja.objects.all().order_by("id")
    if not lojas.exists():
        print("\nNenhuma loja cadastrada.")
        return []

    print("\nLojas cadastradas:")
    for loja in lojas:
        print(f"{loja.id} - {loja.nome}")
    return list(lojas)


def zerar_tudo():
    Venda.objects.all().delete()
    Pedido.objects.all().delete()
    MovimentacaoEstoque.objects.all().delete()
    Produto.objects.all().delete()
    Cliente.objects.all().delete()
    PerfilUsuario.objects.all().delete()
    Entregador.objects.all().delete()
    Loja.objects.all().delete()
    print("Tudo foi apagado com sucesso.")


def zerar_so_vendas():
    quantidade = Venda.objects.count()
    Venda.objects.all().delete()
    print(f"{quantidade} venda(s) apagada(s) com sucesso.")


def zerar_so_estoque():
    total = 0
    for produto in Produto.objects.all():
        produto.estoque_cheio = 0
        produto.estoque_vazio = 0
        produto.save()
        total += 1
    print(f"Estoque zerado em {total} produto(s).")


def zerar_operacao_e_estoque():
    vendas = Venda.objects.count()
    pedidos = Pedido.objects.count()
    movimentacoes = MovimentacaoEstoque.objects.count()

    Venda.objects.all().delete()
    Pedido.objects.all().delete()
    MovimentacaoEstoque.objects.all().delete()

    total_produtos = 0
    for produto in Produto.objects.all():
        produto.estoque_cheio = 0
        produto.estoque_vazio = 0
        produto.save()
        total_produtos += 1

    print(
        f"Operação zerada: {vendas} venda(s), {pedidos} pedido(s), "
        f"{movimentacoes} movimentação(ões) e {total_produtos} estoque(s)."
    )


def zerar_loja_especifica():
    lojas = listar_lojas()
    if not lojas:
        return

    loja_id = input("\nDigite o ID da loja que deseja zerar: ").strip()

    if not loja_id.isdigit():
        print("ID inválido.")
        return

    loja = Loja.objects.filter(id=int(loja_id)).first()
    if not loja:
        print("Loja não encontrada.")
        return

    print(f"\nVocê escolheu a loja: {loja.nome}")
    print("Isso vai apagar desta loja:")
    print("- vendas")
    print("- pedidos")
    print("- movimentações de estoque")
    print("- clientes")
    print("- entregadores")
    print("- produtos")
    print("- perfis de usuários ligados a esta loja")
    print("- e por fim a própria loja")

    confirmar_1 = input('\nDigite EXCLUIR para continuar: ').strip()
    if confirmar_1 != "EXCLUIR":
        print("Operação cancelada.")
        return

    confirmar_2 = input(f'Digite o nome exato da loja "{loja.nome}" para confirmar: ').strip()
    if confirmar_2 != loja.nome:
        print("Nome da loja não confere. Operação cancelada.")
        return

    vendas = Venda.objects.filter(loja=loja).count()
    pedidos = Pedido.objects.filter(loja=loja).count()
    movimentacoes = MovimentacaoEstoque.objects.filter(loja=loja).count()
    clientes = Cliente.objects.filter(loja=loja).count()
    produtos = Produto.objects.filter(loja=loja).count()
    entregadores = Entregador.objects.filter(loja=loja).count()
    perfis = PerfilUsuario.objects.filter(loja=loja).count()

    Venda.objects.filter(loja=loja).delete()
    Pedido.objects.filter(loja=loja).delete()
    MovimentacaoEstoque.objects.filter(loja=loja).delete()
    Cliente.objects.filter(loja=loja).delete()
    Produto.objects.filter(loja=loja).delete()
    Entregador.objects.filter(loja=loja).delete()
    PerfilUsuario.objects.filter(loja=loja).delete()
    loja.delete()

    print(
        f"\nLoja apagada com sucesso.\n"
        f"- {vendas} venda(s)\n"
        f"- {pedidos} pedido(s)\n"
        f"- {movimentacoes} movimentação(ões)\n"
        f"- {clientes} cliente(s)\n"
        f"- {produtos} produto(s)\n"
        f"- {entregadores} entregador(es)\n"
        f"- {perfis} perfil(is)\n"
        f"- 1 loja"
    )


def zerar_operacao_de_uma_loja_sem_apagar_loja():
    lojas = listar_lojas()
    if not lojas:
        return

    loja_id = input("\nDigite o ID da loja para zerar só a operação: ").strip()

    if not loja_id.isdigit():
        print("ID inválido.")
        return

    loja = Loja.objects.filter(id=int(loja_id)).first()
    if not loja:
        print("Loja não encontrada.")
        return

    print(f"\nLoja escolhida: {loja.nome}")
    print("Isso vai apagar apenas:")
    print("- vendas da loja")
    print("- pedidos da loja")
    print("- movimentações da loja")
    print("- e zerar o estoque dos produtos da loja")
    print("Clientes, entregadores, produtos e a loja serão mantidos.")

    confirmar = input('\nDigite LIMPAR para continuar: ').strip()
    if confirmar != "LIMPAR":
        print("Operação cancelada.")
        return

    vendas = Venda.objects.filter(loja=loja).count()
    pedidos = Pedido.objects.filter(loja=loja).count()
    movimentacoes = MovimentacaoEstoque.objects.filter(loja=loja).count()
    produtos = Produto.objects.filter(loja=loja)

    Venda.objects.filter(loja=loja).delete()
    Pedido.objects.filter(loja=loja).delete()
    MovimentacaoEstoque.objects.filter(loja=loja).delete()

    total_produtos = 0
    for produto in produtos:
        produto.estoque_cheio = 0
        produto.estoque_vazio = 0
        produto.save()
        total_produtos += 1

    print(
        f"\nOperação da loja {loja.nome} zerada com sucesso.\n"
        f"- {vendas} venda(s)\n"
        f"- {pedidos} pedido(s)\n"
        f"- {movimentacoes} movimentação(ões)\n"
        f"- {total_produtos} estoque(s) zerado(s)"
    )


def menu():
    while True:
        print("\n=== RESET DO SISTEMA ===")
        print("1 - Zerar tudo")
        print("2 - Zerar só vendas")
        print("3 - Zerar só estoque")
        print("4 - Zerar vendas, pedidos, movimentações e estoque")
        print("5 - Listar lojas")
        print("6 - Zerar uma loja específica por completo")
        print("7 - Zerar só a operação de uma loja")
        print("0 - Sair")

        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            confirmar = input("Isso apaga TUDO. Digite APAGAR TUDO: ").strip()
            if confirmar == "APAGAR TUDO":
                zerar_tudo()
            else:
                print("Operação cancelada.")

        elif opcao == "2":
            confirmar = input("Digite APAGAR VENDAS para confirmar: ").strip()
            if confirmar == "APAGAR VENDAS":
                zerar_so_vendas()
            else:
                print("Operação cancelada.")

        elif opcao == "3":
            confirmar = input("Digite ZERAR ESTOQUE para confirmar: ").strip()
            if confirmar == "ZERAR ESTOQUE":
                zerar_so_estoque()
            else:
                print("Operação cancelada.")

        elif opcao == "4":
            confirmar = input("Digite LIMPAR OPERACAO para confirmar: ").strip()
            if confirmar == "LIMPAR OPERACAO":
                zerar_operacao_e_estoque()
            else:
                print("Operação cancelada.")

        elif opcao == "5":
            listar_lojas()

        elif opcao == "6":
            zerar_loja_especifica()

        elif opcao == "7":
            zerar_operacao_de_uma_loja_sem_apagar_loja()

        elif opcao == "0":
            print("Saindo...")
            break

        else:
            print("Opção inválida.")


if __name__ == "__main__":
    menu()