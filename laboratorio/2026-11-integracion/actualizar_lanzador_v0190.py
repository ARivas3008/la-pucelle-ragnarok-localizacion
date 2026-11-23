from pathlib import Path
B=Path(__file__).resolve().parent/'fuente/parcheador'
p=B/'main.go';s=p.read_text(encoding='utf8')
begin=s.index('\targs := []string{filepath.Join(base, "scripts", "construir_parche.py")',s.index('func runWorker'))
end=s.index('\n\treturn nil\n}',begin)
replacement='''	args := []string{filepath.Join(base, "scripts", "integracion_total.py"), "--salida", cfg.Output, "--repo-directorio", base}
	if cfg.ISO != "" { args = append(args, "--iso", cfg.ISO) }
	if cfg.DLC != "" { args = append(args, "--dlc-directorio", cfg.DLC) }
	if isLauncher { args = append([]string{"-3"}, args...) }
	fmt.Println("Aplicando corpus revisado, diálogos completos y menús...")
	cmd := exec.Command(py, args...)
	cmd.Dir = base
	cmd.Env = append(os.Environ(), "PYTHONUTF8=1", "PYTHONUNBUFFERED=1", "PYTHONIOENCODING=utf-8")
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	if e := cmd.Run(); e != nil { return fmt.Errorf("el motor de integración terminó con error: %w", e) }
	fmt.Println("Archivos generados en JUEGO_PARA_PPSSPP. Consulta informes: la traducción y la validación visual siguen en curso.")'''
s=s[:begin]+replacement+s[end:]
s=s.replace('0.18.3-fijo-qa','0.19.0-integracion').replace('app_v0_18_3_fijo','app_v0_19_0_integracion')
s=s.replace('[]string{"scripts/construir_parche.py",','[]string{"scripts/integracion_total.py", "scripts/recompilar_talk.py", "datos/tablas_base_deltas.json.z", "datos/segmentos_hymt2_aprobados.json", "scripts/construir_parche.py",')
p.write_text(s,encoding='utf8')
p=B/'build_release.py';s=p.read_text(encoding='utf8').replace("VERSION='0.18.3-fijo-qa'","VERSION='0.19.0-integracion'");p.write_text(s,encoding='utf8')
p=B/'gui.ps1';s=p.read_text(encoding='utf8').replace('0.18.3','0.19.0').replace('v0183','v0190')
s=s.replace("'5. Opciones de traduccion'","'5. Traducción incluida'")
s=s.replace("'El aislamiento gráfico sirve para investigar; NO confirma que los glitches desaparezcan.'","'Versión de pruebas: consulta el informe de textos pendientes después del parcheo.'")
s=s.replace("scriptMode = 'fijo'","scriptMode = 'integracion'")
old='UpdateTargetState\n[void]$form.ShowDialog()'
new='''foreach ($legacyControl in @($fontOnly,$includeInvestigation,$atlasUI,$reductions,$scripts,$scriptPhase,$preserveEboot)) {$legacyControl.Visible = $false}
$null = LabelAt 'Se aplican los diálogos revisados, los menús y las correcciones incorporadas a esta versión. Los textos pendientes se detallan en el informe de salida.' 32 490 770 70 $false
$null = LabelAt 'Selecciona una carpeta de salida nueva. Al terminar, la carpeta JUEGO_PARA_PPSSPP contendrá la ISO y los DLC seleccionados.' 32 575 770 60 $false
UpdateTargetState
[void]$form.ShowDialog()'''
assert old in s;s=s.replace(old,new);p.write_text(s,encoding='utf8')
print('Lanzador e interfaz actualizados a 0.19.0-integracion')
