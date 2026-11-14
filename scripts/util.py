import csv, hashlib, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
STATES={'pendiente','en_revision','revisado','requiere_investigacion'}
# Protege controles explícitos, etiquetas y marcadores de nombres ocultos; no obliga a conservar la puntuación ordinaria.
REGEX=re.compile(r'<[^<>\r\n]+>|\{\{[^{}\r\n]+\}\}|\{[A-Za-z_0-9:.+-]+\}|\\[nrt]|%\d*\$?[-+0 #]*\d*(?:\.\d+)?[sdifuxX]|\$[A-Za-z_][A-Za-z_0-9]*|[?？]{4,}|ェD|¥')

def marker_list(text):
    t=str(text or '')
    return REGEX.findall(t)+['<SALTO_REAL>']*(t.count('\n'))

def load(path):
    with (ROOT/path).open('r',encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

def fingerprint(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def esc_excel(text):
    text=str(text or '')
    return "'"+text if text.lstrip().startswith(('=','+','-','@')) else text
