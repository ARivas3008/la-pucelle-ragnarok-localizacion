package main

import (
	"bytes"
	"compress/gzip"
	"encoding/binary"
	"testing"
)

func stream(op byte, off uint64, n uint32, lit string) []byte {
	b := new(bytes.Buffer)
	b.WriteString("LPCOPY01")
	b.WriteByte(op)
	if op == 1 {
		binary.Write(b, binary.LittleEndian, off)
	}
	binary.Write(b, binary.LittleEndian, n)
	b.WriteString(lit)
	b.WriteByte(0)
	return b.Bytes()
}
func TestCompact(t *testing.T) {
	for _, c := range []struct {
		name string
		p    []byte
		size int64
		want string
		fail bool
	}{
		{"copy", stream(1, 2, 4, ""), 4, "cdef", false}, {"literal", stream(2, 0, 3, "xyz"), 3, "xyz", false}, {"bad source", stream(1, 5, 4, ""), 4, "", true}, {"bad target", stream(1, 0, 4, ""), 3, "", true}, {"bad op", stream(7, 0, 1, ""), 1, "", true}, {"zero len", stream(2, 0, 0, ""), 0, "", true}, {"short", stream(2, 0, 4, "x"), 4, "", true}, {"trailing", append(stream(2, 0, 1, "x"), 1), 1, "", true}, {"short target", stream(2, 0, 1, "x"), 2, "", true},
	} {
		t.Run(c.name, func(t *testing.T) {
			var b bytes.Buffer
			e := decodeCompact(bytes.NewReader(c.p), bytes.NewReader([]byte("abcdef")), &b, 6, c.size)
			if (e != nil) != c.fail || (!c.fail && b.String() != c.want) {
				t.Fatalf("%v %q", e, b.String())
			}
		})
	}
}
func TestCRC(t *testing.T) {
	var b bytes.Buffer
	z := gzip.NewWriter(&b)
	z.Write(stream(2, 0, 1, "x"))
	z.Close()
	p := b.Bytes()
	p[len(p)-8] ^= 1
	r, e := gzip.NewReader(bytes.NewReader(p))
	if e != nil {
		t.Fatal(e)
	}
	if decodeCompact(r, bytes.NewReader(nil), new(bytes.Buffer), 0, 1) == nil {
		t.Fatal("CRC not rejected")
	}
}
