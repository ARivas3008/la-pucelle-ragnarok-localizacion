package main
import ("testing";"bytes";"hash/crc32";"encoding/binary";"compress/gzip";"archive/zip")
func number(n int) []byte { var b []byte;for {x:=n&127;n>>=7;if n==0{return append(b,byte(x|128))};b=append(b,byte(x));n--} }
func sample()([]byte,[]byte,[]byte){
 src:=[]byte("abcde");dst:=[]byte("abXYdeYYYY")
 p:=[]byte("BPS1")
 for _,n:=range []int{len(src),len(dst),0,4,5}{p=append(p,number(n)...)}
 p=append(p,'X','Y')
 // SourceCopy 2 bytes from source offset 3, then TargetCopy 4
 // from offset 3 (Y), with overlap after choosing a repeated Y.
 p=append(p,number(6)...);p=append(p,number(6)...)
 // Use literal Y, then copy overlap from its location (offset 6).
 p=append(p,number(1)...);p=append(p,'Y')
 p=append(p,number(11)...);p=append(p,number(12)...)
 for _,n:=range []uint32{crc32.ChecksumIEEE(src),crc32.ChecksumIEEE(dst)}{p=binary.LittleEndian.AppendUint32(p,n)}
 p=binary.LittleEndian.AppendUint32(p,crc32.ChecksumIEEE(p))
 return src,dst,p
}
func TestBPS(t *testing.T){s,w,p:=sample();g,e:=apply(s,p);if e!=nil||!bytes.Equal(g,w){t.Fatalf("result=%q error=%v",g,e)};p[4]^=1;if _,e:=apply(s,p);e==nil{t.Fatal("bad CRC accepted")}}
func TestCollect(t *testing.T){_,_,p:=sample();var a,b bytes.Buffer;g:=gzip.NewWriter(&a);g.Write(p);g.Close();z:=zip.NewWriter(&b);f,_:=z.Create("delta.bps.gz");f.Write(a.Bytes());z.Close();var r [][]byte;collect(b.Bytes(),&r,0);if len(r)!=1||!bytes.Equal(r[0],p){t.Fatal("not recovered")}}
