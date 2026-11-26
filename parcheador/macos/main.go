package main

import (
 "archive/zip"
 "bytes"
 "compress/gzip"
 "crypto/sha256"
 "encoding/binary"
 "encoding/hex"
 "errors"
 "fmt"
 "hash/crc32"
 "io"
 "os"
 "os/exec"
 "path/filepath"
 "strings"
)

const maxDelta = 128*1024*1024
const isoHash = "4360707b251a0f7776a222512926f1f58fb47bda0060b667168de8a1e122e9f5"
const exeHash = "bd07d3d385f3b781d7b2cf4c7ecd6e92869aaea91ed1df8277bbccf233554089"
type component struct { name, src, dst string }
var iso = component{"La_Pucelle_Ragnarok_ES.iso",isoHash,"fc2c8b08f29ef8a0eb4b09b89010496fb382ef96a0976b87b75e75623646aece"}
var dlcs = []component{
 {"DL_JP_00.EDAT","723720fb885a092d1adb71b7ca24b90b6b03e828460669edb662ae6f38dfef00","994e358898ed859b422a325bdddbe8ef5fbc127e11432acba2d46469140fcad8"},
 {"DL_JP_01.EDAT","fc2bcc6cdb9ff84d0a365b1f873e12d7d4546b5215a165473eb292a8d72ce17d","3e0294cf562c22c116e70465d5463749a27ae07a5a53d21e486f137b9265f04d"},
 {"DL_JP_02.EDAT","bd88a3409a1d78b810ff1a07f1eb0d4ded05b9056bea874e720dbdca64bc329e","8120a819706018e9c8c1bfeb9877f2d1bb6b748087472fe67ba19f54735f40ba"},
 {"DL_JP_03.EDAT","bb879fc608d42e326f41d1e460f97a6beacf6ead86b5734e2c200e515847175e","072bdb7a54c39ec020f7c600f13036755a4a6e8b616530119e1139d65282b385"},
}
func digest(b []byte) string { a:=sha256.Sum256(b); return hex.EncodeToString(a[:]) }
func valid(p []byte) bool {return len(p)>=16 && string(p[:4])=="BPS1" && crc32.ChecksumIEEE(p[:len(p)-4])==binary.LittleEndian.Uint32(p[len(p)-4:])}
func collect(b []byte, out *[][]byte, depth int) {
 if depth>3 || len(b)>maxDelta {return}
 if valid(b) {*out=append(*out,b);return}
 if z,e:=zip.NewReader(bytes.NewReader(b),int64(len(b))); e==nil {
  for _,f:=range z.File { if f.UncompressedSize64>maxDelta || f.FileInfo().IsDir(){continue}; r,e:=f.Open(); if e!=nil{continue}; x,e:=io.ReadAll(io.LimitReader(r,maxDelta+1));r.Close();if e==nil{collect(x,out,depth+1)} }
  return
 }
 // Gzip streams embedded by the Windows Go patcher. Only scan the verified EXE
 // or a file beginning with the gzip signature. Reject unrelated executables.
 if len(b)>=2 && string(b[:2])=="MZ" && digest(b)!=exeHash{return}
 if len(b)<3 || (string(b[:2])!="MZ" && !bytes.Equal(b[:3],[]byte{31,139,8})){return}
 for pos:=0;pos<len(b)-2; {
  i:=bytes.Index(b[pos:],[]byte{31,139,8});if i<0{break};i+=pos;pos=i+3
  g,e:=gzip.NewReader(bytes.NewReader(b[i:]));if e!=nil{continue};g.Multistream(false)
  x,e:=io.ReadAll(io.LimitReader(g,maxDelta+1));g.Close()
  if e==nil && valid(x){*out=append(*out,x)}
 }
}
type decoder struct { p []byte; i,end int }
func (d *decoder) num()(int,error){
 v,shift:=uint64(0),uint64(1)
 for {if d.i>=d.end || shift>1<<49{return 0,errors.New("Varint BPS inválido")};x:=d.p[d.i];d.i++;v+=uint64(x&127)*shift;if x&128!=0{return int(v),nil};shift<<=7;v+=shift}
}
func (d *decoder) signed()(int,error){v,e:=d.num();if v&1!=0{return -(v>>1),e};return v>>1,e}
func apply(src,p []byte)([]byte,error){
 if !valid(p){return nil,errors.New("CRC BPS inválido")}
 end:=len(p)-12; if crc32.ChecksumIEEE(src)!=binary.LittleEndian.Uint32(p[end:]){return nil,errors.New("CRC original incorrecto")}
 d:=decoder{p,4,end};n,e:=d.num();if e!=nil||n!=len(src){return nil,errors.New("Tamaño original incorrecto")};size,e:=d.num();if e!=nil||size<=0||size>1024*1024*1024{return nil,errors.New("Tamaño destino inválido")}
 m,e:=d.num();if e!=nil||m>d.end-d.i{return nil,errors.New("Metadatos inválidos")};d.i+=m
 dst:=make([]byte,size);pos,s,t:=0,0,0
 for pos<size {
  c,e:=d.num();if e!=nil{return nil,e};n:=(c>>2)+1;if n>size-pos{return nil,errors.New("Desbordamiento BPS")}
  switch c&3{
  case 0: if pos>len(src)||n>len(src)-pos{return nil,errors.New("SourceRead inválido")};copy(dst[pos:pos+n],src[pos:pos+n])
  case 1: if n>d.end-d.i{return nil,errors.New("Literal truncado")};copy(dst[pos:pos+n],p[d.i:d.i+n]);d.i+=n
  case 2: x,e:=d.signed();if e!=nil{return nil,e};s+=x;if s<0||s>len(src)||n>len(src)-s{return nil,errors.New("SourceCopy inválido")};copy(dst[pos:pos+n],src[s:s+n]);s+=n
  case 3: x,e:=d.signed();if e!=nil{return nil,e};t+=x;if t<0||t>=pos{return nil,errors.New("TargetCopy inválido")};for k:=0;k<n;k++{dst[pos+k]=dst[t+k]};t+=n
  };pos+=n
 }
 if d.i!=end||crc32.ChecksumIEEE(dst)!=binary.LittleEndian.Uint32(p[end+4:]){return nil,errors.New("CRC destino incorrecto")}
 return dst,nil
}
func patch(path,dir string,c component,ps [][]byte) error {
 if st,e:=os.Stat(path);e!=nil||st.Size()>1024*1024*1024{return fmt.Errorf("Original ausente o demasiado grande: %s",path)}
 b,e:=os.ReadFile(path);if e!=nil{return e};if digest(b)!=c.src{return fmt.Errorf("SHA256 original incompatible: %s",path)}
 crc:=crc32.ChecksumIEEE(b)
 for _,p:=range ps {
  if crc!=binary.LittleEndian.Uint32(p[len(p)-12:]){continue}
  dst,e:=apply(b,p);if e!=nil||digest(dst)!=c.dst{continue}
  final:=filepath.Join(dir,c.name)
  if _,e:=os.Lstat(final);!os.IsNotExist(e){return fmt.Errorf("Salida existente; no se sobrescribe: %s",final)}
  f,e:=os.CreateTemp(dir,".LaPucelle-*.part");if e!=nil{return e};temp:=f.Name();defer os.Remove(temp)
  _,e=f.Write(dst);ce:=f.Close();if e!=nil{return e};if ce!=nil{return ce}
  chk,e:=os.ReadFile(temp);if e!=nil||digest(chk)!=c.dst{return errors.New("Falló relectura SHA256")}
  // Link creates the final filename atomically and refuses to overwrite.
  if e=os.Link(temp,final);e!=nil{return e}
  return nil
 }
 return fmt.Errorf("No se encontró un delta RC024 autenticado para %s",c.name)
}
func dialog(script string,args ...string)(string,error){
 a:=append([]string{"-e","on run argv", "-e",script,"-e","end run","--"},args...)
 b,e:=exec.Command("/usr/bin/osascript",a...).Output();return strings.TrimSpace(string(b)),e
}
func msg(s string){dialog("display dialog (item 1 of argv) with title \"La Pucelle ES RC-024\" buttons {\"Aceptar\"} default button 1",s)}
func chooseFile(prompt string)(string,error){return dialog("return POSIX path of (choose file with prompt (item 1 of argv))",prompt)}
func chooseDir(prompt string)(string,error){return dialog("return POSIX path of (choose folder with prompt (item 1 of argv))",prompt)}
func gui() error{
 path,e:=os.Executable();if e!=nil{return e};packagePath:=filepath.Join(filepath.Dir(path),"../Resources/RC024.zip")
 if _,e:=os.Stat(packagePath);e!=nil{packagePath,e=chooseFile("Selecciona el ZIP acumulativo RC-024 (o su EXE original).");if e!=nil{return nil}}
 st,e:=os.Stat(packagePath);if e!=nil||st.Size()>maxDelta{return errors.New("Paquete inválido")}
 data,e:=os.ReadFile(packagePath);if e!=nil{return e}
 var ps [][]byte;collect(data,&ps,0);if len(ps)==0{return errors.New("No se recuperaron deltas BPS del paquete. No se ha modificado ningún archivo.")}
 mode,e:=dialog("set a to choose from list {\"ISO\", \"DLC\", \"ISO y DLC\"} with prompt \"Selecciona los componentes\" default items {\"ISO\"}\nif a is false then return \"\"\nreturn item 1 of a");if e!=nil||mode==""{return nil}
 var notes []string
 if mode=="ISO"||mode=="ISO y DLC"{
  if input,e:=chooseFile("ISO original v1.1.2 de La Pucelle");e==nil{
   if output,e:=chooseDir("Carpeta de destino de la ISO española");e==nil{
    if e:=patch(input,output,iso,ps);e!=nil{notes=append(notes,"ISO: "+e.Error())}else{notes=append(notes,"ISO: verificada por SHA256")}
   }
  }
 }
 if mode=="DLC"||mode=="ISO y DLC"{
  if input,e:=chooseDir("Carpeta ULJS00244 con DLC originales");e==nil{
   if output,e:=chooseDir("Carpeta de destino para ULJS00244");e==nil{
    output=filepath.Join(output,"ULJS00244");if e:=os.MkdirAll(output,0755);e!=nil{return e}
    for _,c:=range dlcs{p:=filepath.Join(input,c.name);if _,e:=os.Stat(p);os.IsNotExist(e){notes=append(notes,c.name+": no disponible");continue};if e:=patch(p,output,c,ps);e!=nil{notes=append(notes,c.name+": "+e.Error())}else{notes=append(notes,c.name+": verificado")}}
   }
  }
 }
 if len(notes)==0{msg("No se aplicaron componentes.")}else{msg(strings.Join(notes,"\n"))};return nil
}
func main(){
 if len(os.Args)==2&&os.Args[1]=="--version"{fmt.Println("La Pucelle RC-024 macOS - motor preliminar");return}
 if e:=gui();e!=nil{msg(e.Error());os.Exit(1)}
}
