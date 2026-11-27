import unittest,struct
from editor_dialogos import stripped,variables,wide
from formato_talk import inspect,replace
from fuentes_es import encode_es

class TestEditor(unittest.TestCase):
    def test_talk(self):
        header=struct.pack('<II',1,1)+struct.pack('<II24s',0,123,b'')
        old=header+b'\1'+encode_es(wide('Hola'))+b'\0\2\1'+encode_es(wide('Adios'))+b'\0\xff'
        before=inspect(old);t=before['strings'][0]
        data=encode_es(wide('Buenos dias'))
        new,_=replace(old,[(t['offset']-1,t['end']+1,b'\1'+data+b'\0')])
        after=inspect(new)
        self.assertEqual(stripped(old,before),stripped(new,after))
        self.assertEqual(after['strings'][0]['raw'],data)
        self.assertEqual(after['strings'][1]['raw'],before['strings'][1]['raw'])
    def test_variables(self):
        self.assertEqual(variables(b'A0'+encode_es(wide('Hola'))+b'A9'),('A0','A9'))
        with self.assertRaises(ValueError):variables(b'AB')
if __name__=='__main__':unittest.main()
