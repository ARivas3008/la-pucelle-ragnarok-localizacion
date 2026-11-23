param([ValidateSet('compacta','integrada','scripts_corregidos','dialogos','correcciones')][string]$Variante='correcciones')
$ErrorActionPreference='Stop'
$root=Split-Path $PSScriptRoot -Parent
$lab=Join-Path $root '10_Trabajo_v0181/laboratorio/PPSSPP'
$exe=(Resolve-Path (Join-Path $lab 'PPSSPPWindows64.exe')).Path
$pidFile=Join-Path $root '10_Trabajo_v0181/laboratorio/pid.txt'
if (Test-Path -LiteralPath $pidFile) {
 $proc=Get-Process -Id ([int](Get-Content -LiteralPath $pidFile)) -ErrorAction SilentlyContinue
 if ($proc -and $proc.Path -eq $exe) { Stop-Process -Id $proc.Id }
}
$nombre=if($Variante -eq 'scripts_corregidos'){'La_Pucelle_Ragnarok_ES_SCRIPT_V014_EXPERIMENTAL.iso'}else{'La_Pucelle_Ragnarok_ES_PRELIMINAR.iso'}
$iso=(Resolve-Path (Join-Path $PSScriptRoot ('prueba_'+$Variante+'/'+$nombre))).Path
$config=Join-Path $lab 'memstick/PSP/SYSTEM/ppsspp.ini'
$log=Join-Path $PSScriptRoot ('informes/ppsspp_'+$Variante+'.log')
$child=Start-Process -FilePath $exe -WorkingDirectory $lab -ArgumentList @(('"'+$iso+'"'),('--config="'+$config+'"'),'--graphics=directx11',('--log="'+$log+'"')) -WindowStyle Hidden -PassThru
$child.Id | Set-Content -LiteralPath $pidFile
Write-Output "Laboratorio $Variante PID $($child.Id)"
