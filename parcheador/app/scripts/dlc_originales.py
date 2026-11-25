"""Identificación estricta de los cuatro EDAT aportados para ROM-024.
Las huellas identifican esta edición comprobada contra el manifiesto;
no son una firma del fabricante ni una certificación de ejecución.
"""
import hashlib,struct
from pathlib import Path

SHA_DLC=["723720fb885a092d1adb71b7ca24b90b6b03e828460669edb662ae6f38dfef00","fc2bcc6cdb9ff84d0a365b1f873e12d7d4546b5215a165473eb292a8d72ce17d","bd88a3409a1d78b810ff1a07f1eb0d4ded05b9056bea874e720dbdca64bc329e","bb879fc608d42e326f41d1e460f97a6beacf6ead86b5734e2c200e515847175e"]
SIZE_DLC=(5127190,5203970,5267964,5348846)

def verificar_dlc_originales(carpeta):
    carpeta=Path(carpeta)
    proof={}
    for n,(digest,size) in enumerate(zip(SHA_DLC,SIZE_DLC)):
        p=carpeta/f'DL_JP_{n:02d}.EDAT'
        if not p.is_file():raise ValueError('Falta DLC original: '+p.name)
        b=p.read_bytes()
        actual=hashlib.sha256(b).hexdigest()
        if len(b)!=size or actual!=digest:
            raise ValueError('DLC original no reconocido: '+p.name+' '+actual)
        if b[:8]!=b'NISPACK\0' or struct.unpack_from('<II',b,8)!=(0,1):
            raise ValueError('Cabecera DLC inválida: '+p.name)
        name,off,length,_=struct.unpack_from('<32sIII',b,16)
        if name.rstrip(b'\0')!=b'start_jp.lzs' or off!=2048 or off+length!=len(b):
            raise ValueError('Directorio DLC inválido: '+p.name)
        proof[p.name]={'sha256':actual,'bytes':len(b)}
    return proof
