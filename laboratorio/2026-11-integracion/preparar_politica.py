from pathlib import Path
p=Path(__file__).parent/'fuente/parcheador/app/scripts/construir_parche.py'
s=p.read_text(encoding='utf-8')
for name,style in [('t','style'),('chunk','st'),('chunk','style'),('text','style'),('newtext','style')]:
 s=s.replace(f"to_full({name}) if {style}=='ancho' else {name}",f'texto_destino({name},{style})')
s=s.replace("if len({x[2] for x in desc})!=1:","if not TEXTO_COMPACTO and len({x[2] for x in desc})!=1:")
s=s.replace("if len(styles)!=1:","if not TEXTO_COMPACTO and len(styles)!=1:")
p.write_text(s,encoding='utf-8')
print('Política compacta explícita preparada')
