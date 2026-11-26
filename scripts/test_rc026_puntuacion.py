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
if __name__=='__main__':unittest.main()
