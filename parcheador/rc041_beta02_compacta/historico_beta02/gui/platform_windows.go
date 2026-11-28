package main

import (
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"runtime"
	"strings"
	"sync"
	"syscall"
	"unsafe"
)

var user32 = syscall.NewLazyDLL("user32.dll")
var kernel32 = syscall.NewLazyDLL("kernel32.dll")
var gdi32 = syscall.NewLazyDLL("gdi32.dll")
var comdlg32 = syscall.NewLazyDLL("comdlg32.dll")
var shell32 = syscall.NewLazyDLL("shell32.dll")
var ole32 = syscall.NewLazyDLL("ole32.dll")
var comctl32 = syscall.NewLazyDLL("comctl32.dll")

//go:uintptrescapes
func call(d *syscall.LazyDLL, n string, args ...uintptr) uintptr {
	r, _, _ := d.NewProc(n).Call(args...)
	return r
}
func ptr(s string) *uint16       { p, _ := syscall.UTF16PtrFromString(s); return p }
func u(s string) uintptr         { return uintptr(unsafe.Pointer(ptr(s))) }
func p(v unsafe.Pointer) uintptr { return uintptr(v) }
func send(h uintptr, m uint32, w, l uintptr) uintptr {
	return call(user32, "SendMessageW", h, uintptr(m), w, l)
}
func setText(h uintptr, s string) {
	q := ptr(s)
	call(user32, "SetWindowTextW", h, p(unsafe.Pointer(q)))
	runtime.KeepAlive(q)
}
func getText(h uintptr) string {
	n := call(user32, "GetWindowTextLengthW", h)
	if n > 32767 {
		n = 32767
	}
	b := make([]uint16, n+1)
	call(user32, "GetWindowTextW", h, p(unsafe.Pointer(&b[0])), uintptr(len(b)))
	return syscall.UTF16ToString(b)
}
func enable(h uintptr, v bool) {
	var n uintptr
	if v {
		n = 1
	}
	call(user32, "EnableWindow", h, n)
}
func box(h uintptr, s, t string, flags uintptr) uintptr {
	a, b := ptr(s), ptr(t)
	r := call(user32, "MessageBoxW", h, p(unsafe.Pointer(a)), p(unsafe.Pointer(b)), flags)
	runtime.KeepAlive(a)
	runtime.KeepAlive(b)
	return r
}
func showError(s string) { box(0, s, "La Pucelle: Ragnarok", 16) }

const (
	wmDestroy        = 2
	wmClose          = 0x10
	wmCommand        = 0x111
	wmTimer          = 0x113
	wmSetFont        = 0x30
	wmCtlColorStatic = 0x138
	wsChild          = 0x40000000
	wsVisible        = 0x10000000
	wsTab            = 0x10000
	wsGroup          = 0x20000
	wsBorder         = 0x800000
	wsVscroll        = 0x200000
	bsRadio          = 9
	bmGetCheck       = 0xf0
	bmSetCheck       = 0xf1
	emSetSel         = 0xb1
	emScrollCaret    = 0xb7
	idBoth           = 101
	idISO            = 102
	idDLC            = 103
	idPickISO        = 104
	idPickDLC        = 105
	idPickOut        = 106
	idStart          = 107
	idCancel         = 108
	idOpen           = 109
)

type rect struct{ Left, Top, Right, Bottom int32 }
type point struct{ X, Y int32 }
type wndClass struct {
	Size, Style                   uint32
	Proc                          uintptr
	ClsExtra, WndExtra            int32
	Instance, Icon, Cursor, Brush uintptr
	Menu, Class                   *uint16
	SmallIcon                     uintptr
}
type winMsg struct {
	Hwnd           uintptr
	Message        uint32
	WParam, LParam uintptr
	Time           uint32
	Pt             point
	Private        uint32
}
type openFile struct {
	Size                         uint32
	Owner, Instance              uintptr
	Filter, CustomFilter         *uint16
	MaxCustomFilter, FilterIndex uint32
	File                         *uint16
	MaxFile                      uint32
	FileTitle                    *uint16
	MaxFileTitle                 uint32
	InitialDir, Title            *uint16
	Flags                        uint32
	FileOffset, FileExtension    uint16
	DefExt                       *uint16
	CustomData, Hook             uintptr
	Template                     *uint16
	Reserved                     uintptr
	Reserved2, FlagsEx           uint32
}
type browseInfo struct {
	Owner, Root        uintptr
	DisplayName, Title *uint16
	Flags              uint32
	Callback, Param    uintptr
	Image              int32
}
type logWriter struct {
	mu sync.Mutex
	s  string
}

func (l *logWriter) Write(b []byte) (int, error) {
	l.mu.Lock()
	defer l.mu.Unlock()
	l.s += string(b)
	if len(l.s) > 24000 {
		l.s = l.s[len(l.s)-20000:]
		if i := strings.IndexByte(l.s, '\n'); i >= 0 {
			l.s = l.s[i+1:]
		}
	}
	return len(b), nil
}
func (l *logWriter) text() string { l.mu.Lock(); defer l.mu.Unlock(); return l.s }

type gui struct {
	h, instance, font, bold, titleFont, headerBrush, bgBrush                                                                          uintptr
	headerLabels                                                                                                                      map[uintptr]bool
	both, isoOnly, dlcOnly, iso, dlc, dest, isoLabel, dlcLabel, pickISO, pickDLC, pickOut, start, cancel, open, progress, status, log uintptr
	busy                                                                                                                              bool
	done                                                                                                                              chan error
	writer                                                                                                                            *logWriter
	last                                                                                                                              string
	lastOut                                                                                                                           string
	controls                                                                                                                          []uintptr
}

var app *gui

func color(r, g, b uintptr) uintptr { return r | (g << 8) | (b << 16) }
func makeFont(height, weight int32) uintptr {
	q := ptr("Segoe UI")
	return call(gdi32, "CreateFontW", uintptr(int64(height)), 0, 0, 0, uintptr(weight), 0, 0, 0, 1, 0, 0, 5, 0, p(unsafe.Pointer(q)))
}
func (g *gui) child(class, label string, style, ex uintptr, x, y, w, h int, id uintptr, font uintptr) uintptr {
	a, b := ptr(class), ptr(label)
	v := call(user32, "CreateWindowExW", ex, p(unsafe.Pointer(a)), p(unsafe.Pointer(b)), style|wsChild|wsVisible, uintptr(x), uintptr(y), uintptr(w), uintptr(h), g.h, id, g.instance, 0)
	runtime.KeepAlive(a)
	runtime.KeepAlive(b)
	if v == 0 {
		panic("No se pudo crear control " + class)
	}
	if font != 0 {
		send(v, wmSetFont, font, 1)
	}
	return v
}
func (g *gui) label(s string, x, y, w, h int, font uintptr) uintptr {
	return g.child("STATIC", s, 0, 0, x, y, w, h, 0, font)
}
func (g *gui) button(s string, x, y, w, h int, id uintptr) uintptr {
	return g.child("BUTTON", s, wsTab, 0, x, y, w, h, id, g.bold)
}
func (g *gui) edit(s string, x, y, w, h int) uintptr {
	return g.child("EDIT", s, wsTab|0x80, 0x200, x, y, w, h, 0, g.font)
}
func (g *gui) setup() {
	g.font = makeFont(-16, 400)
	g.bold = makeFont(-16, 600)
	g.titleFont = makeFont(-27, 700)
	g.headerLabels = map[uintptr]bool{}
	g.headerLabels[g.label("LA PUCELLE: RAGNAROK", 0, 0, 790, 54, g.titleFont)] = true
	g.headerLabels[g.label("PARCHEADOR ESPAÑOL  |  ISO / DLC  |  RC041_REV6_BETA02 · VERSIÓN DE PRUEBAS", 0, 54, 790, 28, g.font)] = true
	g.label("1. Selecciona qué quieres parchear", 20, 94, 740, 24, g.bold)
	g.both = g.child("BUTTON", "ISO + DLC", wsTab|wsGroup|bsRadio, 0, 24, 119, 150, 25, idBoth, g.font)
	g.isoOnly = g.child("BUTTON", "Solo ISO", wsTab|bsRadio, 0, 200, 119, 150, 25, idISO, g.font)
	g.dlcOnly = g.child("BUTTON", "Solo DLC", wsTab|bsRadio, 0, 375, 119, 150, 25, idDLC, g.font)
	g.isoLabel = g.label("2. ISO original (ULJS-00244, v1.1.2)", 20, 153, 745, 22, g.bold)
	g.iso = g.edit("", 22, 177, 590, 27)
	g.pickISO = g.button("Examinar ISO...", 624, 175, 142, 31, idPickISO)
	g.dlcLabel = g.label("3. Carpeta con los cuatro archivos EDAT originales", 20, 216, 745, 22, g.bold)
	g.dlc = g.edit("", 22, 240, 590, 27)
	g.pickDLC = g.button("Examinar carpeta...", 624, 238, 142, 31, idPickDLC)
	g.label("4. Carpeta de salida (los originales no se sobrescriben)", 20, 279, 745, 22, g.bold)
	home, _ := os.UserHomeDir()
	g.dest = g.edit(filepath.Join(home, "Documents", "LaPucelleES"), 22, 303, 590, 27)
	g.pickOut = g.button("Elegir destino...", 624, 301, 142, 31, idPickOut)
	g.label("5. Traducción y gráficos incluidos", 20, 343, 745, 22, g.bold)
	g.label("FontB manual, comas unificadas, carteles ajustados y Mapa aprobado.\nReconstrucción preliminar: consulta el informe de pendientes; falta QA en PPSSPP.", 22, 368, 744, 43, g.font)
	g.start = g.button("INICIAR PARCHEO", 22, 417, 220, 36, idStart)
	g.cancel = g.button("Cancelar", 255, 417, 115, 36, idCancel)
	g.open = g.button("Abrir salida", 624, 417, 142, 36, idOpen)
	g.progress = g.child("msctls_progress32", "", 8, 0, 22, 464, 744, 13, 0, 0)
	g.status = g.label("Listo para seleccionar los archivos.", 22, 483, 744, 22, g.font)
	g.log = g.child("EDIT", "", wsVscroll|0x4|0x40|0x800|0x1000, 0x200, 22, 508, 744, 89, 0, g.font)
	g.controls = []uintptr{g.both, g.isoOnly, g.dlcOnly, g.iso, g.dlc, g.dest, g.pickISO, g.pickDLC, g.pickOut, g.start}
	g.mode(idISO)
	call(user32, "SetTimer", g.h, 1, 150, 0)
}
func (g *gui) mode(id int) {
	for _, v := range []struct {
		h uintptr
		i int
	}{{g.both, idBoth}, {g.isoOnly, idISO}, {g.dlcOnly, idDLC}} {
		var b uintptr
		if id == v.i {
			b = 1
		}
		send(v.h, bmSetCheck, b, 0)
	}
	g.update()
}
func (g *gui) update() {
	for _, h := range g.controls {
		enable(h, !g.busy)
	}
	wantIso := send(g.dlcOnly, bmGetCheck, 0, 0) == 0
	wantDlc := send(g.isoOnly, bmGetCheck, 0, 0) == 0
	for _, h := range []uintptr{g.iso, g.pickISO, g.isoLabel} {
		enable(h, !g.busy && wantIso)
	}
	for _, h := range []uintptr{g.dlc, g.pickDLC, g.dlcLabel} {
		enable(h, !g.busy && wantDlc)
	}
	enable(g.cancel, g.busy)
	enable(g.open, !g.busy)
}
func chooseISO(owner uintptr) string {
	buf := make([]uint16, 32768)
	f := []uint16{'I', 'm', 'a', 'g', 'e', 'n', ' ', 'P', 'S', 'P', ' ', '(', '*', '.', 'i', 's', 'o', ')', 0, '*', '.', 'i', 's', 'o', 0, 0}
	o := openFile{Owner: owner, Filter: &f[0], File: &buf[0], MaxFile: uint32(len(buf)), Title: ptr("Selecciona la ISO original"), Flags: 0x1000 | 0x800 | 0x80000 | 8}
	o.Size = uint32(unsafe.Sizeof(o))
	r := call(comdlg32, "GetOpenFileNameW", p(unsafe.Pointer(&o)))
	runtime.KeepAlive(f)
	runtime.KeepAlive(buf)
	if r == 0 {
		return ""
	}
	return syscall.UTF16ToString(buf)
}
func chooseFolder(owner uintptr, title string) string {
	var name [260]uint16
	var path [32768]uint16
	b := browseInfo{Owner: owner, DisplayName: &name[0], Title: ptr(title), Flags: 0x1 | 0x40}
	r := call(shell32, "SHBrowseForFolderW", p(unsafe.Pointer(&b)))
	if r == 0 {
		return ""
	}
	defer call(ole32, "CoTaskMemFree", r)
	if call(shell32, "SHGetPathFromIDListW", r, p(unsafe.Pointer(&path[0]))) == 0 {
		return ""
	}
	return syscall.UTF16ToString(path[:])
}
func (g *gui) begin() {
	if g.busy {
		return
	}
	c := Config{ISO: strings.TrimSpace(getText(g.iso)), DLC: strings.TrimSpace(getText(g.dlc)), Output: strings.TrimSpace(getText(g.dest))}
	if send(g.dlcOnly, bmGetCheck, 0, 0) == 1 {
		c.ISO = ""
	} else if c.ISO == "" {
		box(g.h, "Selecciona la ISO original .iso (extrae el .7z primero).", "Falta la ISO", 48)
		return
	}
	if send(g.isoOnly, bmGetCheck, 0, 0) == 1 {
		c.DLC = ""
	} else if c.DLC == "" {
		box(g.h, "Selecciona la carpeta DLC original.", "Faltan los DLC", 48)
		return
	}
	if c.Output == "" {
		box(g.h, "Selecciona una carpeta de salida.", "Falta el destino", 48)
		return
	}
	g.lastOut = c.Output
	g.busy = true
	cancelled.Store(false)
	g.writer = &logWriter{}
	out = g.writer
	g.last = ""
	g.done = make(chan error, 1)
	setText(g.log, "")
	setText(g.status, "Comprobando originales y aplicando parche...")
	send(g.progress, 0x40a, 1, 40)
	g.update()
	go func() {
		defer func() {
			if r := recover(); r != nil {
				g.done <- fmt.Errorf("Error interno: %v", r)
			}
		}()
		g.done <- run(c)
	}()
}
func (g *gui) tick() {
	if !g.busy {
		return
	}
	v := g.writer.text()
	if v != g.last {
		g.last = v
		setText(g.log, strings.ReplaceAll(v, "\n", "\r\n"))
		send(g.log, emSetSel, ^uintptr(0), ^uintptr(0))
		send(g.log, emScrollCaret, 0, 0)
	}
	select {
	case e := <-g.done:
		g.busy = false
		out = os.Stdout
		send(g.progress, 0x40a, 0, 0)
		g.update()
		if e == nil {
			send(g.progress, 0x402, 100, 0)
			setText(g.status, "Terminado. ISO/DLC verificados por SHA-256.")
			box(g.h, "Parche aplicado. Abre JUEGO_PARA_PPSSPP_RC041_REV6_BETA02.\nConsulta INFORME_RC041_REV6_BETA02.json. Validación visual pendiente.", "Parcheo terminado", 64)
		} else if errors.Is(e, errCancelled) {
			setText(g.status, "Cancelado. Los originales permanecen intactos.")
		} else {
			setText(g.status, "Error durante el parcheo. Los originales no se sobrescribieron.")
			box(g.h, e.Error(), "Parcheo interrumpido", 16)
		}
	default:
	}
}
func windowProc(h uintptr, m uint32, w, l uintptr) uintptr {
	g := app
	switch m {
	case wmCommand:
		if g == nil {
			return 0
		}
		id := int(w & 0xffff)
		if w>>16 != 0 {
			return 0
		}
		switch id {
		case idBoth, idISO, idDLC:
			if !g.busy {
				g.mode(id)
			}
		case idPickISO:
			if s := chooseISO(h); s != "" {
				setText(g.iso, s)
			}
		case idPickDLC:
			if s := chooseFolder(h, "Selecciona la carpeta ULJS00244 original"); s != "" {
				nested := filepath.Join(s, "ULJS00244")
				if _, e := os.Stat(filepath.Join(nested, "DL_JP_00.EDAT")); e == nil {
					s = nested
				}
				setText(g.dlc, s)
			}
		case idPickOut:
			if s := chooseFolder(h, "Elige una carpeta de salida"); s != "" {
				setText(g.dest, s)
			}
		case idStart:
			g.begin()
		case idCancel:
			cancelled.Store(true)
			setText(g.status, "Cancelando de forma segura...")
			enable(g.cancel, false)
		case idOpen:
			s := getText(g.dest)
			if _, e := os.Stat(s); e == nil {
				verb, path := ptr("open"), ptr(s)
				call(shell32, "ShellExecuteW", h, p(unsafe.Pointer(verb)), p(unsafe.Pointer(path)), 0, 0, 1)
				runtime.KeepAlive(verb)
				runtime.KeepAlive(path)
			} else {
				box(h, "La carpeta todavía no existe.", "Salida", 48)
			}
		}
		return 0
	case wmTimer:
		if g != nil {
			g.tick()
		}
		return 0
	case wmCtlColorStatic:
		if g != nil {
			if g.headerLabels[l] {
				call(gdi32, "SetTextColor", w, color(245, 247, 250))
				call(gdi32, "SetBkColor", w, color(26, 39, 60))
				return g.headerBrush
			}
			call(gdi32, "SetTextColor", w, color(34, 48, 66))
			call(gdi32, "SetBkColor", w, color(245, 247, 250))
			return g.bgBrush
		}
	case wmClose:
		if g != nil && g.busy {
			box(h, "Cancela el parcheo antes de cerrar.", "Parcheo en curso", 48)
			return 0
		}
		call(user32, "DestroyWindow", h)
		return 0
	case wmDestroy:
		call(user32, "PostQuitMessage", 0)
		return 0
	}
	return call(user32, "DefWindowProcW", h, uintptr(m), w, l)
}
func launch() (err error) {
	runtime.LockOSThread()
	defer runtime.UnlockOSThread()
	defer func() {
		if r := recover(); r != nil {
			err = fmt.Errorf("No se pudo abrir la interfaz: %v", r)
		}
	}()
	call(ole32, "CoInitializeEx", 0, 2)
	defer call(ole32, "CoUninitialize")
	icc := [2]uint32{8, 0x20}
	if call(comctl32, "InitCommonControlsEx", p(unsafe.Pointer(&icc[0]))) == 0 {
		return errors.New("No se pudieron inicializar los controles de Windows")
	}
	g := &gui{instance: call(kernel32, "GetModuleHandleW", 0)}
	app = g
	g.headerBrush = call(gdi32, "CreateSolidBrush", color(26, 39, 60))
	g.bgBrush = call(gdi32, "CreateSolidBrush", color(245, 247, 250))
	name := ptr("LaPucelleRC041_REV6_BETA02Native")
	wc := wndClass{Proc: syscall.NewCallback(windowProc), Instance: g.instance, Cursor: call(user32, "LoadCursorW", 0, 32512), Brush: g.bgBrush, Class: name}
	wc.Size = uint32(unsafe.Sizeof(wc))
	if call(user32, "RegisterClassExW", p(unsafe.Pointer(&wc))) == 0 {
		return errors.New("No se pudo registrar la ventana")
	}
	style := uintptr(0x00ca0000)
	r := rect{Right: 790, Bottom: 612}
	call(user32, "AdjustWindowRectEx", p(unsafe.Pointer(&r)), style, 0, 0)
	ww, hh := r.Right-r.Left, r.Bottom-r.Top
	var work rect
	call(user32, "SystemParametersInfoW", 48, 0, p(unsafe.Pointer(&work)), 0)
	x, y := work.Left+(work.Right-work.Left-ww)/2, work.Top+(work.Bottom-work.Top-hh)/2
	if x < work.Left {
		x = work.Left
	}
	if y < work.Top {
		y = work.Top
	}
	title := ptr("La Pucelle: Ragnarok - Parcheador ES RC041_REV6_BETA02")
	g.h = call(user32, "CreateWindowExW", 0, p(unsafe.Pointer(name)), p(unsafe.Pointer(title)), style, uintptr(x), uintptr(y), uintptr(ww), uintptr(hh), 0, 0, g.instance, 0)
	if g.h == 0 {
		return errors.New("CreateWindowExW falló")
	}
	g.setup()
	call(user32, "ShowWindow", g.h, 5)
	call(user32, "UpdateWindow", g.h)
	if len(os.Args) == 2 && os.Args[1] == "--gui-self-test" {
		if g.iso == 0 || g.dlc == 0 || g.start == 0 || g.progress == 0 {
			return errors.New("Controles GUI incompletos")
		}
		call(user32, "DestroyWindow", g.h)
		return nil
	}
	var msg winMsg
	for {
		r := int32(call(user32, "GetMessageW", p(unsafe.Pointer(&msg)), 0, 0, 0))
		if r == 0 {
			break
		}
		if r < 0 {
			return errors.New("GetMessageW falló")
		}
		if call(user32, "IsDialogMessageW", g.h, p(unsafe.Pointer(&msg))) == 0 {
			call(user32, "TranslateMessage", p(unsafe.Pointer(&msg)))
			call(user32, "DispatchMessageW", p(unsafe.Pointer(&msg)))
		}
	}
	return nil
}
