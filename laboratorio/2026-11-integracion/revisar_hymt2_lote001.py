"""Revisión editorial explícita de las primeras 100 propuestas; fuente y modelo conservados."""
from pathlib import Path
import json,sys
B=Path(__file__).resolve().parent
sys.path.insert(0,str(B/'fuente/parcheador/app/scripts'))
from recompilar_talk import wrap
queue=json.loads((B/'informes/cola_hymt2.json').read_text(encoding='utf8'))
correcciones={
0:'¿Me dejan hacer un anuncio antes de terminar? ¡También hay una tienda Rosenqueen en el segundo piso de la tienda principal de Messe Sanoh, en Akihabara, Tokio! ¡Vengan a visitarnos! ￥',
1:'¿Eh? ¿Qué pasa, Prier? ¡Deja de perder el tiempo por aquí y ve a atrapar al culpable de una vez!',
2:'Me han informado de que unos vecinos vieron una luz blanca que era absorbida por la Panza del Diablo. Oye, Prier... ¿De verdad resolviste el caso? ¿Eh? Como descubra que has hecho el trabajo de cualquier manera...',
3:'Sí',4:'No',
5:'Lección de eringués del anciano, segunda parte: «Adiós», eri. En eringués, «adiós» se dice «Asafeianvaoraemoeri», eri.',
6:'Lección de eringués del anciano, tercera parte: «Lo siento», eri. En eringués, «lo siento» se dice «Akorueoangaoweiaeri», eri.',
7:'Última lección de eringués del anciano: «Gracias», eri. En eringués, «gracias» se dice «Weonoaeugagehaoeri», eri.',
8:'Más adelante está el Camino de las Setas, el territorio de los dragones seta, eri. Son increíblemente fuertes, eri. Ni se te ocurra luchar contra ellos, eri. Si quieres adentrarte allí, avanza huyendo de ellos, eri. Y ten cuidado: también hay setas malvadas, eri.',
9:'Nunca he visto a un humano tan fuerte como tú, eri. ¿Acaso eres el legendario Mesías de las Setas, eri...?',
10:'Qué va.',
11:'Gracias a ustedes, los dragones seta ya no salen de su territorio, eri. Pero siguen siendo peligrosos, eri. Es mejor evitar luchar contra ellos, eri.',
12:'Los Eringa terminamos todas las frases con «eri», pero también podemos hablar con normalidad, eri. Lo añadimos porque así somos más adorables, eri. ￥',
13:'Soy el anciano de Grand Champignon, eri... Ya no podemos hacer nada por nuestras propias fuerzas, eri. Quizá los cielos los hayan guiado hasta aquí, eri. Por favor, ayúdennos, eri. Si vuelve la paz a esta tierra, les regalaré un elixir llamado Kinoko Jiru, eri.',
14:'¡Vale! ¡Déjenlo en nuestras manos!',
15:'Gracias a ustedes, la paz ha vuelto a Grand Champignon, eri. En nombre de todo nuestro pueblo, les doy las gracias de corazón, eri.',
16:'¿Les sirvió el Kinoko Jiru, eri?',
17:'Como anciano de Grand Champignon, permíteme decirte algo, eri. ¡Deberías convertirte en Eringa, eri!',
18:'¡¿Eh?!',
19:'El encanto de los Eringa está en este movimiento de arriba abajo, eri.',
20:'Ustedes son el orgullo de los Eringa, eri.',
21:'Mmm... No sé si debería darles las gracias por eso...',
22:'Debe de haber una razón por la que los dragones seta se volvieron violentos, eri. Unos días antes vi una figura sospechosa en el Camino de las Setas, eri. Quizá esa persona tenga algo que ver, eri...',
23:'Su valentía me ha impresionado, eri. ¡Ah, ya sé, eri! Si no te importa, ¿querrías casarte con mi hijo, eri?',
24:'¡A-ah...! ¡Eso sí que no, por favor!',
25:'Qué bien, hermana. Ya has encontrado con quién casarte.',
26:'...Aunque no sea humano.',
27:'Dicen que el Kinoko Jiru está delicioso, eri. ¿Lo has probado alguna vez, eri?',
28:'Ya lo has oído. Cuéntaselo, Prier.',
29:'No sé si será el mejor momento, pero... ¿Quieres comprar algo, miau?',
30:'¿Quieres comprar algo, miau? ...Eso iba a decir, pero lo perdí todo en el ataque de los demonios, miau. Qué pena, miau. Si los hubieran derrotado a todos entonces...',
31:'¿Quieres comprar algo, miau?',
32:'Vamos sin prisas, monya.',
33:'............ (La rara eres tú, hermana...',
34:'¡Q-qué buena pinta! ￥',
36:'Ugh... ¡Solo me tratan como líder en momentos así...!',
37:'Sí, tienes razón... ...Qué lata.',
39:'............ Yo soy yo...',
40:'Los Yattanya se encargarán del Escargot. ¡Nosotros debemos darnos prisa!',
41:'Vamos, Croix. Aún nos queda mucho que investigar en Fátima. ¡Sigamos juntos!',
44:'¡Así se habla! ¡La purificación es muy importante!',
46:'Puedes llamar a los personajes convertidos al combate de inmediato desde el panel base.',
47:'¡Eso es todo! Cuantos más enemigos conviertas, más fuerte será tu ejército.',
48:'Hermana Prier, ¿seguimos adelante?',
50:'En nombre de la Doncella de la Luz, te prohíbo volver a decir «vieja bruja».',
58:'¡No somos soldados imperiales! ¡La guerra ha terminado!',
62:'¿Es tonta o qué?',
63:'Gracias por ayudarme antes. Si no hubieras aparecido, quizá ya estaría en el cielo. Te lo agradezco de corazón.',
67:'¡Ah! ¡Es Prier! Oye, oye... Nosotros... En la Panza del Diablo, esa que está a las afueras de la ciudad... ¡Vimos zombis!',
68:'Unos vecinos dijeron que vieron una luz blanca que era absorbida por la Panza del Diablo. Oye, Prier... ¿Investigaste bien ese lugar? Como te pille holgazaneando...',
69:'¿Un demonio que cambia de forma y arranca el corazón a la gente? Qué caso tan espantoso... Pero no podemos buscar al culpable a ciegas. Para resolverlo, debemos reunir más información.',
71:'Entre los familiares desaparecidos hay desde niños hasta ancianas. No tienen nada en común.',
73:'Que la diosa Poitreene vele por todos ustedes.',
75:'Ugh... Her... H... hermana Prier...',
77:'¿Qué pasa? He venido hasta aquí para ayudarte, ¿y así me recibes?',
78:'¡Reacciona, Culotte! ¡¿Quieres que te traten como a un niño toda la vida?!',
81:'¡¿Los muertos no vuelven a la vida...?!',
82:'¡En nombre de la Doncella de la Luz!',
83:'Yo... Siempre me has protegido, desde que era pequeño.',
85:'Pero siempre tuvo una salud delicada, y poco después de casarnos...',
86:'¡Perderla me destrozó por dentro!',
87:'¡Maldije la enfermedad que se la llevó y maldije a la diosa!',
89:'Dijo que era de la Iglesia de la Divina Madre y que sabía cómo devolverla a la vida.',
93:'He sido un idiota.',
95:'¡Pero le creí!',96:'¡Tenía que creerle!',
98:'Vendí mi alma a aquel hombre a cambio de este cuerpo de demonio.',
99:'Me hice pasar por familiares de otras personas y les robé el corazón...'
}
out=[]
for i,row in enumerate(queue[:100]):
 draft=json.loads((B/'hymt2_borradores'/ (row['id']+'.json')).read_text(encoding='utf8'))
 assert draft['fin']=='stop'
 es=correcciones.get(i,draft['respuesta']).replace('…','...')
 lines=wrap(es)
 if row['opcion']:assert len(lines)==1
 out.append(dict(id=row['id'],original=row['original'],es=es,estado='revisado',procedencia='HY-MT2 local + cotejo editorial de fuente, contexto y glosario',corregido=es!=draft['respuesta'],apariciones=row['apariciones']))
(B/'hymt2_revisados').mkdir(exist_ok=True)
(B/'hymt2_revisados/lote001.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print('Revisados',len(out),'corregidos',sum(r['corregido'] for r in out))
