import sys,struct,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from fuentes_es import *
from fontb_manual import *
class ManualFontBTest(unittest.TestCase):
    def fixture(self,dlc=False):
        fnt=[0]*META_COUNT;ftd=fnt.copy();fnt[0]=ftd[0]=META_COUNT-1
        for c,g in EXPECTED.items():fnt[index_sjis(bytes.fromhex(c))]=74 if dlc and c=='3F' else g
        raw=[]
        for page in range(2):
            b=bytearray(TXP_SIZE);b[:4]=b'\x00\x02\x00\x02'
            for i,a in enumerate(ALPHA):b[16+i*4:20+i*4]=bytes([255,255,255,a])
            raw.append(bytes(b))
        pix=[unpack_pixels(r) for r in raw]
        for c,source in SOURCES.items():
            gid=fnt[index_sjis(bytes.fromhex(c))]
            h=TILES[source];tile=[[int(v,16) for v in h[i:i+14]] for i in range(0,196,14)]
            if not c.startswith('F'):set_tile(pix,gid,tile,only_if_empty=False)
        return {'fontB.fnt':struct.pack('<11616H',*fnt),'fontB.ftd':struct.pack('<11616H',*ftd),
                **{n:pack_pixels(r,p) for n,r,p in zip(NAMES,raw,pix)}}
    def test_manual(self):
        for dlc in (False,True):
            m=self.fixture(dlc);tables=[m[n] for n in ('fontB.fnt','fontB.ftd')]
            a=apply_manual(m)
            self.assertEqual(a['celdas'],17 if dlc else 18)
            self.assertTrue(any(r['pixels_changed'] for r in a['glifos']))
            self.assertEqual(tables,[m[n] for n in ('fontB.fnt','fontB.ftd')])
            self.assertTrue(all(not r['pixels_changed'] for r in apply_manual(m)['glifos']))
    def test_conflict_is_atomic(self):
        m=self.fixture();f=list(struct.unpack('<11616H',m['fontB.fnt']))
        f[index_sjis(b'b')]=2431;m['fontB.fnt']=struct.pack('<11616H',*f);old=dict(m)
        with self.assertRaises(FontError):apply_manual(m)
        self.assertEqual(m,old)
if __name__=='__main__':unittest.main()
