"""FontB manual 27/11/2026: celdas exactas del RAR del usuario, sin Pillow."""
import hashlib
import struct
from fuentes_es import FontError,index_sjis,unpack_pixels,pack_pixels,box_for_gid,get_tile,set_tile

ALPHA=(0,17,34,51,68,85,102,119,135,153,170,187,204,221,238,255)
ROWS={
 "8141": "/////////00271/00af7/004ad/0dad/0000001",
 "8144": "///////////0007fb/0007fb/",
 "8163": "//////////0271006400172/0af703fe007fa/04a20097002a4/",
 "8169": "0000006f4/000002e7/000009e1/00000f8/00004f4/00007f/00007f/00007f/00005f3/00002f6/00000cb/000005f4/000000ad1/000000175",
 "F050": "////000000900009/00000e0000f/0000e0000e/000f0000f/00e0000e/000f0000f/0000e0000e/00000e0000f/000000900009/",
 "F051": "////00900009/000e0000e/0000e0000e/00000f0000f/000000e0000e/00000f0000f/0000e0000e/000e0000e/00900009/",
 "F042": "0027f/004f//0028/004f/004f/004f/004f/004f/004f/004f/0014//",
 "F047": "00007f/0000f/002f2/004f4/004f4/004f4/004f4/004f4/004f4/004f4/004f4/0004//001",
 "F040": "00008e/0008e3/000f8/00262/07fff9/0e908f/1438ef/09fd8f/3f704f/6f54df/1dffcf5/0042142//",
 "F041": "00008e/0008e3/000f8/00152/08eef8/2f909f3/6f989f4/7f87872/5f20283/2f918f2/06eff8/00041//",
 "F043": "00008e/0008e3/000f8/00161/08ffe8/5f808f3/7f000f8/8f000f7/7f000f8/5f808f3/08efe8/0014//",
 "F044": "00008e/0008e3/000f8/2800272/4f004f4/4f004f4/4f004f4/4f004f4/4f005f4/4f22bf4/0efeaf4/0041141//",
 "F04A": "00df006/0f24df/040004/28026/4fbffd/4fd24f3/4f600f4/4f100f4/4f000f4/4f000f4/4f000f4/1400041//",
 "F04C": "0fa00fa/40004//2800272/4f004f4/4f004f4/4f004f4/4f004f4/4f005f4/4f22bf4/0efeaf4/0041141//",
 "F04E": "/000db6/000ff7/000442/0006b3/0008f4/000fe1/004f3/06ff0044/3fe00061/7f7444dc/5ffffff9/09b9774/",
 "F04F": "/00bb3/00ff4/00441/0068/00af/00bf/00bf/00bf/00bf/00bf/00bf/0067/",
 "3F": "/04779b9/9ffffff5/cd4447f7/16000ef3/4400ff6/0003f4/001ef/004f8/003b6/00244/007ff/006bd/"
}
TILES={k:''.join(r.ljust(14,'0') for r in v.split('/')) for k,v in ROWS.items()}
SOURCES={**{k:k for k in TILES if k!='8144'},'8148':'3F','8142':'8144'}
EXPECTED={'F040':2417,'F041':2418,'F042':2419,'F043':2420,'F044':2421,
          'F047':2424,'F04A':2427,'F04C':2429,'F04E':2431,'F04F':2432,
          'F050':2433,'F051':2434,'3F':130,'8148':74,'8141':69,
          '8169':84,'8163':81,'8142':70}
NAMES=('FontB0000.txp','FontB0001.txp')
ORIGINAL={
130:('4b608ca11e6e6e57e01e961e4f2d7ed1eed2269ab31262a6ba82ed905a857ca0',),
74:('735700ae2db6562303ce88e0f7e367cbf2466b34fb92e65fa7794aae8124733a','b0013b76069375b59d1978f93eb4454a8b8f245eceb3ca00e7cd1fadb83a323f'),
69:('5d59c0fae9140b685922f56e960b9223a6edcf2f28a6cae60da8ab3b037131ad','5cb22b4d5fe603d587267feaf6b40fa453cb2d8d7c7c757412cc4925c1d5ff01'),
84:('ca454b03854285542f8d66a28bab9a79887d32b132051df707037f1e2afde471','f9221fe7271188a099860b3f57072e96ba76ab7a64d576690f4215c3ba5072ae'),
81:('b02b7ce678f2ce8f10a8d691e1be268d66cdfb8ba45a6623ce33c36126d35dd9','b4c655186ac93b99c193b44e36f2e64c6dba978d0af9d1f9bcfd86adce9bcf7b'),
70:('8db2151b3faa19b33ae15e43bc7d6e6805721f0482dba0d83bf6439808ead10b','1921be91324dd638d96b87c1d2f30d3868d12a226856f966ef3fb47b6ef7e5e3'),
}
def apply_manual(members):
    """Tras add_spanish_fonts; escritura atómica, preserva FNT, FTD y CLUT."""
    fnt=struct.unpack('<11616H',members['fontB.fnt'])
    ftd=struct.unpack('<11616H',members['fontB.ftd'])
    raw=[bytes(members[n]) for n in NAMES]
    before=[unpack_pixels(r) for r in raw]
    after=[bytearray(p) for p in before]
    palettes=[]
    for r in raw:
        values=[r[19+4*i] for i in range(16)]
        if sorted(values)!=list(ALPHA):raise FontError('CLUT manual desconocida')
        palettes.append({v:i for i,v in enumerate(values)})
    plan={}
    for code,source in SOURCES.items():
        ix=index_sjis(bytes.fromhex(code));gid=fnt[ix]
        if gid!=EXPECTED[code] and not (code=='3F' and gid==74):
            raise FontError('GID manual desconocido: '+code)
        page,x,y=box_for_gid(gid)
        flat=[palettes[page][ALPHA[int(d,16)]] for d in TILES[source]]
        if len(flat)!=196:raise FontError('Celda manual inválida')
        tile=[flat[i:i+14] for i in range(0,196,14)]
        if gid in plan:
            if plan[gid]['tile']!=tile:raise FontError('Conflicto alias')
            plan[gid]['codes'].append(code)
        else:plan[gid]={'tile':tile,'codes':[code]}
    allowed=[set(),set()];journal=[]
    for gid,item in plan.items():
        indices={index_sjis(bytes.fromhex(c)) for c in item['codes']}
        if {i for i,v in enumerate(fnt[1:],1) if v==gid}!=indices:
            raise FontError('Alias manual no autorizado: '+str(gid))
        old=get_tile(before,gid);tile=item['tile']
        digest=hashlib.sha256(bytes(v for row in old for v in row)).hexdigest()
        if gid in ORIGINAL and old!=tile and digest not in ORIGINAL[gid]:
            raise FontError('Dibujo original distinto: '+str(gid))
        page,x,y=box_for_gid(gid)
        set_tile(after,gid,tile,only_if_empty=False)
        allowed[page].update((y+dy)*512+x+dx for dy in range(14) for dx in range(14))
        journal.append({'gid':gid,'codes':item['codes'],
                        'ftd':[ftd[index_sjis(bytes.fromhex(c))] for c in item['codes']],
                        'pixels_changed':sum(a!=b for ro,rn in zip(old,tile) for a,b in zip(ro,rn)),
                        'sha256':hashlib.sha256(bytes(v for row in tile for v in row)).hexdigest()})
    result=[pack_pixels(r,p) for r,p in zip(raw,after)]
    for i,r in enumerate(result):
        reread=unpack_pixels(r)
        if len(r)!=len(raw[i]) or r[:1040]!=raw[i][:1040] or reread!=after[i]:
            raise FontError('Regresión de cabecera, CLUT o relectura')
        if any(a!=b and j not in allowed[i] for j,(a,b) in enumerate(zip(before[i],reread))):
            raise FontError('Cambio fuera de celdas autorizadas')
    for n,r in zip(NAMES,result):members[n]=bytearray(r)
    return {'glifos':journal,'celdas':len(journal),'tablas_preservadas':True,
            'paletas_preservadas':True,'ppsspp':False}
