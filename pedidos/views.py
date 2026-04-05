import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Pedido


@csrf_exempt
def criar_pedido(request):
    if request.method != 'POST':
        return JsonResponse({'erro': 'Método não permitido'}, status=405)

    try:
        data = json.loads(request.body)

        nome = data.get('nome', '').strip()
        telefone = data.get('telefone', '').strip()
        endereco = data.get('endereco', '').strip()
        produto = data.get('produto', '').strip()
        observacoes = data.get('observacoes', '').strip()

        if not nome or not telefone or not endereco or not produto:
            return JsonResponse({'erro': 'Preencha os campos obrigatórios'}, status=400)

        pedido = Pedido.objects.create(
            nome=nome,
            telefone=telefone,
            endereco=endereco,
            produto=produto,
            observacoes=observacoes,
        )

        return JsonResponse({
            'mensagem': 'Pedido criado com sucesso',
            'pedido_id': pedido.id,
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse({'erro': 'JSON inválido'}, status=400)

    except Exception as e:
        return JsonResponse({'erro': str(e)}, status=500)