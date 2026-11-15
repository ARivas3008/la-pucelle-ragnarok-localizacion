#!/usr/bin/env python3
"""Experimental script*.dat relocator (NOT gameplay validated).

Rules verified on source samples:
 * Header: u32 entry_count, entry_count monotonic u32 relative offsets,
   bytecode starts at 4 + count * 4.
 * Text opcode: 0x32, u8 length of text INCLUDING NUL, CP932 text, NUL.
 * Entry offsets move by accumulated byte deltas once after edited bytes.
All other bytecode bytes remain exactly unchanged, but other control-flow
references may exist and are NOT relocated. Do not deploy into a public patch
without inspecting all control instructions and running PPSSPP tests.
"""
from __future__ import annotations
from dataclasses import dataclass
from bisect import bisect_right
import struct

class UnsafeScript(ValueError): pass

@dataclass(frozen=True)
class ScriptEdit:
    offset: int
    before: bytes
    after: bytes

class ScriptTable:
    def __init__(self, raw: bytes):
        self.raw = bytes(raw)
        if len(raw) < 16: raise UnsafeScript('Script too small')
        n = struct.unpack_from('<I', raw, 0)[0]
        if not (1 <= n <= 50000 and 4+4*n < len(raw)):
            raise UnsafeScript('Invalid count or truncated entry table')
        self.count=n
        self.body=4+4*n
        self.pointers=list(struct.unpack_from(f'<{n}I',raw,4))
        limit=len(raw)-self.body
        if self.pointers[0]!=0 or any(x<0 or x>limit for x in self.pointers) or any(a>b for a,b in zip(self.pointers,self.pointers[1:])):
            raise UnsafeScript('Bad or unsorted offsets')

    def check_edit(self,e:ScriptEdit):
        start=e.offset
        if not(e.before and e.after) or b'\x00' in e.before or b'\x00' in e.after:
            raise UnsafeScript('Empty text or embedded NUL')
        if start<self.body+2 or start+len(e.before)>=len(self.raw):
            raise UnsafeScript('Text outside script')
        if self.raw[start-2]!=0x32 or self.raw[start-1]!=len(e.before)+1 or self.raw[start:start+len(e.before)+1]!=e.before+b'\0':
            raise UnsafeScript('Unexpected opcode 0x32, length prefix, text, or terminator')
        if len(e.after)>=255:
            raise UnsafeScript('Updated string exceeds one-byte length field')
        start_rel=start-self.body
        end_rel=start_rel+len(e.before)+1
        j=bisect_right(self.pointers,start_rel)
        if j<len(self.pointers) and self.pointers[j]<end_rel:
            raise UnsafeScript('An entry begins within the replacement string')

    def apply(self,edits:list[ScriptEdit], verify_inverse=True):
        edits=sorted(edits,key=lambda x:x.offset)
        if not edits:return self.raw,[]
        end_before=self.body
        chunks=[];pos=self.body;deltas=[];total=0;new_offsets=[]
        for e in edits:
            self.check_edit(e)
            if e.offset-2<end_before:raise UnsafeScript('Overlapping edits')
            chunks.append(self.raw[pos:e.offset-1]) # leave opcode 0x32 (at offset-2) unchanged
            chunks.append(bytes([len(e.after)+1])+e.after+b'\0')
            new_offsets.append(e.offset+total)
            difference=len(e.after)-len(e.before)
            total+=difference
            deltas.append((e.offset+len(e.before)+1-self.body,total))
            pos=e.offset+len(e.before)+1
            end_before=pos
        chunks.append(self.raw[pos:])
        out=bytearray(self.raw[:self.body] + b''.join(chunks))
        boundaries=[e for e,_ in deltas]
        for i,p in enumerate(self.pointers):
            idx=bisect_right(boundaries,p)-1
            d=deltas[idx][1] if idx>=0 else 0
            v=p+d
            if not 0<=v<=0xffffffff:raise UnsafeScript('u32 offset overflow')
            struct.pack_into('<I',out,4+4*i,v)
        result=bytes(out)
        checked=ScriptTable(result)
        if checked.count!=self.count or len(result)!=len(self.raw)+total:
            raise UnsafeScript('Table parse failure after relocation')
        if verify_inverse:
            inverted=[ScriptEdit(new_off,e.after,e.before) for e,new_off in zip(edits,new_offsets)]
            restored,_=checked.apply(inverted, verify_inverse=False)
            if restored!=self.raw:raise UnsafeScript('Original not recovered bit-for-bit')
        return result,new_offsets
