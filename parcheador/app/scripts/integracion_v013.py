"""Inserta abreviaciones verificables de v0.12 sobre COPIAS de los recursos.

Es una extensión de último recurso del motor v0.8: no modifica los corpus,
no desplaza registros, no escribe sobre cambios anteriores y no toca Now Loading.
CABE_ESTRUCTURAL significa *solo* seguridad binaria, no aprobación editorial.
"""
import csv
import re
from collections import Counter
from pathlib import Path
from campos_fijos import capacidad_verificada, ampliar_campo, CampoError
from fuentes_es import encode_es, missing_render_glyphs, FontError

class IntegracionError(ValueError):
    pass


def cargar_propuestas(ruta):
    with Path(ruta).open('r', encoding='utf-8-sig', newline='') as f:
        rows = list(csv.DictReader(f))
    required = {'unit_id', 'grupo_id', 'recurso', 'original', 'es_revisado',
                'propuesta', 'estado_propuesta', 'tipo'}
    if not rows or not required.issubset(rows[0]):
        raise IntegracionError('El CSV de propuestas no contiene las columnas requeridas')
    if len({r['unit_id'] for r in rows}) != len(rows):
        raise IntegracionError('Unidades duplicadas en las propuestas')
    return rows


def ajustar_propuestas(propuestas, ruta):
    """Aplica cuatro reducciones adicionales sin alterar el historial v0.12.

    Rechaza cambios inesperados en las propuestas archivadas y no modifica
    el estado editorial registrado por GitHub.
    """
    if not Path(ruta).is_file():
        raise IntegracionError('Falta el registro de ajustes v0.13')
    with Path(ruta).open(encoding='utf-8-sig', newline='') as f:
        ajustes = list(csv.DictReader(f))
    por_id = {x['unit_id']: dict(x) for x in propuestas}
    if len({x['unit_id'] for x in ajustes}) != len(ajustes):
        raise IntegracionError('Ajustes duplicados')
    for a in ajustes:
        p = por_id.get(a['unit_id'])
        if not p or p['estado_propuesta'] != 'CABE_ESTRUCTURAL' or p['propuesta'] != a['propuesta_anterior']:
            raise IntegracionError('La propuesta histórica ya no coincide: ' + a['unit_id'])
        if not _valido(a['propuesta_v013']):
            raise IntegracionError('Texto propuesto no válido: ' + a['unit_id'])
        p['propuesta'] = a['propuesta_v013']
        p['regla'] = 'ajuste editorial v0.13: ' + a.get('justificacion', '')
    return list(por_id.values())


def _valido(texto):
    return bool(texto and texto.strip() and '\0' not in texto
                and '\r' not in texto and '\n' not in texto and '\t' not in texto
                and not re.search(r'\{[^}]*\}|%[sd]|<[^>]+>', texto))


def _solapa(intervalos, inicio, fin):
    return any(not (fin <= x or inicio >= y) for x, y in intervalos)


def aplicar(propuestas, manifest, resultados, source_buffers, eboot, patch_offsets,
            packs, matching, reviews=None, *, fuentes_activas=True, incluir_no_aprobadas=False):
    """Aplicación determinista, fail-closed, con una entrada de informe por unidad.

    El motor primero aplica las traducciones v0.8. Aquí solo se intentan
    variantes para unidades que SIGUEN bloqueadas, y únicamente si el texto
    previo del manifest coincide tanto con el original como con el registro
    de v0.12. No se alteran fuentes originales en disco.
    """
    idx = {x['unit_id']: x for x in manifest}
    reports = {x['unit_id']: x for x in resultados}
    c = Counter()
    eboot_nuevos = {}
    detalles = []
    aceptables = {'CABE_ESTRUCTURAL'}
    if incluir_no_aprobadas:
        aceptables.add('PROPUESTA_POR_REVISAR')
    for p in sorted(propuestas, key=lambda x: (x['recurso'], int(idx.get(x['unit_id'], {}).get('offset', 0)))):
        uid = p['unit_id']
        if p['estado_propuesta'] not in aceptables:
            continue
        m = idx.get(uid)
        rr = reports.get(uid)
        if not m or not rr:
            c['NO_EN_MANIFIESTO'] += 1
            continue
        if (m['recurso'] != p['recurso'] or m['grupo_id'] != p['grupo_id']
                or m['original'] != p['original']):
            c['NO_COINCIDE_MANIFIESTO'] += 1
            continue
        if reviews is not None and reviews.get(p['grupo_id'], {}).get('es_revisado') != p['es_revisado']:
            c['TRADUCCION_DESACTUALIZADA'] += 1
            continue
        if rr['estado'].startswith('APLICADO') or rr['estado'] == 'SIN_CAMBIO':
            c['YA_MODIFICADO'] += 1
            continue
        # Nunca usar el reemplazo de un grupo editorial diferente o posterior.
        if rr.get('estado_editorial') != 'revisado':
            c['SIN_REVISION_EDITORIAL'] += 1
            continue
        if not _valido(p['propuesta']):
            c['TEXTO_INVALIDO'] += 1
            continue
        if re.search(r'(?i)now\s+loading|読み込み中', p['original'] + p['propuesta']):
            c['NOW_LOADING_PROTEGIDO'] += 1
            continue
        resource = p['recurso']
        off = int(m['offset'])
        pack_key = 'ISO_START' if resource.startswith('ISO_START/') else resource.split('/')[0]
        try:
            if p['tipo'] == 'TABLA_FIJA':
                buf = source_buffers.get(resource)
                if buf is None:
                    raise IntegracionError('Recurso no seleccionado')
                estilo, antiguo = matching(buf, off, m['original'])
                if antiguo is None:
                    raise IntegracionError('Los bytes originales ya no coinciden')
                # Conservación de estilos full-width, si los había.
                texto = p['propuesta']
                if estilo == 'ancho':
                    texto = ''.join(('　' if x == ' ' else '、' if x == ',' else '。' if x == '.' else chr(ord(x)+0xfee0) if 0x21 <= ord(x) <= 0x7e else x) for x in texto)
                nuevo = encode_es(texto) if fuentes_activas else texto.encode('cp932')
                if fuentes_activas:
                    fonts = packs.get(pack_key, {}).get('inner', {})
                    if missing_render_glyphs(texto, fonts):
                        raise IntegracionError('Faltan glifos para el texto abreviado')
                cap = capacidad_verificada(resource, buf, off, len(antiguo))
                if not cap:
                    raise IntegracionError('Campo sin esquema/padding verificado')
                fin = off + cap
                if _solapa(patch_offsets[resource], off, fin):
                    raise IntegracionError('El campo se solapa con una edición previa')
                raw = bytes(buf[off:fin])
                target = ampliar_campo(raw, len(antiguo), nuevo, cap)
                if len(target) != len(raw) or target[-1] != 0:
                    raise IntegracionError('Campo reconstruido inválido')
                buf[off:fin] = target
                patch_offsets[resource].append((off, fin))
                etiqueta = 'APLICADO_REDUCCION_ESTRUCTURAL'
            elif p['tipo'] == 'EBOOT':
                if eboot is None or resource != 'ISO/PSP_GAME/SYSDIR/EBOOT.BIN':
                    raise IntegracionError('EBOOT no seleccionado')
                antiguo = m['original'].encode('ascii')
                nuevo = p['propuesta'].encode('ascii')
                if not antiguo:
                    raise IntegracionError('Fuente EBOOT vacía')
                if off < 0 or off >= len(eboot):
                    raise IntegracionError('Offset EBOOT fuera de rango')
                fin_nul = eboot.find(b'\0', off, min(len(eboot), off + 256))
                if fin_nul < off:
                    raise IntegracionError('EBOOT: no aparece terminador NUL')
                actual = bytes(eboot[off:fin_nul])
                if actual.rstrip(b' ') != antiguo.rstrip(b' '):
                    raise IntegracionError('Fuente EBOOT/terminador no coincide')
                if len(nuevo) > len(actual):
                    raise IntegracionError('El reemplazo EBOOT no cabe')
                fin = fin_nul
                if _solapa(patch_offsets[resource], off, fin):
                    raise IntegracionError('El campo EBOOT se solapa')
                eboot[off:fin] = nuevo.ljust(len(actual), b' ')
                patch_offsets[resource].append((off, fin))
                eboot_nuevos[uid] = (m['original'], p['propuesta'], off)
                etiqueta = 'APLICADO_REDUCCION_EBOOT'
            else:
                raise IntegracionError('Tipo de propuesta desconocido')
        except (IntegracionError, UnicodeError, FontError, CampoError, ValueError) as exc:
            c['RECHAZADO_ESTRUCTURAL'] += 1
            detalles.append({'unit_id': uid, 'estado': 'RECHAZADO', 'motivo': str(exc)})
            continue
        rr['estado'] = etiqueta
        rr['motivo'] = ('Abreviación del informe v0.12; estructura y bytes comprobados; '
                        'requiere QA lingüístico y PPSSPP')
        rr['es_revisado'] = p['propuesta']
        c[etiqueta] += 1
        detalles.append({'unit_id': uid, 'estado': etiqueta,
                         'original': m['original'], 'propuesta': p['propuesta']})
    return {'conteos': dict(c), 'detalles': detalles, 'eboot_cambios': eboot_nuevos}
