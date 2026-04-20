import hashlib
import hmac
import json
import os
from datetime import timedelta

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.contrib.auth.models import User

from core.models import Cliente, Venda
from .models import Maquina, MaquinaEvento, PagamentoPendente


def autenticar_maquina(request):
    api_key = request.headers.get('X-Maquina-Token')
    if not api_key:
        return None
    try:
        maquina = Maquina.objects.select_related('loja', 'produto').get(api_key=api_key, ativa=True)
        maquina.ultimo_acesso = timezone.now()
        Maquina.objects.filter(pk=maquina.pk).update(ultimo_acesso=timezone.now())
        return maquina
    except Maquina.DoesNotExist:
        return None


def erro_auth():
    return JsonResponse({'erro': 'Token inválido ou máquina inativa'}, status=401)


# GET /api/maquina/status/
@csrf_exempt
@require_http_methods(['GET'])
def status(request):
    maquina = autenticar_maquina(request)
    if not maquina:
        return erro_auth()

    alarmes_ativos = maquina.eventos.filter(
        resolvido=False,
        severidade__in=['critico', 'aviso']
    ).values('tipo', 'severidade', 'mensagem', 'criado_em').order_by('-criado_em')[:5]

    return JsonResponse({
        'maquina': maquina.nome,
        'ativa': maquina.ativa,
        'estoque_atual': maquina.estoque_atual,
        'estoque_minimo': maquina.estoque_minimo,
        'estoque_baixo': maquina.estoque_atual <= maquina.estoque_minimo,
        'preco_troca': str(maquina.preco_troca),
        'preco_avulso': str(maquina.preco_avulso),
        'alarmes_ativos': list(alarmes_ativos),
    })


# GET /api/maquina/cliente/?telefone=11999999999
@csrf_exempt
@require_http_methods(['GET'])
def buscar_cliente(request):
    maquina = autenticar_maquina(request)
    if not maquina:
        return erro_auth()

    telefone = request.GET.get('telefone', '').strip()
    if not telefone:
        return JsonResponse({'erro': 'Informe o telefone'}, status=400)

    telefone_limpo = ''.join(filter(str.isdigit, telefone))

    try:
        cliente = Cliente.objects.get(
            loja=maquina.loja,
            telefone__icontains=telefone_limpo,
            ativo=True
        )
        compras = Venda.objects.filter(
            cliente=cliente,
            produto=maquina.produto,
            status='ativa'
        ).count()

        return JsonResponse({
            'encontrado': True,
            'id': cliente.id,
            'nome': cliente.nome,
            'telefone': cliente.telefone,
            'cpf': cliente.cpf_cnpj,
            'total_compras_maquina': compras,
        })
    except Cliente.DoesNotExist:
        return JsonResponse({'encontrado': False})
    except Cliente.MultipleObjectsReturned:
        cliente = Cliente.objects.filter(
            loja=maquina.loja,
            telefone__icontains=telefone_limpo,
            ativo=True
        ).order_by('-criado_em').first()
        return JsonResponse({
            'encontrado': True,
            'id': cliente.id,
            'nome': cliente.nome,
            'telefone': cliente.telefone,
            'cpf': cliente.cpf_cnpj,
        })


# POST /api/maquina/cliente/
@csrf_exempt
@require_http_methods(['POST'])
def criar_cliente(request):
    maquina = autenticar_maquina(request)
    if not maquina:
        return erro_auth()

    try:
        dados = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'erro': 'JSON inválido'}, status=400)

    nome = dados.get('nome', '').strip()
    telefone = dados.get('telefone', '').strip()

    if not nome or not telefone:
        return JsonResponse({'erro': 'Nome e telefone são obrigatórios'}, status=400)

    telefone_limpo = ''.join(filter(str.isdigit, telefone))

    cliente, criado = Cliente.objects.get_or_create(
        loja=maquina.loja,
        telefone=telefone_limpo,
        defaults={
            'nome': nome,
            'cpf_cnpj': dados.get('cpf', ''),
            'tipo_cliente': 'residencial',
            'observacoes': 'Cadastrado via máquina GLP',
        }
    )

    return JsonResponse({
        'id': cliente.id,
        'nome': cliente.nome,
        'telefone': cliente.telefone,
        'criado': criado,
    }, status=201 if criado else 200)


# POST /api/maquina/venda/
@csrf_exempt
@require_http_methods(['POST'])
def registrar_venda(request):
    maquina = autenticar_maquina(request)
    if not maquina:
        return erro_auth()

    try:
        dados = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'erro': 'JSON inválido'}, status=400)

    tipo = dados.get('tipo')  # 'troca' ou 'avulso'
    pagamento = dados.get('pagamento')  # 'pix' ou 'credito' ou 'debito'
    cliente_id = dados.get('cliente_id')

    if tipo not in ('troca', 'avulso'):
        return JsonResponse({'erro': 'tipo deve ser "troca" ou "avulso"'}, status=400)
    if pagamento not in ('pix', 'credito', 'debito'):
        return JsonResponse({'erro': 'pagamento deve ser "pix", "credito" ou "debito"'}, status=400)

    if maquina.estoque_atual <= 0:
        return JsonResponse({'erro': 'Estoque zerado'}, status=409)

    preco = maquina.preco_troca if tipo == 'troca' else maquina.preco_avulso
    tipo_venda_django = 'troca' if tipo == 'troca' else 'completo'

    cliente = None
    if cliente_id:
        try:
            cliente = Cliente.objects.get(id=cliente_id, loja=maquina.loja)
        except Cliente.DoesNotExist:
            pass

    funcionario_maquina = User.objects.filter(username='maquina_glp').first()
    if not funcionario_maquina:
        funcionario_maquina = User.objects.filter(is_superuser=True).first()

    venda = Venda.objects.create(
        funcionario=funcionario_maquina,
        loja=maquina.loja,
        cliente=cliente,
        produto=maquina.produto,
        quantidade=1,
        preco_unitario=preco,
        forma_pagamento_1=pagamento,
        valor_pagamento_1=preco,
        tipo_venda=tipo_venda_django,
        status='ativa',
    )

    maquina.produto.estoque_cheio = max(0, maquina.produto.estoque_cheio - 1)
    if tipo == 'troca':
        maquina.produto.estoque_vazio += 1
    maquina.produto.save(update_fields=['estoque_cheio', 'estoque_vazio'])

    Maquina.objects.filter(pk=maquina.pk).update(
        estoque_atual=max(0, maquina.estoque_atual - 1)
    )

    return JsonResponse({
        'venda_id': venda.id,
        'tipo': tipo,
        'pagamento': pagamento,
        'valor': str(preco),
        'estoque_restante': max(0, maquina.estoque_atual - 1),
    }, status=201)


# POST /api/maquina/evento/
@csrf_exempt
@require_http_methods(['POST'])
def registrar_evento(request):
    maquina = autenticar_maquina(request)
    if not maquina:
        return erro_auth()

    try:
        dados = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'erro': 'JSON inválido'}, status=400)

    tipo = dados.get('tipo')
    mensagem = dados.get('mensagem', '')
    severidade = dados.get('severidade', 'info')

    tipos_validos = [c[0] for c in MaquinaEvento.TIPO_CHOICES]
    if tipo not in tipos_validos:
        return JsonResponse({'erro': f'Tipo inválido. Use: {tipos_validos}'}, status=400)

    evento = MaquinaEvento.objects.create(
        maquina=maquina,
        tipo=tipo,
        severidade=severidade,
        mensagem=mensagem,
        dados_extras=dados.get('dados_extras'),
    )

    return JsonResponse({'evento_id': evento.id, 'registrado': True}, status=201)


# POST /api/maquina/reposicao/
@csrf_exempt
@require_http_methods(['POST'])
def registrar_reposicao(request):
    maquina = autenticar_maquina(request)
    if not maquina:
        return erro_auth()

    try:
        dados = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'erro': 'JSON inválido'}, status=400)

    quantidade = dados.get('quantidade')
    if not isinstance(quantidade, int) or quantidade <= 0:
        return JsonResponse({'erro': '"quantidade" deve ser inteiro positivo'}, status=400)

    Maquina.objects.filter(pk=maquina.pk).update(
        estoque_atual=quantidade
    )

    MaquinaEvento.objects.create(
        maquina=maquina,
        tipo='manutencao',
        severidade='info',
        mensagem=f'Reposição de estoque: {quantidade} botijões',
        dados_extras={'quantidade': quantidade},
    )

    return JsonResponse({'estoque_atual': quantidade, 'atualizado': True})


# POST /api/maquina/pagamento/criar/
# RPi cria um pagamento pendente e recebe o QR code PIX para exibir na tela
@csrf_exempt
@require_http_methods(['POST'])
def criar_pagamento(request):
    maquina = autenticar_maquina(request)
    if not maquina:
        return erro_auth()

    try:
        dados = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'erro': 'JSON inválido'}, status=400)

    tipo = dados.get('tipo')
    forma = dados.get('forma_pagamento', 'pix')
    cliente_id = dados.get('cliente_id')

    if tipo not in ('troca', 'avulso'):
        return JsonResponse({'erro': 'tipo deve ser "troca" ou "avulso"'}, status=400)

    valor = maquina.preco_troca if tipo == 'troca' else maquina.preco_avulso

    pagamento = PagamentoPendente.objects.create(
        maquina=maquina,
        tipo_venda=tipo,
        forma_pagamento=forma,
        valor=valor,
        cliente_id=cliente_id,
        expira_em=timezone.now() + timedelta(minutes=5),
    )

    resposta = {
        'pagamento_id': pagamento.id,
        'valor': str(valor),
        'expira_em': pagamento.expira_em.isoformat(),
        'status': 'aguardando',
    }

    # Integração Stone (PIX) — ativa quando STONE_SECRET_KEY estiver configurada
    if forma == 'pix' and os.environ.get('STONE_SECRET_KEY'):
        qr = _gerar_qr_stone(pagamento)
        if qr:
            resposta['qr_code'] = qr.get('qr_code')
            resposta['qr_code_url'] = qr.get('qr_code_url')
    else:
        # Modo desenvolvimento: simula QR code
        resposta['qr_code'] = f'00020126580014BR.GOV.BCB.PIX0136villagaz-{pagamento.id}@pix.com.br5204000053039865802BR5913VillaGas GLP6009SJC62070503***6304ABCD'
        resposta['qr_code_url'] = ''

    return JsonResponse(resposta, status=201)


# GET /api/maquina/pagamento/<id>/status/
# RPi faz polling para saber se o pagamento foi confirmado
@csrf_exempt
@require_http_methods(['GET'])
def status_pagamento(request, pagamento_id):
    maquina = autenticar_maquina(request)
    if not maquina:
        return erro_auth()

    try:
        pagamento = PagamentoPendente.objects.get(id=pagamento_id, maquina=maquina)
    except PagamentoPendente.DoesNotExist:
        return JsonResponse({'erro': 'Pagamento não encontrado'}, status=404)

    # Expira automaticamente se passou do prazo
    if pagamento.status == 'aguardando' and pagamento.expira_em and timezone.now() > pagamento.expira_em:
        pagamento.status = 'expirado'
        pagamento.save(update_fields=['status'])

    return JsonResponse({
        'pagamento_id': pagamento.id,
        'status': pagamento.status,
        'valor': str(pagamento.valor),
        'pago_em': pagamento.pago_em.isoformat() if pagamento.pago_em else None,
    })


# POST /api/maquina/webhook/stone/
# Stone chama este endpoint quando o pagamento PIX é confirmado
@csrf_exempt
@require_http_methods(['POST'])
def webhook_stone(request):
    # Valida assinatura HMAC da Stone
    stone_key = os.environ.get('STONE_WEBHOOK_SECRET', '')
    if stone_key:
        assinatura = request.headers.get('X-Stone-Signature', '')
        esperada = hmac.new(
            stone_key.encode(),
            request.body,
            hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(assinatura, esperada):
            return JsonResponse({'erro': 'Assinatura inválida'}, status=401)

    try:
        dados = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'erro': 'JSON inválido'}, status=400)

    # Stone envia o order_id no campo "id" ou "order_id"
    stone_order_id = dados.get('id') or dados.get('order_id', '')
    status_stone = dados.get('status', '').lower()

    if status_stone not in ('paid', 'approved', 'confirmed'):
        return JsonResponse({'ok': True, 'acao': 'ignorado'})

    try:
        pagamento = PagamentoPendente.objects.select_related('maquina').get(
            stone_order_id=stone_order_id,
            status='aguardando',
        )
    except PagamentoPendente.DoesNotExist:
        return JsonResponse({'ok': True, 'acao': 'nao_encontrado'})

    # Confirma o pagamento e registra a venda
    pagamento.status = 'pago'
    pagamento.pago_em = timezone.now()
    pagamento.save(update_fields=['status', 'pago_em'])

    _registrar_venda_confirmada(pagamento)

    return JsonResponse({'ok': True, 'acao': 'confirmado', 'pagamento_id': pagamento.id})


def _gerar_qr_stone(pagamento: PagamentoPendente) -> dict | None:
    """Cria order PIX na API Stone e retorna QR code."""
    import requests as req
    try:
        r = req.post(
            'https://api.stone.com.br/api/v1/transactions',
            headers={
                'Authorization': f'Bearer {os.environ["STONE_SECRET_KEY"]}',
                'Content-Type': 'application/json',
            },
            json={
                'amount': int(pagamento.valor * 100),  # centavos
                'payment_method': 'pix',
                'pix': {'expiration': 300},
                'description': f'VillaGas GLP - Pedido #{pagamento.id}',
                'metadata': {'pagamento_id': str(pagamento.id)},
            },
            timeout=8,
        )
        r.raise_for_status()
        dados = r.json()
        pagamento.stone_order_id = dados.get('id', '')
        pagamento.stone_qr_code = dados.get('pix', {}).get('qr_code', '')
        pagamento.stone_qr_code_url = dados.get('pix', {}).get('qr_code_url', '')
        pagamento.save(update_fields=['stone_order_id', 'stone_qr_code', 'stone_qr_code_url'])
        return {'qr_code': pagamento.stone_qr_code, 'qr_code_url': pagamento.stone_qr_code_url}
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f'Stone QR falhou: {e}')
        return None


def _registrar_venda_confirmada(pagamento: PagamentoPendente):
    """Cria a Venda e desconta estoque após confirmação de pagamento."""
    maquina = pagamento.maquina
    preco = pagamento.valor
    tipo_venda_django = 'troca' if pagamento.tipo_venda == 'troca' else 'completo'

    cliente = None
    if pagamento.cliente_id:
        try:
            cliente = Cliente.objects.get(id=pagamento.cliente_id, loja=maquina.loja)
        except Cliente.DoesNotExist:
            pass

    funcionario = User.objects.filter(username='maquina_glp').first() \
        or User.objects.filter(is_superuser=True).first()

    Venda.objects.create(
        funcionario=funcionario,
        loja=maquina.loja,
        cliente=cliente,
        produto=maquina.produto,
        quantidade=1,
        preco_unitario=preco,
        forma_pagamento_1=pagamento.forma_pagamento,
        valor_pagamento_1=preco,
        tipo_venda=tipo_venda_django,
        status='ativa',
    )

    maquina.produto.estoque_cheio = max(0, maquina.produto.estoque_cheio - 1)
    if pagamento.tipo_venda == 'troca':
        maquina.produto.estoque_vazio += 1
    maquina.produto.save(update_fields=['estoque_cheio', 'estoque_vazio'])
    Maquina.objects.filter(pk=maquina.pk).update(estoque_atual=max(0, maquina.estoque_atual - 1))
