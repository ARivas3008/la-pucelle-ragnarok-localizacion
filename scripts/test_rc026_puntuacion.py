import sys,struct,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'parcheador/app/scripts'))
from fuentes_es import *

class PunctuationTest(unittest.TestCase):
    def fixture(self):
        fnt=[0]*META_COUNT;ftd=[0]*META_COUNT
        fnt[0]=ftd[0]=META_COUNT-1
        for c,g in [('¿',2431),('¡',2432),('a',10)]:
            i=index_sjis(CODIGOS[c] if c in CODIGOS else b'a')
            fnt[i]=g;ftd[i]=0x700
        raw=bytearray(TXP_SIZE);raw[:4]=b'\x00\x02\x00\x02';raw[79]=255
        raw=bytes(raw)
        atlas=[unpack_pixels(raw),unpack_pixels(raw)]
        for g in (10,2431,2432):
            set_tile(atlas,g,[[15]*14 for _ in range(14)])
        return {'fontB.fnt':struct.pack('<11616H',*fnt),'fontB.ftd':struct.pack('<11616H',*ftd),
                'FontB0000.txp':pack_pixels(raw,atlas[0]),'FontB0001.txp':pack_pixels(raw,atlas[1])}
    def test_masks(self):
        for c in ('¿','¡'):
            t=inverted_punctuation(c)
            self.assertTrue(any(t[0]));self.assertTrue(any(t[1]));self.assertFalse(any(t[2]))
            self.assertTrue(all(not any(row[7:]) for row in t))
            self.assertFalse(any(map(any,t[12:])))
            self.assertEqual(t,spanish_glyph(c,[[0]*14 for _ in range(14)]))
    def test_repair(self):
        m=self.fixture();old=dict(m)
        r=repair_inverted_punctuation(m)
        self.assertEqual(len(r['signos']),2)
        self.assertEqual(m['fontB.fnt'],old['fontB.fnt'])
        self.assertEqual(m['fontB.ftd'],old['fontB.ftd'])
        self.assertEqual(m['FontB0000.txp'],old['FontB0000.txp'])
        self.assertTrue(all(x['changed_pixels'] for x in r['signos']))
        self.assertTrue(all(not x['changed_pixels'] for x in repair_inverted_punctuation(m)['signos']))
    def test_reject_alias(self):
        m=self.fixture();f=list(struct.unpack('<11616H',m['fontB.fnt']))
        f[index_sjis(b'b')]=2431
        m['fontB.fnt']=struct.pack('<11616H',*f);old=dict(m)
        with self.assertRaises(FontError):repair_inverted_punctuation(m)
        self.assertEqual(m,old)

class StartTest(unittest.TestCase):
    def test_lzs_roundtrip(self):
        from rc026_reparar_start import compress
        from nis_formats import lzs_decompress
        import random
        rng=random.Random(26)
        data=[b'',b'a',b'abc'*300,bytes(range(256))*8,
              bytes(rng.randrange(256) for _ in range(4096))]
        for marker in (0,1,127,254,255):
            original=struct.pack('<4sIIB3s',b'DAT\0',0,12,marker,b'\0'*3)
            for d in data:
                with self.subTest(marker=marker,size=len(d)):
                    self.assertEqual(lzs_decompress(compress(d,original),allow_overlap=False),d)
    def test_dat_preservation(self):
        from rc026_reparar_start import repair
        m=PunctuationTest().fixture();m['untouched.dat']=b'example'
        entries=bytearray();payload=bytearray()
        for name,raw in m.items():
            payload+=raw
            entries+=struct.pack('<I28s',len(payload),name.encode('ascii'))
        original=struct.pack('<I12s',len(m),b'')+entries+payload
        updated,journal=repair(original)
        self.assertEqual(len(updated),len(original))
        self.assertEqual(updated[:16+32*len(m)],original[:16+32*len(m)])
        self.assertTrue(updated.endswith(b'example'))
        self.assertEqual(len(journal['signos']),2)
        self.assertEqual(repair(updated)[0],updated)
if __name__=='__main__':unittest.main()

