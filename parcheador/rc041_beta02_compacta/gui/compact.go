package main

import (
	"encoding/binary"
	"errors"
	"io"
)

// LPCOPY01: source-copy and literal commands, gzip wrapped. Source and target
// hashes are checked by apply; the decoder enforces all lengths and EOF/CRC.
func decodeCompact(z io.Reader, src io.ReaderAt, dst io.Writer, sourceSize, targetSize int64) error {
	var head [8]byte
	if _, e := io.ReadFull(z, head[:]); e != nil {
		return e
	}
	if string(head[:]) != "LPCOPY01" {
		return errors.New("delta compacto inválido")
	}
	var written int64
	buf := make([]byte, 65536)
	for {
		if e := checkCancel(); e != nil {
			return e
		}
		var op [1]byte
		if _, e := io.ReadFull(z, op[:]); e != nil {
			return e
		}
		if op[0] == 0 {
			break
		}
		var offset uint64
		if op[0] == 1 {
			if e := binary.Read(z, binary.LittleEndian, &offset); e != nil {
				return e
			}
		} else if op[0] != 2 {
			return errors.New("comando delta desconocido")
		}
		var n uint32
		if e := binary.Read(z, binary.LittleEndian, &n); e != nil {
			return e
		}
		if n == 0 || int64(n) > targetSize-written {
			return errors.New("longitud de destino inválida")
		}
		var r io.Reader = z
		if op[0] == 1 {
			if offset > uint64(sourceSize) || uint64(n) > uint64(sourceSize)-offset {
				return errors.New("intervalo de origen inválido")
			}
			r = io.NewSectionReader(src, int64(offset), int64(n))
		}
		count, e := io.CopyBuffer(dst, cancelReader{io.LimitReader(r, int64(n))}, buf)
		if e != nil {
			return e
		}
		if count != int64(n) {
			return io.ErrUnexpectedEOF
		}
		written += count
	}
	if written != targetSize {
		return errors.New("tamaño de salida incompleto")
	}
	if n, e := z.Read(buf[:1]); n != 0 || e != io.EOF {
		return errors.New("delta con datos sobrantes o CRC inválido")
	}
	return nil
}
