"""Seguridad del selector talk 0x14/0xFD, fixtures sintéticos (sin EDAT original)."""
import sys
import struct
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from formato_talk import inspect,replace,TalkError

def fake_talk():
    head=struct.pack("<II",1,1)+struct.pack("<II",0,123)+bytes(24)
    a="はい".encode("cp932")
    b="いいえ".encode("cp932")
    tail="次の説明".encode("cp932")
    selector=b"\x14\x02\x01"+a+b"\0\x01"+b+b"\0\xfd"
    return head+selector+b"\x01"+tail+b"\0\x03"

def selector_token(meta):
    return next((t for t in meta["tokens"] if t[2]==0x14),None)

class TestSelectorTalkSeguro(unittest.TestCase):
    def test_inspecta_opciones_y_narracion_por_separado(self):
        d=fake_talk();meta=inspect(d)
        self.assertEqual(meta["n"],1)
        self.assertEqual([x["raw"].decode("cp932") for x in meta["strings"]],["はい","いいえ","次の説明"])
        self.assertEqual([bool(x.get("choice")) for x in meta["strings"]],[True,True,False])
        self.assertIsNotNone(selector_token(meta))
        self.assertEqual(d[selector_token(meta)[1]],1)

    def test_rechaza_recorte_dentro_de_una_opcion(self):
        d=fake_talk();m=inspect(d);choice=m["strings"][0]
        with self.assertRaises(TalkError):
            replace(d,[(choice["offset"],choice["end"]+1,b"\x01"+b"ABC"+b"\0")])
        with self.assertRaises(TalkError):
            replace(d,[(choice["offset"]-1,choice["end"],b"\x01"+b"ABC"+b"\0")])

    def test_sustitucion_de_opcion_completa_preserva_las_otras(self):
        d=fake_talk();m=inspect(d);choice=m["strings"][0]
        a,b=choice["offset"]-1,choice["end"]+1
        new=b"\x01"+"進む".encode("cp932")+b"\0"
        result,journal=replace(d,[(a,b,new)])
        self.assertEqual(len(journal),1)
        self.assertEqual(result[:a],d[:a])
        self.assertEqual(result[a+len(new):],d[b:])
        self.assertEqual([x["raw"].decode("cp932") for x in inspect(result)["strings"]],["進む","いいえ","次の説明"])

    def test_sustitucion_atomica_del_selector_preserva_cabecera(self):
        d=fake_talk();m=inspect(d)
        a,b,op=selector_token(m)
        new=b"\x14\x02\x01"+"続行".encode("cp932")+b"\0\x01"+"中止".encode("cp932")+b"\0\xfd"
        result,journal=replace(d,[(a,b,new)])
        self.assertEqual(len(journal),1)
        self.assertEqual(result[:m["base"]],d[:m["base"]])
        self.assertEqual(result[m["base"]+len(new):],d[b:])
        self.assertEqual([x["raw"].decode("cp932") for x in inspect(result)["strings"]],["続行","中止","次の説明"])

    def test_selector_sin_terminador_se_rechaza(self):
        d=fake_talk();m=inspect(d);a,b,_=selector_token(m)
        bad=d[:b-1]+d[b:]
        with self.assertRaises(TalkError): inspect(bad)

if __name__=="__main__":unittest.main()
