import struct
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from integrar_scripts_v014 import plan
from contenedores import entradas_dat,reconstruir_dat

def fixture():
    chunks=[('script00.dat',b'S'*64),('sys3.txp',b'T'*32),('waku.txp',b'W'*16)]
    out=bytearray(16+32*len(chunks));struct.pack_into('<I',out,0,len(chunks))
    end=0
    for i,(name,blob) in enumerate(chunks):
        end+=len(blob);loc=16+32*i
        struct.pack_into('<I',out,loc,end)
        out[loc+4:loc+4+len(name)]=name.encode()
        out+=blob
    return bytes(out)

class TestAlignment(unittest.TestCase):
    def test_crecimiento_38_preserva_alineacion_y_texturas(self):
        old=fixture();new=reconstruir_dat(old,{'script00.dat':b'S'*102})
        rows=entradas_dat(new)
        self.assertTrue(all(s%16==0 and e%16==0 for _,s,e,_ in rows))
        payload={n:new[s:e] for n,s,e,_ in rows}
        self.assertEqual(payload['script00.dat'],b'S'*102+b'\0'*10)
        self.assertEqual(payload['sys3.txp'],b'T'*32)
        self.assertEqual(payload['waku.txp'],b'W'*16)

    def test_identidad_no_reempaqueta(self):
        old=fixture()
        self.assertEqual(reconstruir_dat(old,{}),old)
        self.assertEqual(reconstruir_dat(old,{'script00.dat':b'S'*64}),old)

    def test_ancla_ascii_interior_no_se_inventa(self):
        # El índice 4 apunta a 'l' en hello; antes se redistribuía por proporción.
        raw=struct.pack('<5I',2,0,4,100,101)+b'\x32\x06hello\0'+b'\0'*16
        rows={'ISO_START/script00.dat':[dict(unit_id='1',offset=22,original='hello',
              es_revisado='Hola, mundo entero',estado_editorial='revisado')]}
        changed,result,counts=plan(rows,{'ISO_START/script00.dat':raw})
        self.assertEqual(changed,{})
        self.assertEqual(counts['REFERENCIA_INTERIOR_NO_VERIFICADA'],1)

if __name__=='__main__':unittest.main()
