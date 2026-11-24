"""ISO9660 sintéticas creadas aquí; no contienen datos comerciales."""
import hashlib
import struct
import tempfile
import unittest
from pathlib import Path
from verificar_iso_aislamiento import ISOIsolationError, inventory, verify, BLOCK

def record(name,lba,size,isdir=False):
    n=name if isinstance(name,bytes) else name.encode("ascii")
    length=33+len(n)+(len(n)%2==0)
    r=bytearray(length);r[0]=length
    struct.pack_into("<I",r,2,lba);struct.pack_into(">I",r,6,lba)
    struct.pack_into("<I",r,10,size);struct.pack_into(">I",r,14,size)
    r[25]=2 if isdir else 0
    struct.pack_into("<H",r,28,1);struct.pack_into(">H",r,30,1)
    r[32]=len(n);r[33:33+len(n)]=n
    return bytes(r)

def iso(first=b"AAA",second=b"BBB",first_lba=21,second_lba=22):
    raw=bytearray(27*BLOCK)
    raw[16*BLOCK:16*BLOCK+7]=b"\x01CD001\x01"
    raw[16*BLOCK+156:16*BLOCK+190]=record(b"\0",20,BLOCK,True)
    directory=record(b"\0",20,BLOCK,True)+record(b"\1",20,BLOCK,True)
    directory+=record("A.BIN;1",first_lba,len(first))+record("B.BIN;1",second_lba,len(second))
    raw[20*BLOCK:20*BLOCK+len(directory)]=directory
    raw[first_lba*BLOCK:first_lba*BLOCK+len(first)]=first
    raw[second_lba*BLOCK:second_lba*BLOCK+len(second)]=second
    return bytes(raw)

class IsolationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.p=Path(self.tmp.name)/"a.iso"
        self.q=Path(self.tmp.name)/"b.iso"
        self.p.write_bytes(iso())
    def tearDown(self):self.tmp.cleanup()
    def test_iso_igual_sintetica(self):
        self.q.write_bytes(iso())
        result=verify(self.p,self.q)
        self.assertEqual(result["archivos_comparados"],2)
        self.assertEqual(result["recursos_idénticos"],2)
    def test_mover_sector_sin_cambiar_contenido_no_rompe(self):
        self.q.write_bytes(iso(first_lba=23,second_lba=25))
        self.assertEqual(verify(self.p,self.q)["recursos_idénticos"],2)
    def test_prohibir_texto_no_autorizado(self):
        self.q.write_bytes(iso(first=b"XXA"))
        with self.assertRaises(ISOIsolationError):verify(self.p,self.q)
    def test_permitir_solo_archivo_fijado_por_hash(self):
        self.q.write_bytes(iso(first=b"XXXX"))
        source=hashlib.sha256(b"AAA").hexdigest()
        report=verify(self.p,self.q,{"A.BIN":source})
        self.assertEqual([x["recurso"] for x in report["recursos_modificados_autorizados"]],["A.BIN"])
        with self.assertRaises(ISOIsolationError):verify(self.p,self.q,{"A.BIN":"0"*64})
        with self.assertRaises(ISOIsolationError):verify(self.p,self.q,{"OTHER.BIN":source})
    def test_prohibir_modificacion_de_segundo_recurso(self):
        self.q.write_bytes(iso(first=b"XXA",second=b"ZZZ"))
        with self.assertRaises(ISOIsolationError):verify(self.p,self.q,{"A.BIN":hashlib.sha256(b"AAA").hexdigest()})
    def test_detectar_fichero_fuera_limites(self):
        bad=bytearray(iso());index=20*BLOCK+34+34+40  # cuarto registro B.BIN;1
        self.assertEqual(bad[index],40)
        struct.pack_into("<I",bad,index+2,200)
        struct.pack_into(">I",bad,index+6,200)
        self.q.write_bytes(bad)
        with self.assertRaises(ISOIsolationError):inventory(self.q)
    def test_rechazar_pvd_corrupto(self):
        bad=bytearray(iso());bad[16*BLOCK:16*BLOCK+7]=b"INVALID";self.q.write_bytes(bad)
        with self.assertRaises(ISOIsolationError):inventory(self.q)
if __name__=="__main__":unittest.main()
