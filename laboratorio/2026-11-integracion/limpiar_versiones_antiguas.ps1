param([switch]$Aplicar)
$ErrorActionPreference='Stop'
$root=[System.IO.Path]::GetFullPath((Split-Path $PSScriptRoot -Parent))
$keepIso=[System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot 'prueba_correcciones/La_Pucelle_Ragnarok_ES_PRELIMINAR.iso'))
$keepExe=[System.IO.Path]::GetFullPath((Join-Path $root '11_Entrega_v0183/LaPucelle_Parcheador_ES_GUI_v0.18.3-fijo-qa.exe'))
if(!(Test-Path -LiteralPath $keepIso) -or !(Test-Path -LiteralPath $keepExe)){throw 'Falta última ISO o último EXE'}
$selected=@()
foreach($dir in @('07_Herramientas_Windows','08_Trabajo_local','09_Entrega_v0180','10_Trabajo_v0181','11_Entrega_v0183')){
 foreach($file in Get-ChildItem -LiteralPath (Join-Path $root $dir) -Recurse -File){
  if($file.Extension -eq '.iso' -or ($file.Name -like 'LaPucelle_Parcheador*.exe' -and $file.FullName -ne $keepExe)){$selected+=$file}
  elseif($file.Extension -eq '.EDAT' -and $file.FullName -match '\\(?:salida_|baseline_|diagnostico\\)'){$selected+=$file}
 }
}
foreach($dir in Get-ChildItem -LiteralPath $PSScriptRoot -Directory -Filter 'prueba_*'){
 foreach($file in Get-ChildItem -LiteralPath $dir.FullName -File -Filter '*.iso'){
  if($file.FullName -ne $keepIso){$selected+=$file}
 }
}
$records=@()
foreach($file in $selected){
 $absolute=[System.IO.Path]::GetFullPath($file.FullName)
 if(!$absolute.StartsWith($root+[System.IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)){throw 'Ruta fuera del proyecto'}
 if($absolute -eq $keepIso -or $absolute -eq $keepExe -or $absolute -match '\\La_Pucelle_Ragnarok_v1\.1\.2\\|\\ULJS00244\\ULJS00244\\'){throw 'Se seleccionó un original o la última versión'}
 $records+=[pscustomobject]@{ruta=$absolute;bytes=$file.Length;estado='seleccionado';error=''}
}
$records | ConvertTo-Json -Depth 3 | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'informes/limpieza_versiones.json') -Encoding utf8
$total=($records | Measure-Object -Property bytes -Sum).Sum
Write-Output "Seleccionados: $($records.Count); bytes: $total; aplicar: $Aplicar"
if($Aplicar){
 foreach($record in $records){
  try {Remove-Item -LiteralPath $record.ruta -Force; $record.estado='eliminado'}
  catch {$record.estado='pendiente';$record.error=$_.Exception.Message}
 }
 $records | ConvertTo-Json -Depth 3 | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'informes/limpieza_versiones_ejecutada_20261117.json') -Encoding utf8
 $records | Group-Object estado | Select-Object Name,Count
}
