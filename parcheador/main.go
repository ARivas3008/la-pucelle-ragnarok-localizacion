// La Pucelle Ragnarok - Parcheador con interfaz grafica Windows v0.13.0.
// No contiene el juego, DLC ni recursos comerciales: solo scripts y mapas.
package main

import (
	"archive/tar"
	"archive/zip"
	"bytes"
	"compress/gzip"
	"crypto/sha256"
	"embed"
	"encoding/hex"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"time"
)

//go:embed resources.tar.gz gui.ps1
var resources embed.FS

const version = "0.13.0"
const pythonDownload = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip"
const maxDownload = 35 << 20

func isFile(path string) bool { f, e := os.Stat(path); return e == nil && !f.IsDir() }
func isDir(path string) bool  { f, e := os.Stat(path); return e == nil && f.IsDir() }
func hasDLCS(p string) bool {
	for n := 0; n < 4; n++ {
		if !isFile(filepath.Join(p, fmt.Sprintf("DL_JP_%02d.EDAT", n))) {
			return false
		}
	}
	return true
}
func locateDefaultISO(home string) string {
	roots := []string{home, filepath.Dir(home)}
	for _, root := range roots {
		f, _ := os.ReadDir(root)
		for _, e := range f {
			if !e.IsDir() && strings.HasSuffix(strings.ToLower(e.Name()), ".iso") {
				return filepath.Join(root, e.Name())
			}
		}
	}
	return ""
}
func locateDefaultDLC(home string) string {
	roots := []string{home, filepath.Join(home, "ULJS00244"), filepath.Dir(home), filepath.Join(filepath.Dir(home), "ULJS00244")}
	for _, p := range roots {
		if hasDLCS(p) {
			return p
		}
	}
	return ""
}
func getHome() (string, error) {
	p, e := os.Executable()
	if e != nil {
		return "", e
	}
	return filepath.Dir(p), nil
}
func workDir() (string, error) {
	base := os.Getenv("LOCALAPPDATA")
	if base == "" {
		var err error
		base, err = os.UserCacheDir()
		if err != nil {
			return "", err
		}
	}
	return filepath.Join(base, "LaPucelleES", "app_v0_13_0"), nil
}
func extractEmbedded(base string) error {
	stamp := filepath.Join(base, ".version")
	if b, err := os.ReadFile(stamp); err == nil && strings.TrimSpace(string(b)) == version && isFile(filepath.Join(base, "scripts", "construir_parche.py")) && isFile(filepath.Join(base, "datos", "mapa_26258_unidades.csv")) && isFile(filepath.Join(base, "scripts", "nis_lzs_pack.exe")) {
		return nil
	}
	if err := os.MkdirAll(base, 0755); err != nil {
		return err
	}
	content, err := resources.ReadFile("resources.tar.gz")
	if err != nil {
		return err
	}
	g, err := gzip.NewReader(bytes.NewReader(content))
	if err != nil {
		return err
	}
	defer g.Close()
	t := tar.NewReader(g)
	for {
		h, e := t.Next()
		if errors.Is(e, io.EOF) {
			break
		}
		if e != nil {
			return e
		}
		if h.Typeflag != tar.TypeReg {
			continue
		}
		p := filepath.Join(base, filepath.FromSlash(h.Name))
		rel, e := filepath.Rel(base, p)
		if e != nil || strings.HasPrefix(rel, "..") || filepath.IsAbs(rel) {
			return errors.New("ruta insegura en el paquete")
		}
		if e := os.MkdirAll(filepath.Dir(p), 0755); e != nil {
			return e
		}
		f, e := os.OpenFile(p, os.O_CREATE|os.O_TRUNC|os.O_WRONLY, 0644)
		if e != nil {
			return e
		}
		_, e = io.Copy(f, t)
		f.Close()
		if e != nil {
			return e
		}
	}
	return os.WriteFile(stamp, []byte(version), 0644)
}
func runCmd(name string, args ...string) (string, error) {
	c := exec.Command(name, args...)
	b, e := c.CombinedOutput()
	return string(b), e
}
func existingPython() string {
	// Primero Python oficial de la app; si existe y responde, no descarga nada.
	base, e := workDir()
	if e == nil {
		p := filepath.Join(filepath.Dir(base), "python311", "python.exe")
		if isFile(p) {
			if _, e := runCmd(p, "-c", "print('ok')"); e == nil {
				return p
			}
		}
	}
	// En Windows no confundir launcher de Microsoft Store con Python real.
	for _, p := range []string{"py", "python", "python3"} {
		if _, e := exec.LookPath(p); e != nil {
			continue
		}
		args := []string{"-c", "import sys; assert sys.version_info >= (3,10); print('ok')"}
		if p == "py" {
			args = append([]string{"-3"}, args...)
		}
		c := exec.Command(p, args...)
		if e := c.Run(); e == nil {
			return p
		}
	}
	return ""
}
func getPython() (string, bool, error) {
	if p := existingPython(); p != "" {
		return p, p == "py", nil
	}
	base, e := workDir()
	if e != nil {
		return "", false, e
	}
	dest := filepath.Join(filepath.Dir(base), "python311")
	if e := os.MkdirAll(dest, 0755); e != nil {
		return "", false, e
	}
	zipPath := filepath.Join(dest, "runtime.zip")
	fmt.Println("\nNo hay Python compatible disponible. Descargando Python oficial")
	fmt.Println("Origen:", pythonDownload)
	fmt.Println("Esto ocurre una sola vez. No se realiza instalacion en Windows.")
	client := &http.Client{Timeout: 4 * time.Minute}
	req, e := http.NewRequest("GET", pythonDownload, nil)
	if e != nil {
		return "", false, e
	}
	req.Header.Set("User-Agent", "LaPucellePatcher/0.3")
	res, e := client.Do(req)
	if e != nil {
		return "", false, fmt.Errorf("no se pudo descargar el runtime: %w", e)
	}
	defer res.Body.Close()
	if res.StatusCode != 200 {
		return "", false, fmt.Errorf("descarga Python HTTP %d (usa Python 3.10+ instalado o comprueba conexion)", res.StatusCode)
	}
	if res.ContentLength > maxDownload {
		return "", false, errors.New("runtime demasiado grande")
	}
	f, e := os.Create(zipPath)
	if e != nil {
		return "", false, e
	}
	n, e := io.Copy(f, io.LimitReader(res.Body, maxDownload+1))
	f.Close()
	if e != nil {
		return "", false, e
	}
	if n > maxDownload {
		return "", false, errors.New("runtime excede limite de descarga")
	}
	fmt.Printf("Descargado: %.1f MiB\n", float64(n)/(1<<20))
	z, e := zip.OpenReader(zipPath)
	if e != nil {
		return "", false, fmt.Errorf("ZIP de Python invalido: %w", e)
	}
	for _, item := range z.File {
		if item.FileInfo().IsDir() {
			continue
		}
		rel := filepath.Clean(item.Name)
		if strings.ContainsAny(rel, "/\\") || strings.Contains(rel, "..") {
			z.Close()
			return "", false, errors.New("ZIP contiene ruta no valida")
		}
		p := filepath.Join(dest, rel)
		r, e := item.Open()
		if e != nil {
			z.Close()
			return "", false, e
		}
		o, e := os.Create(p)
		if e != nil {
			r.Close()
			z.Close()
			return "", false, e
		}
		_, e = io.Copy(o, io.LimitReader(r, int64(50<<20)))
		o.Close()
		r.Close()
		if e != nil {
			z.Close()
			return "", false, e
		}
	}
	z.Close()
	os.Remove(zipPath)
	py := filepath.Join(dest, "python.exe")
	if !isFile(py) {
		return "", false, errors.New("La distribucion descargada no tiene python.exe")
	}
	// Embeddable Python usa un archivo ._pth para limitar los imports.
	pth := filepath.Join(dest, "python311._pth")
	scriptDir := filepath.Join(base, "scripts")
	content := fmt.Sprintf("python311.zip\n.\n%s\n", scriptDir)
	if e = os.WriteFile(pth, []byte(content), 0644); e != nil {
		return "", false, e
	}
	if out, e := runCmd(py, "-c", "import csv,hashlib,urllib.request; print('OK')"); e != nil {
		return "", false, fmt.Errorf("Python embebido no paso prueba: %s: %w", out, e)
	}
	fmt.Println("Python portatil preparado correctamente")
	return py, false, nil
}

type GUIConfig struct {
	ISO           string `json:"iso"`
	DLC           string `json:"dlc"`
	Output        string `json:"output"`
	FontOnly      bool   `json:"fontOnly"`
	Investigation bool   `json:"investigation"`
	Segment       bool   `json:"segment"`
	Atlas         bool   `json:"atlas"`
	Reductions    bool   `json:"reductions"`
	Log           string `json:"log"`
}

func runWorker(configPath string) (err error) {
	raw, err := os.ReadFile(configPath)
	if err != nil {
		return fmt.Errorf("no se pudo leer la configuración: %w", err)
	}
	var cfg GUIConfig
	if err := json.Unmarshal(raw, &cfg); err != nil {
		return fmt.Errorf("configuración inválida: %w", err)
	}
	if cfg.ISO == "" && cfg.DLC == "" {
		return errors.New("debes indicar una ISO, carpeta DLC o ambos")
	}
	if cfg.ISO != "" && (!isFile(cfg.ISO) || strings.ToLower(filepath.Ext(cfg.ISO)) != ".iso") {
		return errors.New("ISO no encontrada o extensión incorrecta")
	}
	if cfg.DLC != "" && !hasDLCS(cfg.DLC) {
		return fmt.Errorf("la carpeta %q no contiene los cuatro EDAT", cfg.DLC)
	}
	if cfg.Output == "" {
		return errors.New("falta la carpeta de salida")
	}
	if cfg.Log != "" {
		if e := os.MkdirAll(filepath.Dir(cfg.Log), 0755); e != nil {
			return e
		}
		log, e := os.Create(cfg.Log)
		if e != nil {
			return fmt.Errorf("no se pudo crear el log: %w", e)
		}
		defer func() {
			if err != nil {
				fmt.Fprintln(log, "ERROR:", err)
			}
			_ = log.Close()
		}()
		os.Stdout = log
		os.Stderr = log
	}
	fmt.Printf("La Pucelle ES v%s\n", version)
	fmt.Println("Modo:", map[bool]string{true: "ISO + DLC", false: "Seleccion parcial"}[cfg.ISO != "" && cfg.DLC != ""])
	fmt.Println("ISO:", cfg.ISO)
	fmt.Println("DLC:", cfg.DLC)
	fmt.Println("Salida:", cfg.Output)
	fmt.Println("Los originales NO se sobrescriben. Resultado EXPERIMENTAL.")
	if e := os.MkdirAll(cfg.Output, 0755); e != nil {
		return fmt.Errorf("no se pudo crear la salida: %w", e)
	}
	base, e := workDir()
	if e != nil {
		return e
	}
	fmt.Println("Preparando archivos del motor... ")
	if e := extractEmbedded(base); e != nil {
		return fmt.Errorf("extracción del motor: %w", e)
	}
	fmt.Println("Comprobando Python portátil...")
	py, isLauncher, e := getPython()
	if e != nil {
		return fmt.Errorf("Python: %w", e)
	}
	args := []string{filepath.Join(base, "scripts", "construir_parche.py"), "--salida", cfg.Output}
	if cfg.ISO != "" {
		args = append(args, "--iso", cfg.ISO)
	}
	if cfg.DLC != "" {
		args = append(args, "--dlc-directorio", cfg.DLC)
	}
	if cfg.FontOnly {
		args = append(args, "--solo-fuentes")
	} else {
		args = append(args, "--descargar-revisiones")
	}
	if cfg.Investigation && !cfg.FontOnly {
		args = append(args, "--incluir-investigacion")
	}
	if !cfg.FontOnly {
		args = append(args, "--dialogos-atomicos")
	}
	if cfg.Segment && !cfg.FontOnly {
		args = append(args, "--segmentar-conservador")
	}
	if cfg.Atlas {
		args = append(args, "--atlas-ui")
	}
	if cfg.Reductions && !cfg.FontOnly {
		args = append(args, "--reducciones-verificadas")
	}
	if isLauncher {
		args = append([]string{"-3"}, args...)
	}
	fmt.Println("Aplicando fuentes y revisión de diálogos...")
	cmd := exec.Command(py, args...)
	cmd.Dir = base
	cmd.Env = append(os.Environ(), "PYTHONUTF8=1", "PYTHONUNBUFFERED=1", "PYTHONIOENCODING=utf-8")
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	if e := cmd.Run(); e != nil {
		return fmt.Errorf("el motor de parcheo terminó con error: %w", e)
	}
	fmt.Println("Proceso completado. Revisa el archivo resumen.json y el reporte.")
	return nil
}

func selfTest() error {
	base, e := workDir()
	if e != nil {
		return e
	}
	if e := extractEmbedded(base); e != nil {
		return e
	}
	for _, p := range []string{"scripts/construir_parche.py", "scripts/subtitulos_script.py", "scripts/fuentes_es.py", "scripts/segmentacion.py", "scripts/nis_lzs_pack.exe", "datos/mapa_26258_unidades.csv", "datos/propuestas_reduccion_v012.csv", "datos/ajustes_reducciones_v013.csv", "scripts/integracion_v013.py"} {
		if !isFile(filepath.Join(base, p)) {
			return fmt.Errorf("falta el recurso %s", p)
		}
	}
	f, e := os.Open(filepath.Join(base, "datos", "mapa_26258_unidades.csv"))
	if e != nil {
		return e
	}
	defer f.Close()
	h := sha256.New()
	if _, e := io.Copy(h, f); e != nil {
		return e
	}
	fmt.Println("Autotest OK, SHA256 manifiesto:", hex.EncodeToString(h.Sum(nil)))
	return nil
}

func runGUI() error {
	executable, e := os.Executable()
	if e != nil {
		return e
	}
	data, e := resources.ReadFile("gui.ps1")
	if e != nil {
		return e
	}
	tmp, e := os.MkdirTemp("", "LaPucelle_GUI_")
	if e != nil {
		return e
	}
	defer os.RemoveAll(tmp)
	// PowerShell 5.1 interpreta UTF-8 correctamente si el archivo lleva BOM.
	ps1 := filepath.Join(tmp, "interfaz.ps1")
	content := append([]byte{0xEF, 0xBB, 0xBF}, data...)
	if e := os.WriteFile(ps1, content, 0600); e != nil {
		return e
	}
	cmd := exec.Command("powershell.exe", "-NoLogo", "-NoProfile", "-STA", "-WindowStyle", "Hidden", "-ExecutionPolicy", "Bypass", "-File", ps1, "-Executable", executable)
	output, e := cmd.CombinedOutput()
	if e != nil {
		return fmt.Errorf("falló la interfaz de Windows: %w. Detalles: %s", e, string(output))
	}
	return nil
}

func main() {
	worker := flag.Bool("worker", false, "Proceso interno de parcheo")
	config := flag.String("config", "", "Ruta de configuración interna")
	self := flag.Bool("self-test", false, "Verifica el paquete integrado")
	flag.Parse()
	if *self {
		if e := selfTest(); e != nil {
			fmt.Fprintln(os.Stderr, e)
			os.Exit(1)
		}
		return
	}
	if *worker {
		if e := runWorker(*config); e != nil {
			fmt.Fprintln(os.Stderr, "ERROR:", e)
			os.Exit(1)
		}
		return
	}
	if e := runGUI(); e != nil {
		base, _ := os.UserCacheDir()
		if base != "" {
			_ = os.WriteFile(filepath.Join(base, "LaPucelle_GUI_error.txt"), []byte(e.Error()), 0644)
		}
		fmt.Fprintln(os.Stderr, e)
		os.Exit(1)
	}
}
