package main

import (
    "encoding/json"
    "os"
    "path/filepath"
    "strings"
    "testing"
)

func writeTestFile(t *testing.T,path,content string) {
    t.Helper()
    if err:=os.MkdirAll(filepath.Dir(path),0755);err!=nil {t.Fatal(err)}
    if err:=os.WriteFile(path,[]byte(content),0644);err!=nil {t.Fatal(err)}
}
func readTestFile(t *testing.T,path string) string {
    t.Helper()
    b,err:=os.ReadFile(path);if err!=nil {t.Fatal(err)}
    return string(b)
}
func setupFinalDelivery(t *testing.T)(GUIConfig,string,string,string) {
    t.Helper()
    root:=t.TempDir()
    cfg:=GUIConfig{Output:filepath.Join(root,"salida"),ISO:"original.iso",DLC:"ULJS00244"}
    stage:=filepath.Join(cfg.Output,"v017_dlc_entrada")
    scripts:=filepath.Join(cfg.Output,"v017_scripts_conservador")
    preliminaryISO:=filepath.Join(cfg.Output,"La_Pucelle_Ragnarok_ES_PRELIMINAR.iso")
    writeTestFile(t,preliminaryISO,"iso-preliminar")
    for n:=0;n<4;n++{
        suffix:=string(rune('0'+n))
        writeTestFile(t,filepath.Join(stage,"DL_JP_0"+suffix+".EDAT"),"dlc"+suffix+"-preliminar")
    }
    return cfg,preliminaryISO,stage,scripts
}
func writeReport(t *testing.T,scriptOut string, entries map[string]string) {
    t.Helper()
    data,e:=json.Marshal(entries);if e!=nil {t.Fatal(e)}
    writeTestFile(t,filepath.Join(scriptOut,"resumen_script_v014.json"),string(data))
}
func TestEntregaMixtaIncluyeDLCNoModificados(t *testing.T) {
    cfg,iso,stage,scripts:=setupFinalDelivery(t)
    updatedISO:=filepath.Join(scripts,"La_Pucelle_Ragnarok_ES_SCRIPT_V014_EXPERIMENTAL.iso")
    updatedDLC:=filepath.Join(scripts,"DLC_00_SCRIPT_V014_EXPERIMENTAL.EDAT")
    writeTestFile(t,updatedISO,"iso-segunda-fase")
    writeTestFile(t,updatedDLC,"dlc0-segunda-fase")
    writeReport(t,scripts,map[string]string{"iso":updatedISO,"DLC_00":updatedDLC})
    final,e:=prepareFinalDelivery(cfg,iso,stage,scripts)
    if e!=nil {t.Fatal(e)}
    if want:="iso-segunda-fase";readTestFile(t,filepath.Join(final,"La_Pucelle_Ragnarok_ES_V0172_PRUEBA_PPSSPP.iso"))!=want {t.Fatal("ISO no corresponde a segunda fase")}
    for n:=0;n<4;n++{
        suffix:=string(rune('0'+n))
        path:=filepath.Join(final,"ULJS00244","DL_JP_0"+suffix+".EDAT")
        want:="dlc"+suffix+"-preliminar"
        if n==0 {want="dlc0-segunda-fase"}
        if got:=readTestFile(t,path);got!=want {t.Fatalf("DLC %d: obtuvo %q; esperaba %q",n,got,want)}
    }
    manifest:=readTestFile(t,filepath.Join(final,"INFORME_ENTREGA_V0172.json"))
    if !strings.Contains(manifest,"conservado_de_fase_preliminar_sin_cambios_de_scripts"){t.Fatal("no explica DLC sin cambios")}
    if _,e:=os.Stat(final+".en_construccion");!os.IsNotExist(e){t.Fatal("se dejó staging visible")}
    // Garantía: los materiales de entrada NO fueron movidos ni sobrescritos.
    if readTestFile(t,updatedDLC)!="dlc0-segunda-fase" || readTestFile(t,filepath.Join(stage,"DL_JP_01.EDAT"))!="dlc1-preliminar" {t.Fatal("se alteraron las fuentes")}
}
func TestInformeQueDeclaraDLCInexistenteBloquea(t *testing.T) {
    cfg,iso,stage,scripts:=setupFinalDelivery(t)
    writeReport(t,scripts,map[string]string{"DLC_02":filepath.Join(scripts,"no-existe.EDAT")})
    _,e:=prepareFinalDelivery(cfg,iso,stage,scripts)
    if e==nil || !strings.Contains(e.Error(),"DLC_02"){t.Fatalf("no bloqueó DLC declarado ausente: %v",e)}
    if _,e:=os.Stat(filepath.Join(cfg.Output,"JUEGO_PARA_PPSSPP_V0172"));!os.IsNotExist(e){t.Fatal("salida parcial publicada")}
}
func TestPreflightDeCuatroDLC(t *testing.T) {
    cfg,iso,stage,scripts:=setupFinalDelivery(t)
    if e:=os.Remove(filepath.Join(stage,"DL_JP_03.EDAT"));e!=nil {t.Fatal(e)}
    writeReport(t,scripts,map[string]string{})
    _,e:=prepareFinalDelivery(cfg,iso,stage,scripts)
    if e==nil || !strings.Contains(e.Error(),"DLC_03"){t.Fatalf("debió rechazar paquete incompleto: %v",e)}
    if _,e:=os.Stat(filepath.Join(cfg.Output,"JUEGO_PARA_PPSSPP_V0172"));!os.IsNotExist(e){t.Fatal("carpeta final incompleta")}
}
func TestSóloISOConInformeSinCambios(t *testing.T) {
    cfg,iso,stage,scripts:=setupFinalDelivery(t)
    cfg.DLC=""
    writeReport(t,scripts,map[string]string{})
    final,e:=prepareFinalDelivery(cfg,iso,stage,scripts)
    if e!=nil{t.Fatal(e)}
    if got:=readTestFile(t,filepath.Join(final,"La_Pucelle_Ragnarok_ES_V0172_PRUEBA_PPSSPP.iso"));got!="iso-preliminar"{t.Fatal("no conserva ISO sin cambios")}
    if _,e:=os.Stat(filepath.Join(final,"ULJS00244"));!os.IsNotExist(e){t.Fatal("no debe crear DLC en modo ISO")}
}
