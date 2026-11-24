"""Regresiones sintéticas: datos no indexados y PVD con layout fijo."""
import hashlib,tempfile,unittest
from pathlib import Path
from test_verificar_iso_aislamiento import iso,BLOCK
from verificar_iso_layout_fijo import verify_fixed,ISOIsolationError

class FixedLayoutTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.a=Path(self.tmp.name)/"a.iso";self.b=Path(self.tmp.name)/"b.iso"
        self.a.write_bytes(iso())
    def tearDown(self):self.tmp.cleanup()
    def test_identity(self):
        self.b.write_bytes(iso())
        self.assertEqual(verify_fixed(self.a,self.b)["bytes_fuera_de_recursos_autorizados_cotejados"],27*BLOCK)
    def test_allowed_exact_member(self):
        self.b.write_bytes(iso(first=b"XYZ"))
        p={"A.BIN":hashlib.sha256(b"AAA").hexdigest()}
        self.assertEqual(verify_fixed(self.a,self.b,p)["bytes_fuera_de_recursos_autorizados_cotejados"],27*BLOCK-3)
    def test_padding_system_area_and_pvd(self):
        for index in (100,16*BLOCK+42,21*BLOCK+9,26*BLOCK+100):
            with self.subTest(offset=index):
                bad=bytearray(iso());bad[index]^=1;self.b.write_bytes(bad)
                with self.assertRaises(ISOIsolationError):verify_fixed(self.a,self.b)
    def test_refuses_relocation(self):
        self.b.write_bytes(iso(first_lba=23))
        with self.assertRaises(ISOIsolationError):verify_fixed(self.a,self.b)
    def test_refuses_growth(self):
        self.b.write_bytes(iso()+bytes(BLOCK))
        with self.assertRaises(ISOIsolationError):verify_fixed(self.a,self.b)
if __name__=="__main__":unittest.main()
