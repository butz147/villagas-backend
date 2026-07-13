import re

f = 'gaserp/core/templates/base.html'
c = open(f).read()

if '/lancamento-retroativo/' in c:
    print('Link ja existe no menu.')
else:
    # Desktop sidebar: insere antes de "Vendas Antecipadas"
    m = re.search(r'<a [^>]*href="/vendas-antecipadas/"', c)
    if m:
        novo = '<a class="" href="/lancamento-retroativo/">\n                    <i class="bi bi-clock-history"></i> <span>Retroativo</span>\n                </a>\n                '
        c = c[:m.start()] + novo + c[m.start():]
        print('Desktop: adicionado')

    # Mobile menu: insere antes de "Comodatos" (segunda ocorrencia)
    matches = list(re.finditer(r'<a [^>]*href="/comodatos/"', c))
    t = matches[1] if len(matches) >= 2 else (matches[0] if matches else None)
    if t:
        novo2 = '<a href="/lancamento-retroativo/"><i class="bi bi-clock-history"></i> Retroativo</a>\n            '
        c = c[:t.start()] + novo2 + c[t.start():]
        print('Mobile: adicionado')

    open(f, 'w').write(c)
    print('Pronto!')
