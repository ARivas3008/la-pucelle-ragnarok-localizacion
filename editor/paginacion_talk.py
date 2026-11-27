"""Paginación conservadora para TALK: mínimo de cuadros, sin cortar palabras.
La capacidad de 28 pares y 3 filas procede del compilador existente; no es
una medición visual nueva. No interpreta voz, retratos ni otros opcodes.
"""
from functools import lru_cache

def paginate_words(words, widths, limit=28, rows=3, space=1):
    """Devuelve páginas de líneas; cada línea es una tupla de palabras.
    Prioridad: cuadros mínimos, líneas mínimas, evitar cuadros de una palabra/una fila,
    evitar líneas de una palabra, equilibrio visual.
    El llamador debe limitar la entrada a una intervención continua.
    """
    words=tuple(words);widths=tuple(widths)
    if not words or len(words)!=len(widths) or len(words)>512:
        raise ValueError('Intervención vacía o demasiado larga')
    if not 1<=rows<=3 or limit<1 or space<1:
        raise ValueError('Capacidad inválida')
    if any(not isinstance(w,int) or not 1<=w<=limit for w in widths):
        raise ValueError('Palabra excede capacidad')
    n=len(words)
    opts=[]
    for i in range(n):
        length=0;choices=[]
        for j in range(i,n):
            length+=widths[j]+(space if j>i else 0)
            if length>limit:break
            choices.append((j+1,length))
        opts.append(tuple(reversed(choices)))
    # Coste lexicográfico. Una página de una fila es aceptable si es la
    # única página necesaria; en textos largos favorecemos 2+2 frente a 3+1.
    best={n:((0,0,0,0,0,0),())}
    for i in range(n-1,-1,-1):
        winner=None
        def visit(pos,lines,singletons,ragged):
            nonlocal winner
            if lines:
                suffix,pages=best[pos]
                page_cost=(1,len(lines),int(pos-i==1),
                           int(len(lines)==1),singletons,ragged)
                cost=tuple(a+b for a,b in zip(page_cost,suffix))
                candidate=(cost,(tuple(lines),)+pages)
                if winner is None or cost<winner[0]:winner=candidate
            if pos==n or len(lines)==rows:return
            for end,length in opts[pos]:
                # Raggedness is only a tie-breaker; no extra lines to fill space.
                visit(end,lines+[(pos,end)],
                      singletons+int(end-pos==1),ragged+(limit-length)**2)
        visit(i,[],0,0)
        if winner is None:raise ValueError('No se pudo paginar')
        best[i]=winner
    pages=tuple(tuple(tuple(words[a:b]) for a,b in page) for page in best[0][1])
    if tuple(w for page in pages for line in page for w in line)!=words:
        raise ValueError('Paginación perdió contenido')
    return pages

def paginate_text(text, encoder, limit=28, rows=3):
    if any(c in text for c in '\0\n\r\t'):
        raise ValueError('Control editorial pendiente')
    words=text.split(' ')
    if any(not w for w in words):raise ValueError('Espaciado estructurado')
    sizes=[len(encoder(w)) for w in words]
    if any(s%2 for s in sizes):raise ValueError('Texto no codificado en pares')
    if len(encoder(' '))!=2:raise ValueError('Espacio TALK inesperado')
    pages=paginate_words(words,[s//2 for s in sizes],limit,rows)
    result=tuple(tuple(' '.join(line) for line in page) for page in pages)
    if ' '.join(l for p in result for l in p)!=text:
        raise ValueError('Reflujo perdió texto')
    for p in result:
        if len(p)>rows or any(len(encoder(l))>2*limit for l in p):
            raise ValueError('Reflujo excedió capacidad')
    return result
