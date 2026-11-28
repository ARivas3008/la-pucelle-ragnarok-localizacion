package main

import (
	"compress/gzip"
	"crypto/sha256"
	"embed"
	"encoding/binary"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"strings"
	"sync/atomic"
)

//go:embed patches/*
var assets embed.FS

const version = "RC041_REV6_BETA02-GUI-NATIVO"

type Config struct {
	ISO    string `json:"iso"`
	DLC    string `json:"dlc"`
	Output string `json:"output"`
	Log    string `json:"log"`
}
type Spec struct {
	Name       string `json:"name"`
	Patch      string `json:"patch"`
	SourceSHA  string `json:"source_sha256"`
	TargetSHA  string `json:"target_sha256"`
	SourceSize int64  `json:"source_size"`
	TargetSize int64  `json:"target_size"`
}
type Manifest struct {
	Version string `json:"version"`
	Scope   string `json:"scope"`
	Specs   []Spec `json:"specs"`
}

var out io.Writer = os.Stdout
var cancelled atomic.Bool
var errCancelled = errors.New("Parcheo cancelado")

func checkCancel() error {
	if cancelled.Load() {
		return errCancelled
	}
	return nil
}

type cancelReader struct{ r io.Reader }

func (r cancelReader) Read(p []byte) (int, error) {
	if e := checkCancel(); e != nil {
		return 0, e
	}
	return r.r.Read(p)
}

func msg(s string, a ...any) { fmt.Fprintf(out, s+"\n", a...) }
func hashFile(f *os.File) (string, error) {
	if _, e := f.Seek(0, 0); e != nil {
		return "", e
	}
	h := sha256.New()
	_, e := io.Copy(h, cancelReader{f})
	return fmt.Sprintf("%x", h.Sum(nil)), e
}
func manifest() (Manifest, error) {
	var m Manifest
	b, e := assets.ReadFile("patches/manifest.json")
	if e == nil {
		e = json.Unmarshal(b, &m)
	}
	return m, e
}
func verifySource(path string, s Spec) error {
	f, e := os.Open(path)
	if e != nil {
		return e
	}
	defer f.Close()
	st, e := f.Stat()
	if e != nil {
		return e
	}
	if st.Size() != s.SourceSize {
		return fmt.Errorf("tamaño original incorrecto: %s", s.Name)
	}
	h, e := hashFile(f)
	if e != nil {
		return e
	}
	if h != s.SourceSHA {
		return fmt.Errorf("SHA-256 original incorrecto: %s (%s)", s.Name, h)
	}
	return nil
}
func apply(src, dst string, s Spec) error {
	f, e := os.Open(src)
	if e != nil {
		return e
	}
	defer f.Close()
	st, e := f.Stat()
	if e != nil {
		return e
	}
	if st.Size() != s.SourceSize {
		return errors.New("tamaño origen distinto")
	}
	h, e := hashFile(f)
	if e != nil {
		return e
	}
	if h != s.SourceSHA {
		return errors.New("SHA origen distinto")
	}
	if _, e = f.Seek(0, 0); e != nil {
		return e
	}
	p, e := assets.Open("patches/" + s.Patch)
	if e != nil {
		return e
	}
	defer p.Close()
	z, e := gzip.NewReader(p)
	if e != nil {
		return e
	}
	defer z.Close()
	head := make([]byte, 8)
	if _, e = io.ReadFull(z, head); e != nil {
		return e
	}
	if string(head) != "LPGUI001" {
		return errors.New("delta inválido")
	}
	o, e := os.OpenFile(dst, os.O_CREATE|os.O_EXCL|os.O_RDWR, 0600)
	if e != nil {
		return e
	}
	good := false
	defer func() {
		o.Close()
		if !good {
			os.Remove(dst)
		}
	}()
	if _, e = io.Copy(o, cancelReader{f}); e != nil {
		return e
	}
	if e = o.Truncate(s.TargetSize); e != nil {
		return e
	}
	var last int64
	b := make([]byte, 65536)
	d := make([]byte, 65536)
	for {
		if e = checkCancel(); e != nil {
			return e
		}
		var offset uint64
		if e = binary.Read(z, binary.LittleEndian, &offset); e != nil {
			return e
		}
		if offset == ^uint64(0) {
			break
		}
		var n uint32
		if e = binary.Read(z, binary.LittleEndian, &n); e != nil {
			return e
		}
		if n == 0 || n > 65536 || offset > uint64(s.TargetSize) || uint64(n) > uint64(s.TargetSize)-offset || int64(offset) < last {
			return errors.New("intervalo delta inválido")
		}
		size := int(n)
		last = int64(offset) + int64(n)
		if _, e = io.ReadFull(z, d[:size]); e != nil {
			return e
		}
		if _, e = o.ReadAt(b[:size], int64(offset)); e != nil {
			return e
		}
		for i := 0; i < size; i++ {
			b[i] ^= d[i]
		}
		if _, e = o.WriteAt(b[:size], int64(offset)); e != nil {
			return e
		}
	}
	if n, e := z.Read(b[:1]); n != 0 || e != io.EOF {
		return errors.New("delta con datos sobrantes o CRC inválido")
	}
	if e = o.Sync(); e != nil {
		return e
	}
	h, e = hashFile(o)
	if e != nil {
		return e
	}
	if h != s.TargetSHA {
		return fmt.Errorf("SHA de salida incorrecto %s", h)
	}
	if e = o.Close(); e != nil {
		return e
	}
	good = true
	msg("Verificado SHA-256: %s", s.Name)
	return nil
}
func run(c Config) error {
	if strings.TrimSpace(c.Output) == "" || (c.ISO == "" && c.DLC == "") {
		return errors.New("Selecciona ISO y/o DLC y una salida")
	}
	m, e := manifest()
	if e != nil {
		return e
	}
	msg("%s | %s", m.Version, m.Scope)
	abs, e := filepath.Abs(c.Output)
	if e != nil {
		return e
	}
	if e = os.MkdirAll(abs, 0755); e != nil {
		return e
	}
	final := filepath.Join(abs, "JUEGO_PARA_PPSSPP_RC041_REV6_BETA02")
	if _, e = os.Lstat(final); !os.IsNotExist(e) {
		return errors.New("La carpeta JUEGO_PARA_PPSSPP_RC041_REV6_BETA02 ya existe; elige otra salida")
	}
	type Job struct {
		src, rel string
		s        Spec
	}
	jobs := []Job{}
	for _, s := range m.Specs {
		if s.Name == "ISO" && c.ISO != "" {
			jobs = append(jobs, Job{c.ISO, "La_Pucelle_Ragnarok_ES_RC041_REV6_BETA02.iso", s})
		} else if strings.HasSuffix(s.Name, ".EDAT") && c.DLC != "" {
			jobs = append(jobs, Job{filepath.Join(c.DLC, s.Name), filepath.Join("ULJS00244", s.Name), s})
		}
	}
	expected := 0
	if c.ISO != "" {
		expected++
	}
	if c.DLC != "" {
		expected += 4
	}
	if len(jobs) != expected {
		return errors.New("manifiesto incompleto")
	}
	for _, j := range jobs {
		msg("Comprobando original: %s", j.s.Name)
		if e = verifySource(j.src, j.s); e != nil {
			return e
		}
	}
	stage, e := os.MkdirTemp(abs, ".rc034-")
	if e != nil {
		return e
	}
	defer os.RemoveAll(stage)
	for _, j := range jobs {
		dst := filepath.Join(stage, j.rel)
		if e = os.MkdirAll(filepath.Dir(dst), 0755); e != nil {
			return e
		}
		msg("Aplicando parche: %s", j.s.Name)
		if e = apply(j.src, dst, j.s); e != nil {
			return e
		}
	}
	// Preserve the optional original DLC metadata verbatim. It is not a patch payload.
	if c.DLC != "" {
		aux := filepath.Join(c.DLC, "PARAM.PBP")
		data, err := os.ReadFile(aux)
		if os.IsNotExist(err) {
			msg("Aviso: PARAM.PBP no encontrado; conserva el original al instalar los DLC.")
		} else if err != nil {
			return err
		} else {
			const expected = "25f4966d083bd683cc92f845863ff5f77a1c744349709579db82b2f73dc2a9e1"
			if fmt.Sprintf("%x", sha256.Sum256(data)) != expected {
				return errors.New("PARAM.PBP no coincide con el paquete DLC de referencia; no se publicaron resultados")
			}
			if err = os.WriteFile(filepath.Join(stage, "ULJS00244", "PARAM.PBP"), data, 0644); err != nil {
				return err
			}
			msg("PARAM.PBP original conservado y verificado SHA-256")
		}
	}
	report, e := assets.ReadFile("patches/informe.json")
	if e != nil {
		return e
	}
	if e = os.WriteFile(filepath.Join(stage, "INFORME_RC041_REV6_BETA02.json"), report, 0644); e != nil {
		return e
	}
	if e = checkCancel(); e != nil {
		return e
	}
	if e = os.Rename(stage, final); e != nil {
		return e
	}
	msg("Proceso terminado: %s", final)
	return nil
}
func main() {
	if len(os.Args) == 1 || (len(os.Args) == 2 && os.Args[1] == "--gui-self-test") {
		if e := launch(); e != nil {
			showError(e.Error())
			os.Exit(1)
		}
		return
	}
	if len(os.Args) == 2 && os.Args[1] == "--self-test" {
		m, e := manifest()
		if e != nil || len(m.Specs) != 5 {
			os.Exit(1)
		}
		for _, s := range m.Specs {
			f, e := assets.Open("patches/" + s.Patch)
			if e != nil {
				os.Exit(1)
			}
			z, e := gzip.NewReader(f)
			if e != nil {
				os.Exit(1)
			}
			_, e = io.Copy(io.Discard, z)
			z.Close()
			f.Close()
			if e != nil {
				os.Exit(1)
			}
		}
		msg("Recursos incrustados verificados")
		return
	}
	var c Config
	var cfg string
	var worker bool
	flag.BoolVar(&worker, "worker", false, "proceso GUI")
	flag.StringVar(&cfg, "config", "", "archivo JSON")
	flag.StringVar(&c.ISO, "iso", "", "ISO original")
	flag.StringVar(&c.DLC, "dlc", "", "DLC originales")
	flag.StringVar(&c.Output, "salida", "", "carpeta destino")
	flag.Parse()
	if worker {
		b, e := os.ReadFile(cfg)
		if e != nil {
			os.Exit(1)
		}
		if e = json.Unmarshal(b, &c); e != nil {
			os.Exit(1)
		}
		f, e := os.OpenFile(c.Log, os.O_CREATE|os.O_WRONLY|os.O_TRUNC, 0600)
		if e != nil {
			os.Exit(1)
		}
		out = f
		defer f.Close()
	}
	if e := run(c); e != nil {
		msg("ERROR: %v", e)
		os.Exit(1)
	}
}
