import tempfile,struct,zlib,mmap
from pathlib import Path
from generar_bps_mac_piloto import BPS,num,sign,apply,encode

def patch(src, dst, actions):
    p=bytearray(b'BPS1'+num(len(src))+num(len(dst))+num(3)+b'abc'+actions)
    p+=struct.pack('<II',zlib.crc32(src),zlib.crc32(dst))
    p+=struct.pack('<I',zlib.crc32(p))
    return p
def cmd(mode,n):return num(((n-1)<<2)|mode)

src=b'abcdefgh'
dst=b'abXYZfghabXYZfgh'
actions=cmd(0,2)+cmd(1,3)+b'XYZ'+cmd(2,3)+sign(5)+cmd(3,8)+sign(0)
p=patch(src,dst,actions)
assert list(BPS(p).actions())==[(0,0,2,0),(1,2,3,12),(2,5,3,5),(3,8,8,0)]
with tempfile.TemporaryDirectory() as d:
    path=Path(d)/'out'
    apply(p,src,path)
    assert path.read_bytes()==dst
    edited=bytearray(dst);edited[3]=ord('!');edited[10]=ord('?')
    new=encode(p,edited,[(3,4),(10,11)])
    apply(new,src,path)
    assert path.read_bytes()==edited
    # Reuse source/target copy after prior command turned into a literal.
    original=b'abcdabcdabcdabcd'
    q=patch(src,original,cmd(2,4)+sign(0)+cmd(3,12)+sign(0))
    apply(q,src,path)
    assert path.read_bytes()==original
    changed=bytearray(original);changed[0]=ord('Z')
    apply(encode(q,changed,[(0,1)]),src,path)
    assert path.read_bytes()==changed
print('BPS synthetic tests passed')
