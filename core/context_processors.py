from .models import PerfilUsuario, Loja


def perfil_ativo(request):
    """
    Injeta em todos os templates:
    - perfil_ativo: perfil do usuário na loja atual
    - loja_ativa: loja selecionada na sessão
    - lojas_usuario: todas as lojas que o usuário tem acesso (para o seletor)
    """
    if not request.user.is_authenticated:
        return {}

    lojas_usuario = []
    loja_ativa = None
    perfil = None

    try:
        perfis = PerfilUsuario.objects.filter(user=request.user).select_related('loja')

        if perfis.exists():
            lojas_usuario = [p.loja for p in perfis if p.loja]

            # Tenta usar a loja da sessão
            loja_id = request.session.get('loja_ativa_id')
            if loja_id:
                perfil = perfis.filter(loja_id=loja_id).first()

            # Fallback: primeiro perfil
            if not perfil:
                perfil = perfis.first()
                if perfil and perfil.loja:
                    request.session['loja_ativa_id'] = perfil.loja.id

            loja_ativa = perfil.loja if perfil else None

    except Exception:
        pass

    return {
        'perfil_ativo': perfil,
        'loja_ativa': loja_ativa,
        'lojas_usuario': lojas_usuario,
        'folguista_ativo': request.session.get('folguista_ativo', False),
        'folguista_nome': request.session.get('folguista_nome', ''),
    }
