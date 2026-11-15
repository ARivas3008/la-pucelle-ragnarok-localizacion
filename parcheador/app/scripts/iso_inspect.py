import os,sys,struct,csv
SECTOR=2048
class ISO:
 def __init__(self,path):
  self.path=path;self.fp=open(path,'rb');self.fp.seek(SECTOR*16); p=self.fp.read(SECTOR); assert p[1:6]==b'CD001';self.volume=p
 def read(self,offset,size):self.fp.seek(offset);return self.fp.read(size)
 def parse_record(self,raw):
  size=raw[0]; ext=struct.unpack_from('<I',raw,2)[0]; length=struct.unpack_from('<I',raw,10)[0]; flag=raw[25]; nl=raw[32]; name=raw[33:33+nl].decode('ascii','replace');name=name.split(';')[0]
  return dict(name=name,offset=ext*SECTOR,size=length,sector=ext,flags=flag,dir=bool(flag&2))
 def listdir(self,node,level=0):
  data=self.read(node['offset'],node['size']);pos=0; out=[]
  while pos<len(data):
   ln=data[pos]
   if ln==0:pos=((pos//SECTOR)+1)*SECTOR;continue
   rec=self.parse_record(data[pos:pos+ln]);pos+=ln
   if rec['name'] in ('\x00','\x01'):continue
   out.append(rec)
  return out
 def walk(self):
  root=self.parse_record(self.volume[156:]);paths=[]
  def rec(node,prefix):
   for f in self.listdir(node):
    name=prefix+'/'+f['name']; paths.append((name,f['size'],f['offset'],f['dir']))
    if f['dir']:rec(f,name)
  rec(root,'');return paths
if __name__=='__main__':
 p=sys.argv[1];isofile=ISO(p); print('VOLUME',isofile.volume[40:72]);files=isofile.walk();print('TOTAL',len(files),'files',sum(not z[-1] for z in files));
 for path,size,off,dir in files:print(f'{size/1024/1024:9.3f} MiB {off:10} {"DIR" if dir else "FILE"} {path}')
 with open('/mnt/data/iso_inventory.csv','w',newline='') as out:
  w=csv.writer(out);w.writerow(['path','size','offset','is_dir']);w.writerows(files)
