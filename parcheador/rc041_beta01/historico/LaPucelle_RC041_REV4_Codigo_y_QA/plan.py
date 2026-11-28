import json,re,collections as c
from pathlib import Path
p=Path('/tmp/rc41text');pending=json.loads((p/'pending.json').read_text());out=[]
# Explicit changes to source English and Japanese phrases; preserve proper names.
eng={'kis.dat':{'Stormbringer':'Portatormentas','Kinoko Jiru':'Caldo de setas'},'magic.dat':{'Cure':'Curación','Blessing':'Bendición','Transformation':'Transformación','Cumulonimbus':'Cumulonimbo','業火':'Fuego infernal','狙った獲物を地獄の業火で攻撃':'Ataca al objetivo con fuego infernal.','Kinoko Jiru':'Caldo de setas','Use spirit power to attack everyone':'Ataca a todos con energía espiritual.','Poison':'Veneno'},'mapinfo.dat':{'Foothills':'Faldas del Monte Tarte'},'char.dat':{'Nosferatu�':'Nosferatu','Hyacinth':'Jacinto','Rafflesian':'Rafflesia','Church':'Iglesia','Boy':'Niño','Girl':'Niña','Woman':'Mujer','Uncle':'Tío','Aunt':'Tía'},'ritem.dat':{'OK':'Aceptable','Ultima':'Última','Demon':'Demonio','Punch':'Puño','Book':'Libro'},'com.dat':{'Confess your sins to character\x02':'Confiesa tus pecados al personaje\x02','X-Rated':'Libro erótico','Surgery':'Cirugía','Cyborg':'Cíborg','Yell':'Gritar','Shoot':'Disparar'},'name.dat':{'Sexy':'Sensual'}}
for i in range(1,5):eng['magic.dat'][f'Move +{i}']=f'Movimiento +{i}'
for i in range(2,7):eng['magic.dat'][f'テスト{i}']=f'Prueba {i}'
for stat in ['HP','SP','ATK','DEF','INT','SPD','HIT','RES']:eng['magic.dat'][f'{stat} Growth +1']=f'Crecimiento {stat} +1'
eng['skill.dat']={f'Jump+{i}':f'Salto +{i}' for i in [2,5,8,11,15,20]}
# Japanese suffixes concatenate with the randomly generated preceding phrase.
suffix={128:', al parecer.',129:', por lo visto.',130:', sin duda.',131:', según lo escrito.',132:', así lo llaman.',133:', según dicen.',134:', muy popular entre las estudiantes.',135:', según la opinión general.',136:', según cuenta la leyenda.',137:', ¡así es!',138:'.',139:', ¿verdad?',140:', esperemos que no.',141:', no tiene ninguna gracia.',142:', pero ¿estará bien?',143:', ¿de verdad?',146:'. Está maldito.',147:'. Potencia insuficiente.',148:'. Producto defectuoso.',149:'. No esperes gran cosa.',150:'. Prototipo.',151:'. Para principiantes.',152:'. De calidad aceptable.',153:'. Mantener refrigerado.',154:'. Anfibio.',155:'. Para uso espacial.',156:'. Sake de primera calidad.',157:'. Bajo en calorías.',158:'. Con hierbas medicinales.',159:'. Modelo inalámbrico.',160:'. Materiales selectos.',161:'. Fácil de limpiar.',162:'. Sin aditivos.',163:'. Contiene soja transgénica.',164:'. De fabricación nacional.',165:'. De cuerpo intenso.',166:'. De cuerpo ligero.',167:'. Ahorra energía.',168:'. ¡Ahora más sabroso!',169:'. 20% más (que el anterior).',170:'. Para aficionados.',171:'. Bastante fuerte.',172:'. Muy valioso.',173:'. Obra maestra.',174:'. Clase S.',175:'. Clase A.',176:'. Clase B.'}
# DLC-specific descriptions and names where JP differs from the English adaptation.
magic_desc={15:'¡Mira qué elegante movimiento de trasero, dood!',16:'¡Pulsar □ repetidamente no permite disparar, dood!',17:'La melodía de la diosa destroza al enemigo.',22:'Destroza al rival con una doble patada sísmica.',23:'Un golpe que hace arrepentirse hasta al demonio.',26:'Invoca a la cría del Señor y ataca en el área.',30:'¡Patadas y puños que aniquilan a un rey demonio!',49:'Golpe a un punto vital; gran daño si acierta.',50:'Golpea con el libro sagrado y reduce atributos.',52:'Milagro intermedio de Alouette: rayo divino.',53:'Milagro supremo de Alouette: luz divina.',54:'Milagro definitivo de Alouette: luz de las diosas.',60:'Dispara balas de fuego y hielo con dos pistolas.',62:'Arma definitiva que destruye hasta dioses demonio.',63:'Arma capaz de aniquilar a reyes demonio.',69:'Espada real que aniquila monstruos.',70:'Técnica real de espada, veloz como el rayo.',71:'Técnica real de espada que derrota dragones.',76:'Técnica real capaz de vencer a reyes demonio.',81:'Aniquila a los del área con la Espada de Aura.',91:'Técnica de espada ideada por un antiguo rey.',92:'¡Combate a los demonios con su propio poder!',93:'Lanza la energía combativa de la espada.',97:'Parte al enemigo en dos, incluso la luna.',99:'Puño divino que derrota a un demonio de un golpe.',102:'El verdadero puño sagrado, fruto de años de rigor.',104:'Puñetazo perfecto que no admite el menor error.',112:'Convoca aliados para disparar flechas potentes.',115:'¡Atraviesa un punto vital con una larga garra!',116:'¡Cuando arde de pasión, su garra se incendia!',117:'¡Cuando se enfurece, su garra invoca meteoritos!',118:'¡Cuando ruge, su garra se carga de electricidad!',119:'¡Cuando grita, su garra se cubre de espinas!',124:'Convoca al escuadrón Chocolat para una carga.',125:'¡Se divide en mini Chocolats para atacar!',126:'¡Ataque combinado legendario de los Chocolat!',128:'Ataca al objetivo con fuego infernal.',129:'Calcina a todos en el área con fuego infernal.',134:'Daña y envenena con líquido tóxico.',135:'Corta al objetivo con toda su fuerza.',136:'Corta a todos en el área con toda su fuerza.',141:'Embelesa al rival con movimientos extraños.',145:'Genera caldo de setas y se cura por completo.',149:'Consume todos los SP y causa gran daño en el área.',151:'Convierte al rival en una bola de pelo al bailar.',165:'Lanza agua para curar a todos en el área.',167:'Causa daño devastador a todos en el área.',177:'Aliento de setas que daña y envenena en el área.',183:'Causa gran daño a todos en el área.',184:'Cura a todos en el área.',186:'Paraliza a todos en el área.',189:'Grito aterrador que mata al objetivo.',191:'Embelesa a todos en el área.',196:'Ataca a todos en el área con energía espiritual.',197:'Aumenta el ataque de todos en el área.',198:'Reduce la defensa de todos en el área.',199:'Daña a todos en el área con un potente puñetazo.',206:'Causa gran daño a todos en el área.',207:'Altera el estado de todos en el área.',224:'Onda de choque que destroza todo.',225:'Los demonios del rey demonio causan estragos.',226:'El poder del rey demonio extingue toda la vida.',279:'Difiere un poco del Tajo del Gran Rey Demonio.',280:'Laharl arroja energía de un rey demonio.',281:'Técnica suprema que corta incluso el espacio.',290:'¡Se convierte en un monstruo espacial!'}
magic_name={'いやしの奇跡':'Milagro curativo','愛の奇跡':'Curación','神の恵み':'Bendición','変身':'Transformación','火蝶封月':'Cumulonimbo','雷影繰打':'Golpe furioso','真・聖拳突き':'Verdad sagrada','ぷりちぃきっす¥':'Besito encantador','漢の生き様ニャ!!':'¡Estilo varonil!','おしりだニャ!':'Ataque de trasero','炎':'Llama','キノコじる':'Caldo de setas','キノコ召喚':'Dios de las setas','ハニ魔王見参':'Señor Hani','魔王玉・愛':'Amor demoníaco','ヒップアタック!':'Ataque de trasero','プリニー連射!':'Ráfaga Prinny','戦女神のラッパ':'Trompeta guerrera'}
for i in range(1,5):magic_name[f'移動+{i}']=f'Movimiento +{i}'
for stat in ['HP','SP','ATK','DEF','INT','SPD','HIT','RES']:magic_name[f'{stat}成長+1']=f'Crecimiento {stat} +1'
for jp,color in zip('赤緑黄青紫水白',['rojo','verde','amarillo','azul','morado','celeste','blanco']):magic_name[jp+'属性UP']='Potenciar '+color
for i in range(2,7):magic_name[f'テスト{i}']=f'Prueba {i}'
# name fragments are separate generated components, with a hard 11-byte limit.
namejp={14:'Jefe',18:'Ministro',19:'Ministro',24:'Sold. raso',31:'Tte.coronel',33:'General',34:'Tte.general',35:'General',61:'Obsesión',62:'De humor',67:'(Risa)',68:'(Risa/ll.)',70:'¿Verdad?',72:'Debe ser',78:'Aprox.',79:'¿Dónde?',82:'¿¡Cómo!?',86:'¿Eh?',88:'¿No?',93:'¿¡Eh!?',94:'¿Qué es?',96:'Tipo',103:'Sala',112:'Revuelta',115:'Pesadilla',118:'Felicidad',122:'Extremo',125:'Hermana',126:'Hermanita',127:'Hermano',128:'Hermanito',130:'Crónica',131:'Alien',133:'Prohibido',134:'Iniciación',137:'Necio',138:'Diario',139:'Informe',143:'¡Persigue!',148:'Amor',152:'Camino a',153:'Al este',154:'Al norte',155:'Al oeste',156:'Al sur',157:'N.º 1',162:'Emperador',183:'Bar',186:'Balneario',187:'Extravag.',188:'Monstruo',191:'Secuela',194:'Alienígena',197:'Vale',199:'También',210:'¿Y si...?',215:'Artesanal',230:'No perdono',232:'Imitación',234:'A todo gas',238:'Exprés',239:'Larga vida',251:'Sin parar',252:'Uno más',255:'A toda costa',258:'A veces',259:'También',264:'Mañana',270:'Fíjate',271:'Aquí también',272:'Otra vez',277:'De vuelta',282:'A estas alturas',283:'Bastante',284:'Más o menos',285:'Quizá',286:'A propósito',288:'A escondidas',289:'Sin duda'}
# Compact exact replacements for long generated names.
namejp.update({255:'A la fuerza',271:'Aquí igual',282:'Ya tarde',288:'En secreto'})
ritem_name={1:'Maldito',5:'Torpe',23:'Somnoliento',44:'Experto',52:'Alienígena',57:'Victoria',69:'Atómico',73:'Estupendo',74:'Monstruo',76:'Colosal',80:'Asombroso',81:'De primera',83:'N.º 1',84:'Dios bélico',87:'Doncella',88:'Demonio',90:'Tajo',92:'Gancho alto',101:'Cuchillo',104:'Bastón',111:'Pantalones',113:'Bandana',116:'Cepillo'}
ritem_desc={6:'Sucio.',33:'Por alguna razón dan ganas de combatir.',37:'Emociona sin saber por qué.',43:'Hecho con tecnología de vanguardia.',46:'Debilita la magia con el poder estelar.',48:'Supuestamente imbuido de poder oscuro.',50:'Parece capaz de causar la muerte.',51:'Parece bastante impresionante.',60:'Tiene un aire de poderes psíquicos.',69:'Intentaron instalarle un reactor, sin éxito.',87:'Utilizado por la Doncella de la Luz.',88:'Desechado por el Gran Rey Demonio.'}
kis={0:'Aumenta el ataque y te da un aire más elegante.',17:'¡El espíritu de un karateka legendario!',22:'Espada maldita, demasiado horrible para contar.',26:'Espada poderosísima que vuelve tonto al usuario.',35:'Arma definitiva con alcance de mil millones de años luz.',80:'Artículo masculino de lujo, rebosante de elegancia.',89:'Artesanía del desierto hecha con cactus.',91:'Pieza legendaria que aumenta mucho los atributos.',97:'Traje de superaleación, el más fuerte del universo.',105:'No luches contra enemigos a mil leguas.',111:'Te vuelve veloz, pero no un ángel.',124:'Emblema del rey demonio más fuerte.',133:'Facilita el crecimiento de HP.',149:'Colócalo y pulsa □ para cambiar la corriente.'}
comname={27:'Libro erótico',34:'Invitar a cenar',52:'Escribir «carne»',53:'Escribir «centro»',57:'Modificar',58:'Robot transformable',59:'Gritar',69:'Cuatro golpes',76:'Disparar'}
comdesc={10:'Deja que te golpee para desahogarse.',14:'Deja que te dé una paliza para desahogarse.',18:'Reconforta al personaje en tu regazo.',35:'Atiende al personaje como a un VIP.',38:'Profundiza el amor en todos los sentidos.',47:'Mejora la resistencia corriendo a toda velocidad.',50:'Mejora la salud con gimnasia.',52:'Le escribes «carne» en la frente.',53:'Le escribes «centro» en la frente.',55:'Presiona puntos vitales para despertar su poder.',57:'Una organización secreta modifica al personaje.',58:'Una organización secreta lo convierte en robot.',70:'Fortalece su espíritu con un retiro intensivo.',71:'Potencia al personaje con una poción sospechosa.',72:'Fortalece su carácter con salsa muy picante.'}
# source row indexes may differ in exclusive DLC attacks; only reuse same-row English if
# the source Japanese was present in DLC00 for that row, and is not an exceptional row.
dlc0={(r['table'],r['row'],r['rel']):r['original'] for r in pending if r['package']=='DLC_00'}
for r in pending:
 k,t,i,rel,x=r['package'],r['table'],r['row'],r['rel'],r['actual'];source=r['original'];target=None;method='traducción directa'
 if k=='ISO_START':
  target=eng.get(t,{}).get(x.strip())
  if t=='ritem.dat' and rel==17 and i in suffix:target=suffix[i]
 else:
  if t=='magic.dat':
   if rel==18:target=magic_name.get(source.strip())
   else:
    if i in magic_desc and (dlc0.get((t,i,rel))==source or i in (15,16,17,224)):
     if i in (15,16,17) and not any(w in source for w in ['シリ','連射','女神の旋律']):target=None
     else:target=magic_desc[i]
  elif t=='kis.dat':
   if rel==21:target=kis.get(i)
   elif source=='10億光年砲':target='Cañón año luz'
   elif source=='超魔王の証':target='Emblema del Diablo'
  elif t=='skill.dat':
   if i==39 and rel==16:target='Bloqueo circular'
   if i==42 and rel==37:target='Recupera HP al final del turno.'
   if i==63 and rel==37:target='Aumenta la potencia de purificación.'
   if rel==16 and source.startswith('ジャンプ'):target='Salto '+source.split('+')[-1].join(['+',''])
  elif t=='ritem.dat':
   if rel==17:target=suffix.get(i) or ritem_desc.get(i)
   else:target=ritem_name.get(i)
  elif t=='name.dat':target=namejp.get(i)
  elif t=='com.dat':target=(comname if rel==0 else comdesc).get(i)
  elif t=='mapinfo.dat':target='Faldas del Monte Tarte' if i==16 else 'Acceso al corazón de Prier' if i==103 else None
  if target is None:
   target=eng.get(t,{}).get(r['base_original'].strip()) if t!='magic.dat' or rel!=40 else None
  if target is None and r['base_actual'] and not re.search('[\u3040-\u30ff\u3400-\u9fff\ufffd]',r['base_actual']) and r['base_original']!=r['base_actual'] and t not in ('name.dat','magic.dat'):
   target=r['base_actual'].strip();method='equivalente inglés/español cotejado'
  if target is None and t=='magic.dat' and rel==40 and r['base_actual'] and r['base_original']!=r['base_actual'] and not re.search('[\u3040-\u30ff\u3400-\u9fff\ufffd]',r['base_actual']):
   if i not in (15,16,17,18,279,280,281,290):target=r['base_actual'].strip();method='equivalente inglés/español cotejado'
  if target is None and t in ('char.dat','kis.dat','skill.dat','magic.dat') and rel!=40:
   if len(r['proposals'])==1:target=r['proposals'][0];method='corpus previo cotejado'
   elif t=='char.dat' and r['base_actual'] and not re.search('[\u3040-\u30ff\u3400-\u9fff\ufffd]',r['base_actual']):target=r['base_actual'];method='nombre equivalente del juego base'
  if target is None and t=='magic.dat' and rel==18 and r['base_actual'] and r['base_original']!=r['base_actual'] and i not in (15,16,17,18):target=r['base_actual'].strip();method='nombre equivalente del juego base'
 # controls must be preserved; use only supported Spanish charset.
 if target is not None:target=target.replace('Calamidad','Calamity').replace('Éclair Oscura','Éclair oscura')
 if target and target!=x:
  r.update(target=target,method=method);out.append(r)
(p/'plan.json').write_text(json.dumps(out,ensure_ascii=False));print(len(out),c.Counter(r['package'] for r in out))
left=[r for r in pending if r not in out];seen=set()
for r in left:
 k=r['table'],r['actual'];
 if k in seen:continue
 seen.add(k);print(r['table'],r['row'],r['rel'],r['actual'],'|',r['base_actual'],'|',r['proposals'])
