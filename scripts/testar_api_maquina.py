"""
Script de teste da API da máquina GLP.

Uso:
    python testar_api.py --token SEU_TOKEN [--base http://localhost:8000]

Testa todos os endpoints em sequência e mostra o resultado de cada um.
"""
import argparse
import json
import sys
import time
import requests

VERDE = "\033[92m"
VERMELHO = "\033[91m"
AMARELO = "\033[93m"
RESET = "\033[0m"
NEGRITO = "\033[1m"

ok_count = 0
falha_count = 0


def titulo(texto):
    print(f"\n{NEGRITO}{'─'*50}{RESET}")
    print(f"{NEGRITO}  {texto}{RESET}")
    print(f"{NEGRITO}{'─'*50}{RESET}")


def ok(label, detalhe=""):
    global ok_count
    ok_count += 1
    detalhe_str = f"  {AMARELO}{detalhe}{RESET}" if detalhe else ""
    print(f"  {VERDE}✓{RESET} {label}{detalhe_str}")


def falha(label, detalhe=""):
    global falha_count
    falha_count += 1
    detalhe_str = f"  → {detalhe}" if detalhe else ""
    print(f"  {VERMELHO}✗{RESET} {label}{detalhe_str}")


def get(base, token, path, params=None):
    r = requests.get(
        f"{base}/api/maquina/{path}",
        headers={"X-Maquina-Token": token},
        params=params,
        timeout=8,
    )
    return r


def post(base, token, path, dados=None):
    r = requests.post(
        f"{base}/api/maquina/{path}",
        headers={"X-Maquina-Token": token, "Content-Type": "application/json"},
        data=json.dumps(dados or {}),
        timeout=8,
    )
    return r


def rodar(base, token):
    cliente_id = None
    pagamento_id = None

    # ── 1. Autenticação ─────────────────────────────────
    titulo("1. Autenticação")

    r = get(base, "token_invalido", "status/")
    if r.status_code == 401:
        ok("Token inválido retorna 401")
    else:
        falha("Token inválido deveria retornar 401", f"recebeu {r.status_code}")

    r = get(base, token, "status/")
    if r.status_code == 200:
        d = r.json()
        ok("Token válido retorna status", f"estoque={d.get('estoque_atual')} preco_troca=R${d.get('preco_troca')}")
    else:
        falha("Status com token válido falhou", f"{r.status_code} {r.text[:100]}")
        print(f"\n{VERMELHO}Token inválido — verifique o --token.{RESET}")
        sys.exit(1)

    # ── 2. Cliente ──────────────────────────────────────
    titulo("2. Clientes")

    FONE_TESTE = "12999887766"

    r = get(base, token, "cliente/", {"telefone": FONE_TESTE})
    if r.status_code == 200:
        d = r.json()
        if d.get("encontrado"):
            cliente_id = d["id"]
            ok("Busca cliente existente", f"nome={d['nome']} id={cliente_id}")
        else:
            ok("Busca cliente inexistente retorna encontrado=false")
    else:
        falha("Busca de cliente falhou", r.text[:100])

    r = post(base, token, "cliente/criar/", {"nome": "Teste Automatizado", "telefone": FONE_TESTE})
    if r.status_code in (200, 201):
        d = r.json()
        cliente_id = d["id"]
        ok("Criar/buscar cliente", f"id={cliente_id} criado={d.get('criado')}")
    else:
        falha("Criar cliente falhou", r.text[:100])

    r = post(base, token, "cliente/criar/", {"telefone": ""})
    if r.status_code == 400:
        ok("Criar cliente sem nome/fone retorna 400")
    else:
        falha("Deveria rejeitar cliente sem dados", f"recebeu {r.status_code}")

    # ── 3. Pagamento PIX ────────────────────────────────
    titulo("3. Pagamento PIX")

    r = post(base, token, "pagamento/criar/", {
        "tipo": "troca",
        "forma_pagamento": "pix",
        "cliente_id": cliente_id,
    })
    if r.status_code == 201:
        d = r.json()
        pagamento_id = d["pagamento_id"]
        ok("Criar pagamento PIX", f"id={pagamento_id} valor=R${d.get('valor')}")
        if d.get("qr_code"):
            ok("QR code gerado", f"{d['qr_code'][:40]}...")
        else:
            falha("QR code ausente na resposta")
    else:
        falha("Criar pagamento falhou", r.text[:100])

    if pagamento_id:
        r = get(base, token, f"pagamento/{pagamento_id}/status/")
        if r.status_code == 200:
            d = r.json()
            ok("Polling de status do pagamento", f"status={d.get('status')}")
        else:
            falha("Polling de pagamento falhou", r.text[:100])

    r = post(base, token, "pagamento/criar/", {"tipo": "invalido", "forma_pagamento": "pix"})
    if r.status_code == 400:
        ok("Tipo inválido retorna 400")
    else:
        falha("Deveria rejeitar tipo inválido", f"recebeu {r.status_code}")

    # ── 4. Venda direta (cartão) ────────────────────────
    titulo("4. Venda direta (cartão)")

    r = post(base, token, "venda/", {
        "tipo": "avulso",
        "pagamento": "debito",
        "cliente_id": cliente_id,
    })
    if r.status_code == 201:
        d = r.json()
        ok("Registrar venda débito", f"venda_id={d.get('venda_id')} estoque={d.get('estoque_restante')}")
    else:
        falha("Registrar venda falhou", r.text[:100])

    # ── 5. Webhook Stone (simulado) ─────────────────────
    titulo("5. Webhook Stone (simulado)")

    # Cria um pagamento e simula o webhook confirmando
    r = post(base, token, "pagamento/criar/", {
        "tipo": "troca",
        "forma_pagamento": "pix",
        "cliente_id": cliente_id,
    })
    if r.status_code == 201:
        pid = r.json()["pagamento_id"]

        # Busca o stone_order_id (em dev está vazio, mas testa o endpoint)
        webhook_payload = json.dumps({
            "id": f"order_teste_{pid}",
            "status": "paid",
            "amount": 10000,
        })
        r2 = requests.post(
            f"{base}/api/maquina/webhook/stone/",
            data=webhook_payload,
            headers={"Content-Type": "application/json"},
            timeout=8,
        )
        if r2.status_code == 200:
            d = r2.json()
            ok("Webhook Stone aceito", f"acao={d.get('acao')}")
        else:
            falha("Webhook Stone falhou", f"{r2.status_code} {r2.text[:100]}")
    else:
        falha("Não foi possível criar pagamento para testar webhook")

    # ── 6. Evento / alarme ──────────────────────────────
    titulo("6. Eventos e alarmes")

    r = post(base, token, "evento/", {
        "tipo": "info",
        "mensagem": "Teste de evento automatizado",
        "severidade": "info",
    })
    if r.status_code == 201:
        ok("Registrar evento info")
    else:
        falha("Registrar evento falhou", r.text[:100])

    r = post(base, token, "evento/", {
        "tipo": "alarme_gas",
        "mensagem": "Teste de alarme de gás",
        "severidade": "critico",
        "dados_extras": {"sensor": 1, "leitura": 150},
    })
    if r.status_code == 201:
        ok("Registrar alarme crítico com dados_extras")
    else:
        falha("Registrar alarme falhou", r.text[:100])

    r = post(base, token, "evento/", {"tipo": "tipo_que_nao_existe"})
    if r.status_code == 400:
        ok("Tipo de evento inválido retorna 400")
    else:
        falha("Deveria rejeitar tipo inválido", f"recebeu {r.status_code}")

    # ── 7. Reposição ────────────────────────────────────
    titulo("7. Reposição de estoque")

    r = post(base, token, "reposicao/", {"quantidade": 10})
    if r.status_code == 200:
        d = r.json()
        ok("Registrar reposição", f"estoque_atual={d.get('estoque_atual')}")
    else:
        falha("Reposição falhou", r.text[:100])

    r = post(base, token, "reposicao/", {"quantidade": -1})
    if r.status_code == 400:
        ok("Quantidade negativa retorna 400")
    else:
        falha("Deveria rejeitar quantidade negativa", f"recebeu {r.status_code}")

    # ── Resultado final ─────────────────────────────────
    total = ok_count + falha_count
    print(f"\n{'═'*50}")
    print(f"  Resultado: {VERDE}{ok_count} passou{RESET}  {VERMELHO}{falha_count} falhou{RESET}  ({total} total)")
    print(f"{'═'*50}\n")

    if falha_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Testa a API da máquina GLP")
    parser.add_argument("--token", required=True, help="X-Maquina-Token (gerado pelo manage.py criar_dados_teste)")
    parser.add_argument("--base", default="http://localhost:8000", help="URL base do servidor Django")
    args = parser.parse_args()

    print(f"\n{NEGRITO}VillaGás — Teste da API da Máquina GLP{RESET}")
    print(f"  Servidor: {args.base}")
    print(f"  Token:    {args.token[:16]}...")

    rodar(args.base, args.token)
