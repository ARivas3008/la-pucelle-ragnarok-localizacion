import struct,unittest
from rc026_reflujo_dialogos import audit,apply,inspect,text_words,control_signature,SPACE
from paginacion_talk import paginate_words,paginate_text
from fuentes_es import encode_es

def encode(s):
    return encode_es(''.join('　' if c==' ' else chr(ord(c)+0xfee0) if 0x21<=ord(c)<=0x7e else c for c in s))
def line(s):return b'\1'+encode(s)+b'\0'
def talk(*entries):
    table=bytearray();body=bytearray()
    for i,e in enumerate(entries):
        table+=struct.pack('<II24s',len(body),1234+i,b'')
        body+=e
    return struct.pack('<II',len(entries),len(entries))+table+body
def words(raw):
    return [w for t in inspect(raw)['strings'] for w in text_words(t['raw'])]

class PaginationTest(unittest.TestCase):
    def test_short_sentence_single_line(self):
        self.assertEqual(paginate_text('Hola mundo',encode),(('Hola mundo',),))
    def test_one_box_two_lines(self):
        text='No sé, ya está. ¿Luego qué haré?'
        pages=paginate_text(text,encode)
        self.assertEqual(len(pages),1)
        self.assertEqual(len(pages[0]),2)
        self.assertEqual(' '.join(pages[0]),text)
    def test_no_orphan_four_lines(self):
        items=['a'*14,'b'*14,'c'*14,'d'*14]
        p=paginate_words(items,[14]*4)
        self.assertEqual(tuple(map(len,p)),(2,2))
    def test_boundaries(self):
        self.assertEqual(paginate_text('x'*28,encode),(('x'*28,),))
        with self.assertRaises(ValueError):paginate_text('x'*29,encode)
        with self.assertRaises(ValueError):paginate_text('a  b',encode)
    def test_preserve_pointers_and_words(self):
        raw=talk(line('No sé, ya está.')+b'\2'+line('¿Luego qué haré?')+b'\xff',
                 line('Otra entrada')+b'\xff')
        a=audit(raw);self.assertEqual(len(a['candidatos']),1)
        c=a['candidatos'][0]
        self.assertEqual(c['metricas_antes']['cuadros'],2)
        self.assertEqual(c['metricas_despues']['cuadros'],1)
        with self.assertRaises(ValueError):apply(raw,a)
        c['aprobado']=True
        new,j=apply(raw,a)
        self.assertEqual(words(raw),words(new))
        self.assertEqual(control_signature(raw,inspect(raw)),control_signature(new,inspect(new)))
        self.assertEqual(raw[44:72],new[44:72])
        self.assertEqual(inspect(new)['n'],2)
        self.assertEqual(inspect(new)['strings'][-1]['raw'],inspect(raw)['strings'][-1]['raw'])
        self.assertLess(len(new),len(raw)+2)
        self.assertEqual(len(audit(new)['candidatos']),0)
        c['sha_antes']='0'*64
        with self.assertRaises(ValueError):apply(raw,a)
    def test_preserve_speaker_control(self):
        raw=talk(line('Hola')+b'\x09\x01\x00'+line('Adiós')+b'\xff')
        self.assertEqual(audit(raw)['candidatos'],[])
    def test_preserve_dynamic_variable(self):
        raw=talk(b'\1A0'+encode('hola')+b'\0\2'+line('Adiós')+b'\xff')
        self.assertEqual(audit(raw)['candidatos'],[])
    def test_preserve_choices(self):
        raw=talk(b'\x14\x02'+line('Sí')+line('No')+b'\xfd\xff')
        self.assertEqual(audit(raw)['candidatos'],[])
if __name__=='__main__':unittest.main()
