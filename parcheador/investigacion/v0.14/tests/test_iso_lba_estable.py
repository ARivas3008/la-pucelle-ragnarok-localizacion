"""ISO9660 mínima sintética: verificar posición física LBA preservada."""
import os
import struct
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(Path(__file__).resolve().parents[3]/"v0.10"))
from integrar_scripts_v014 import append_multiple_iso, Peligro
from iso_reubicar import recorrer

SECTOR=2048

def iso_entry(name,lba,length,is_dir=False):
    name=name if isinstance(name,bytes) else name.encode("ascii")
    ln=33+len(name)+(len(name)%2==0)
    buf=bytearray(ln)
    buf[0]=ln
    struct.pack_into("<I",buf,2,lba)
    struct.pack_into(">I",buf,6,lba)
    struct.pack_into("<I",buf,10,length)
    struct.pack_into(">I",buf,14,length)
    buf[25]=2 if is_dir else 0
    struct.pack_into("<H",buf,28,1)
    struct.pack_into(">H",buf,30,1)
    buf[32]=len(name)
    buf[33:33+len(name)]=name
    return bytes(buf)

def build_iso(path):
    raw=bytearray(32*SECTOR)
    pvd=16*SECTOR
    raw[pvd]=1
    raw[pvd+1:pvd+6]=b"CD001"
    raw[pvd+6]=1
    struct.pack_into("<I",raw,pvd+80,32)
    struct.pack_into(">I",raw,pvd+84,32)
    root=iso_entry(b"\x00",20,SECTOR,True)
    raw[pvd+156:pvd+156+len(root)]=root
    structure=[
      (20,iso_entry("PSP_GAME",21,SECTOR,True)),
      (21,iso_entry("USRDIR",22,SECTOR,True)),
      (22,b"".join([
           iso_entry("START_JP.LZS;1",23,800),
           iso_entry("SCRIPTPACK.DAT;1",24,1000),
           iso_entry("BGPACK.DAT;1",25,700),
      ])),
    ]
    for sec,chunk in structure:
        raw[sec*SECTOR:sec*SECTOR+len(chunk)]=chunk
    for sec,fill,cap in ((23,b"S",800),(24,b"P",1000),(25,b"B",700)):
        raw[sec*SECTOR:sec*SECTOR+cap]=fill*cap
    path.write_bytes(raw)

class TestKeepLBA(unittest.TestCase):
 def setUp(self):
    self.tmp=tempfile.TemporaryDirectory()
    self.addCleanup(self.tmp.cleanup)
    self.src=Path(self.tmp.name)/"source.iso"
    self.out=Path(self.tmp.name)/"patched.iso"
    build_iso(self.src)
 def records(self,path):
    with path.open("rb") as fp:
        return {r.ruta:r for r in recorrer(fp)}
 def test_sustitucion_segura_y_bgpack_intacto(self):
    before=self.records(self.src)
    originals=self.src.read_bytes()
    replacement={"/PSP_GAME/USRDIR/START_JP.LZS":b"N"*710,
                 "/PSP_GAME/USRDIR/SCRIPTPACK.DAT":b"Q"*1000}
    append_multiple_iso(self.src,self.out,replacement)
    after=self.records(self.out)
    self.assertEqual(set(before),set(after))
    for key in before:
        self.assertEqual(before[key].offset,after[key].offset,key)
    self.assertEqual(self.src.stat().st_size,self.out.stat().st_size)
    self.assertEqual(before["/PSP_GAME/USRDIR/BGPACK.DAT"].size,
                     after["/PSP_GAME/USRDIR/BGPACK.DAT"].size)
    patched=self.out.read_bytes()
    self.assertEqual(patched[25*SECTOR:25*SECTOR+700], originals[25*SECTOR:25*SECTOR+700])
    self.assertEqual(patched[16*SECTOR:17*SECTOR],originals[16*SECTOR:17*SECTOR])
    self.assertEqual(patched[23*SECTOR:23*SECTOR+710],b"N"*710)
    self.assertEqual(patched[23*SECTOR+710:23*SECTOR+800],b"\0"*90)
    self.assertEqual(patched[24*SECTOR:24*SECTOR+1000],b"Q"*1000)
    self.assertEqual(after["/PSP_GAME/USRDIR/START_JP.LZS"].size,710)
 def test_overflow_falla_sin_escribir_iso(self):
    with self.assertRaisesRegex(Peligro,"reubicar automáticamente"):
        append_multiple_iso(self.src,self.out,{
            "/PSP_GAME/USRDIR/START_JP.LZS":b"X"*801
        })
    self.assertFalse(self.out.exists())
 def test_no_sobrescribe_original(self):
    with self.assertRaises(Peligro):
        append_multiple_iso(self.src,self.src,{
            "/PSP_GAME/USRDIR/START_JP.LZS":b"X"*500
        })

if __name__=="__main__":
 unittest.main()
