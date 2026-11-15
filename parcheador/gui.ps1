param([Parameter(Mandatory=$true)][string]$Executable)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
[System.Windows.Forms.Application]::EnableVisualStyles()

$script:process = $null
$script:cancelled = $false
$script:cfgFile = ''
$script:logFile = ''
$script:previousLog = ''

$navy = [System.Drawing.Color]::FromArgb(26,39,60)
$navy2 = [System.Drawing.Color]::FromArgb(40,57,83)
$blue = [System.Drawing.Color]::FromArgb(38,111,196)
$accent = [System.Drawing.Color]::FromArgb(23,145,119)
$muted = [System.Drawing.Color]::FromArgb(92,105,121)
$bg = [System.Drawing.Color]::FromArgb(245,247,250)
$ink = [System.Drawing.Color]::FromArgb(34,48,66)
$font = [System.Drawing.Font]::new('Segoe UI', 10)
$fontBold = [System.Drawing.Font]::new('Segoe UI', 10, [System.Drawing.FontStyle]::Bold)

$form = New-Object System.Windows.Forms.Form
$form.Text = 'La Pucelle: Ragnarok - Parcheador ES v0.17.4'
$form.ClientSize = [System.Drawing.Size]::new(860, 970)
$form.MinimumSize = [System.Drawing.Size]::new(876, 1010)
$form.MaximumSize = [System.Drawing.Size]::new(1200, 1100)
$form.StartPosition = 'CenterScreen'
$form.BackColor = $bg
$form.Font = $font
$form.AutoScaleMode = [System.Windows.Forms.AutoScaleMode]::Font

function LabelAt([string]$text, [int]$x,[int]$y,[int]$w,[int]$h,[bool]$bold=$false) {
  $l = New-Object System.Windows.Forms.Label
  $l.Text = $text
  $l.Location = [System.Drawing.Point]::new($x,$y)
  $l.Size = [System.Drawing.Size]::new($w,$h)
  $l.ForeColor = $ink
  if ($bold) {$l.Font = $fontBold}
  $form.Controls.Add($l)
  return $l
}
function BoxAt([string]$value,[int]$x,[int]$y,[int]$w) {
  $b = New-Object System.Windows.Forms.TextBox
  $b.Text = $value
  $b.Location = [System.Drawing.Point]::new($x,$y)
  $b.Size = [System.Drawing.Size]::new($w,30)
  $b.Anchor = [System.Windows.Forms.AnchorStyles]::Left -bor [System.Windows.Forms.AnchorStyles]::Right -bor [System.Windows.Forms.AnchorStyles]::Top
  $form.Controls.Add($b)
  return $b
}
function ButtonAt([string]$text,[int]$x,[int]$y,[int]$w,[int]$h,[System.Drawing.Color]$color) {
  $b = New-Object System.Windows.Forms.Button
  $b.Text = $text
  $b.Location = [System.Drawing.Point]::new($x,$y)
  $b.Size = [System.Drawing.Size]::new($w,$h)
  $b.FlatStyle = [System.Windows.Forms.FlatStyle]::Flat
  $b.FlatAppearance.BorderSize = 0
  $b.BackColor = $color
  $b.ForeColor = [System.Drawing.Color]::White
  $b.Cursor = [System.Windows.Forms.Cursors]::Hand
  $b.Font = $fontBold
  $b.Anchor = [System.Windows.Forms.AnchorStyles]::Top -bor [System.Windows.Forms.AnchorStyles]::Right
  $form.Controls.Add($b)
  return $b
}

$header = New-Object System.Windows.Forms.Panel
$header.BackColor = $navy
$header.Location = [System.Drawing.Point]::new(0,0)
$header.Size = [System.Drawing.Size]::new(860,118)
$header.Anchor = [System.Windows.Forms.AnchorStyles]::Top -bor [System.Windows.Forms.AnchorStyles]::Left -bor [System.Windows.Forms.AnchorStyles]::Right
$form.Controls.Add($header)
$title = New-Object System.Windows.Forms.Label
$title.Text = 'LA PUCELLE: RAGNAROK'
$title.Font = [System.Drawing.Font]::new('Segoe UI Semibold', 19, [System.Drawing.FontStyle]::Bold)
$title.ForeColor = [System.Drawing.Color]::White
$title.Location = [System.Drawing.Point]::new(26,20)
$title.Size = [System.Drawing.Size]::new(800,40)
$header.Controls.Add($title)
$sub = New-Object System.Windows.Forms.Label
$sub.Text = 'PARCHEADOR ESPANOL   |   ISO  /  DLC   |   VERSION EXPERIMENTAL 0.17.3'
$sub.Font = [System.Drawing.Font]::new('Segoe UI', 9)
$sub.ForeColor = [System.Drawing.Color]::FromArgb(200,214,232)
$sub.Location = [System.Drawing.Point]::new(28,70)
$sub.Size = [System.Drawing.Size]::new(800,28)
$header.Controls.Add($sub)

$null = LabelAt '1. Selecciona que quieres parchear' 26 133 500 27 $true
$radioBoth = New-Object System.Windows.Forms.RadioButton
$radioBoth.Text = 'ISO + DLC'
$radioBoth.Location = [System.Drawing.Point]::new(32,168)
$radioBoth.Size = [System.Drawing.Size]::new(170,30)
$radioBoth.Checked = $true
$form.Controls.Add($radioBoth)
$radioISO = New-Object System.Windows.Forms.RadioButton
$radioISO.Text = 'Solo ISO'
$radioISO.Location = [System.Drawing.Point]::new(222,168)
$radioISO.Size = [System.Drawing.Size]::new(165,30)
$form.Controls.Add($radioISO)
$radioDLC = New-Object System.Windows.Forms.RadioButton
$radioDLC.Text = 'Solo DLC'
$radioDLC.Location = [System.Drawing.Point]::new(412,168)
$radioDLC.Size = [System.Drawing.Size]::new(165,30)
$form.Controls.Add($radioDLC)

$isoLabel = LabelAt '2. Imagen ISO del juego' 26 213 450 26 $true
$isoBox = BoxAt '' 28 243 644
$isoPick = ButtonAt 'Examinar ISO...' 686 241 145 33 $blue
$isoPick.Add_Click({
  $dlg = New-Object System.Windows.Forms.OpenFileDialog
  $dlg.Title = 'Selecciona la ISO de La Pucelle: Ragnarok'
  $dlg.Filter = 'Imagen PSP (*.iso)|*.iso|Todos los archivos (*.*)|*.*'
  $dlg.CheckFileExists = $true
  $dlg.Multiselect = $false
  if (-not [string]::IsNullOrWhiteSpace($isoBox.Text)) {
    $dir = [System.IO.Path]::GetDirectoryName($isoBox.Text)
    if ([System.IO.Directory]::Exists($dir)) {$dlg.InitialDirectory = $dir}
  }
  if ($dlg.ShowDialog($form) -eq [System.Windows.Forms.DialogResult]::OK) {$isoBox.Text = $dlg.FileName}
})

$dlcLabel = LabelAt '3. Carpeta que contiene DL_JP_00...03.EDAT' 26 293 610 26 $true
$dlcBox = BoxAt '' 28 323 644
$dlcPick = ButtonAt 'Examinar carpeta...' 686 321 145 33 $blue
$dlcPick.Add_Click({
  $dlg = New-Object System.Windows.Forms.FolderBrowserDialog
  $dlg.Description = 'Elige ULJS00244 o la carpeta que contiene los cuatro archivos EDAT'
  $dlg.ShowNewFolderButton = $false
  if ([System.IO.Directory]::Exists($dlcBox.Text)) {$dlg.SelectedPath = $dlcBox.Text}
  if ($dlg.ShowDialog($form) -eq [System.Windows.Forms.DialogResult]::OK) {
    $chosen = $dlg.SelectedPath
    if (-not [System.IO.File]::Exists([System.IO.Path]::Combine($chosen,'DL_JP_00.EDAT')) -and
        [System.IO.File]::Exists([System.IO.Path]::Combine($chosen,'ULJS00244','DL_JP_00.EDAT'))) {
        $chosen = [System.IO.Path]::Combine($chosen,'ULJS00244')
    }
    $dlcBox.Text = $chosen
  }
})

$null = LabelAt '4. Carpeta donde guardar las copias parcheadas' 26 373 720 26 $true
$defaultOutput = [System.IO.Path]::Combine([Environment]::GetFolderPath('MyDocuments'), 'LaPucelleES', 'salida')
$outBox = BoxAt $defaultOutput 28 404 644
$outPick = ButtonAt 'Elegir destino...' 686 402 145 33 $navy2
$outPick.Add_Click({
  $dlg = New-Object System.Windows.Forms.FolderBrowserDialog
  $dlg.Description = 'Selecciona una carpeta de salida (no se reemplazan los originales)'
  $dlg.ShowNewFolderButton = $true
  $p = $outBox.Text
  while (-not [System.IO.Directory]::Exists($p) -and -not [string]::IsNullOrEmpty($p)) {$p = [System.IO.Path]::GetDirectoryName($p)}
  if ([System.IO.Directory]::Exists($p)) {$dlg.SelectedPath = $p}
  if ($dlg.ShowDialog($form) -eq [System.Windows.Forms.DialogResult]::OK) {$outBox.Text = $dlg.SelectedPath}
})

$null = LabelAt '5. Opciones de traduccion' 26 455 600 26 $true
$fontOnly = New-Object System.Windows.Forms.CheckBox
$fontOnly.Text = 'Solo soporte de fuentes (sin reemplazar dialogos)'
$fontOnly.Location = [System.Drawing.Point]::new(32,482)
$fontOnly.Size = [System.Drawing.Size]::new(500,26)
$form.Controls.Add($fontOnly)
$includeInvestigation = New-Object System.Windows.Forms.CheckBox
$includeInvestigation.Text = 'Incluir textos provisionales marcados para investigacion'
$includeInvestigation.Location = [System.Drawing.Point]::new(32,511)
$includeInvestigation.Size = [System.Drawing.Size]::new(620,26)
$includeInvestigation.Checked = $false
$form.Controls.Add($includeInvestigation)
$fontOnly.Add_CheckedChanged({$includeInvestigation.Enabled = -not $fontOnly.Checked; $reductions.Enabled = -not $fontOnly.Checked; $scripts.Enabled = -not $fontOnly.Checked; $scriptPhase.Enabled = (-not $fontOnly.Checked) -and $scripts.Checked})

$atlasUI = New-Object System.Windows.Forms.CheckBox
$atlasUI.Text = 'Localizar algunas texturas de menús (experimental; vista previa recomendada)'
$atlasUI.Location = [System.Drawing.Point]::new(32,543)
$atlasUI.Size = [System.Drawing.Size]::new(770,26)
$atlasUI.Checked = $false
$form.Controls.Add($atlasUI)
$reductions = New-Object System.Windows.Forms.CheckBox
$reductions.Text = 'Aplicar abreviaciones v0.12 (experimentales; requieren revisión editorial)'
$reductions.Location = [System.Drawing.Point]::new(32,573)
$reductions.Size = [System.Drawing.Size]::new(780,26)
$reductions.Checked = $false
$form.Controls.Add($reductions)
$scripts = New-Object System.Windows.Forms.CheckBox
$scripts.Text = 'Integrar scripts de eventos y crear carpeta FINAL para PPSSPP (recomendado)'
$scripts.Location = [System.Drawing.Point]::new(32,602)
$scripts.Size = [System.Drawing.Size]::new(800,26)
$scripts.Checked = $true
$form.Controls.Add($scripts)
$scriptPhase = New-Object System.Windows.Forms.CheckBox
$scriptPhase.Text = 'v0.16: ENSAYO de las 14 referencias CP932 (riesgo de escenas; NO release)'
$scriptPhase.Location = [System.Drawing.Point]::new(52,630)
$scriptPhase.Size = [System.Drawing.Size]::new(780,26)
$scriptPhase.Checked = $false
$scriptPhase.Enabled = $false
$form.Controls.Add($scriptPhase)
$preserveEboot = New-Object System.Windows.Forms.CheckBox
$preserveEboot.Text = 'Prueba gráfica: conservar EBOOT y atlas de interfaz originales (menos menús en español)'
$preserveEboot.Location = [System.Drawing.Point]::new(32,660)
$preserveEboot.Size = [System.Drawing.Size]::new(800,28)
$preserveEboot.Checked = $true
$form.Controls.Add($preserveEboot)
$preserveEboot.Add_CheckedChanged({
  if ($preserveEboot.Checked) {$atlasUI.Checked = $false}
  $atlasUI.Enabled = (-not $preserveEboot.Checked) -and (-not $script:process)
})
$atlasUI.Enabled = $false
$scripts.Add_CheckedChanged({$scriptPhase.Enabled = $scripts.Checked -and (-not $fontOnly.Checked); if(-not $scripts.Checked){$scriptPhase.Checked = $false}})
$safetyNote = LabelAt 'El aislamiento gráfico sirve para investigar; NO confirma que los glitches desaparezcan.' 30 699 800 17 $false
$safetyNote.ForeColor = $muted
$safetyNote.Font = [System.Drawing.Font]::new('Segoe UI', 8)
$btnStart = ButtonAt 'INICIAR PARCHEO' 28 720 228 42 $accent
$btnCancel = ButtonAt 'Cancelar' 270 720 115 42 $navy2
$btnCancel.Enabled = $false
$btnOpen = ButtonAt 'Abrir salida' 699 720 132 42 $navy2

$progress = New-Object System.Windows.Forms.ProgressBar
$progress.Location = [System.Drawing.Point]::new(28,773)
$progress.Size = [System.Drawing.Size]::new(803,10)
$progress.Style = [System.Windows.Forms.ProgressBarStyle]::Blocks
$progress.Anchor = [System.Windows.Forms.AnchorStyles]::Top -bor [System.Windows.Forms.AnchorStyles]::Left -bor [System.Windows.Forms.AnchorStyles]::Right
$form.Controls.Add($progress)
$status = LabelAt 'Listo para seleccionar los archivos.' 27 790 780 23 $false
$status.ForeColor = $muted
$status.Anchor = [System.Windows.Forms.AnchorStyles]::Bottom -bor [System.Windows.Forms.AnchorStyles]::Left -bor [System.Windows.Forms.AnchorStyles]::Right
$log = New-Object System.Windows.Forms.TextBox
$log.Multiline = $true
$log.ScrollBars = [System.Windows.Forms.ScrollBars]::Vertical
$log.ReadOnly = $true
$log.BackColor = [System.Drawing.Color]::FromArgb(236,241,247)
$log.ForeColor = $ink
$log.Font = [System.Drawing.Font]::new('Consolas', 9)
$log.Location = [System.Drawing.Point]::new(28,822)
$log.Size = [System.Drawing.Size]::new(803,115)
$log.Anchor = [System.Windows.Forms.AnchorStyles]::Bottom -bor [System.Windows.Forms.AnchorStyles]::Left -bor [System.Windows.Forms.AnchorStyles]::Right
$form.Controls.Add($log)

function UpdateTargetState {
  $isoEnabled = (-not $radioDLC.Checked)
  $dlcEnabled = (-not $radioISO.Checked)
  $isoBox.Enabled = $isoEnabled
  $isoPick.Enabled = $isoEnabled
  $isoLabel.Enabled = $isoEnabled
  $dlcBox.Enabled = $dlcEnabled
  $dlcPick.Enabled = $dlcEnabled
  $dlcLabel.Enabled = $dlcEnabled
}
$radioBoth.Add_CheckedChanged({UpdateTargetState})
$radioISO.Add_CheckedChanged({UpdateTargetState})
$radioDLC.Add_CheckedChanged({UpdateTargetState})

function SetBusy([bool]$busy) {
  $btnStart.Enabled = -not $busy
  $btnCancel.Enabled = $busy
  $isoPick.Enabled = (-not $busy) -and (-not $radioDLC.Checked)
  $dlcPick.Enabled = (-not $busy) -and (-not $radioISO.Checked)
  $outPick.Enabled = -not $busy
  $isoBox.ReadOnly = $busy
  $dlcBox.ReadOnly = $busy
  $outBox.ReadOnly = $busy
  $radioBoth.Enabled = -not $busy
  $radioISO.Enabled = -not $busy
  $radioDLC.Enabled = -not $busy
  $fontOnly.Enabled = -not $busy
  $includeInvestigation.Enabled = (-not $busy) -and (-not $fontOnly.Checked)
  $atlasUI.Enabled = (-not $busy) -and (-not $preserveEboot.Checked)
  $preserveEboot.Enabled = -not $busy
  $reductions.Enabled = (-not $busy) -and (-not $fontOnly.Checked)
  $scripts.Enabled = (-not $busy) -and (-not $fontOnly.Checked)
  $scriptPhase.Enabled = (-not $busy) -and (-not $fontOnly.Checked) -and $scripts.Checked
  if ($busy) {$progress.Style = [System.Windows.Forms.ProgressBarStyle]::Marquee}
  else {$progress.Style = [System.Windows.Forms.ProgressBarStyle]::Blocks}
}

$timer = New-Object System.Windows.Forms.Timer
$timer.Interval = 600
$timer.Add_Tick({
  if ($script:logFile -and [System.IO.File]::Exists($script:logFile)) {
    try {
      $stream = New-Object System.IO.FileStream($script:logFile, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::ReadWrite)
      $reader = New-Object System.IO.StreamReader($stream, [System.Text.Encoding]::UTF8)
      try {$newText = $reader.ReadToEnd()} finally {$reader.Close();$stream.Close()}
      if ($newText -ne $script:previousLog) {
        $script:previousLog = $newText
        if ($newText.Length -gt 20000) {$newText = $newText.Substring($newText.Length-20000)}
        $log.Text = $newText
        $log.SelectionStart = $log.TextLength
        $log.ScrollToCaret()
      }
    } catch {}
  }
  if ($script:process -and $script:process.HasExited) {
    $timer.Stop()
    $exitCode = $script:process.ExitCode
    $script:process.Dispose()
    $script:process = $null
    SetBusy $false
    if ($script:cancelled) {
      $status.Text = 'Parcheo cancelado. Los originales no se modificaron.'
      $status.ForeColor = [System.Drawing.Color]::DarkOrange
    } elseif ($exitCode -eq 0) {
      $status.Text = 'Proceso terminado. Usa JUEGO_PARA_PPSSPP_V0174 (si activaste scripts).'
      $status.ForeColor = $accent
      $detail = 'Se han creado archivos experimentales. Consulta resumen.json y reporte_por_unidad.csv. El parcheo no certifica que el juego se muestre completamente en espanol.'
      $summary = [System.IO.Path]::Combine($outBox.Text,'resumen.json')
      if ([System.IO.File]::Exists($summary)) {
        try {
          $d = [System.IO.File]::ReadAllText($summary,[System.Text.Encoding]::UTF8) | ConvertFrom-Json
          $detail = "Cadenas modificadas: $($d.cadenas_modificadas)`nMenús EBOOT corregidos: $($d.menus_eboot_ascii_aplicados)`nAtlas UI: $($d.texturas_interfaz_localizadas.PSObject.Properties.Count) paquetes`nUnidades bloqueadas por limites técnicos: $($d.unidades_bloqueadas)`nUnidades con resegmentación pendiente: $($d.unidades_sin_resegmentar)`n`nConsulta reporte_por_unidad.csv para conocer los detalles. Cuatro rótulos narrativos de script localizados; los vídeos y el logotipo conservan su imagen original. El resultado necesita pruebas en PPSSPP."
        } catch {}
      }
      [System.Windows.Forms.MessageBox]::Show($form,$detail,'Parcheo terminado',[System.Windows.Forms.MessageBoxButtons]::OK,[System.Windows.Forms.MessageBoxIcon]::Information) | Out-Null
    } else {
      $status.Text = "Error durante el parcheo (codigo $exitCode). Consulta el registro."
      $status.ForeColor = [System.Drawing.Color]::Firebrick
      $reason = 'Consulta el registro en pantalla y en la carpeta de salida.'
      try {
        if ([System.IO.File]::Exists($script:logFile)) {
          $raw = [System.IO.File]::ReadAllText($script:logFile,[System.Text.Encoding]::UTF8)
          $last = @($raw -split '[\r\n]+' | Where-Object { $_.StartsWith('ERROR:') } | Select-Object -Last 1)
          if ($last.Count -gt 0 -and -not [string]::IsNullOrWhiteSpace($last[0])) {
            $reason = [string]$last[0]
            if ($reason.Length -gt 1200) {$reason = $reason.Substring(0,1200)}
          }
        }
      } catch {}
      [System.Windows.Forms.MessageBox]::Show($form,"Parcheo interrumpido (codigo $exitCode).`n`n$reason`n`nNo se han sobrescrito tus archivos originales.",'Parcheo interrumpido',[System.Windows.Forms.MessageBoxButtons]::OK,[System.Windows.Forms.MessageBoxIcon]::Warning) | Out-Null
    }
  }
})

$btnStart.Add_Click({
  if ($script:process) {return}
  $wantIso = (-not $radioDLC.Checked)
  $wantDlc = (-not $radioISO.Checked)
  $iso = $isoBox.Text.Trim().Trim('"')
  $dlc = $dlcBox.Text.Trim().Trim('"')
  $dest = $outBox.Text.Trim().Trim('"')
  if ($wantIso -and (-not [System.IO.File]::Exists($iso) -or [System.IO.Path]::GetExtension($iso).ToLowerInvariant() -ne '.iso')) {
    [System.Windows.Forms.MessageBox]::Show($form,'Selecciona una ISO .iso existente. Si tienes un archivo .7z, extraelo primero.','Falta la ISO') | Out-Null;return
  }
  if ($wantDlc) {
    $missing = @()
    for ($i=0;$i -lt 4;$i++) {
      $filename = 'DL_JP_{0:00}.EDAT' -f $i
      if (-not [System.IO.File]::Exists([System.IO.Path]::Combine($dlc,$filename))) {$missing += $filename}
    }
    if ($missing.Count -gt 0) {
      [System.Windows.Forms.MessageBox]::Show($form,"La carpeta DLC debe contener los cuatro archivos EDAT.`nFaltan: $($missing -join ', ')",'Carpeta DLC no valida') | Out-Null;return
    }
  }
  if ([string]::IsNullOrWhiteSpace($dest)) {
    [System.Windows.Forms.MessageBox]::Show($form,'Selecciona una carpeta de salida.','Falta la salida') | Out-Null;return
  }
  if ($scriptPhase.Checked) {
    $answer = [System.Windows.Forms.MessageBox]::Show($form,
      'La fase experimental puede alterar la ejecución de escenas. No se ha validado PPSSPP. Se crearán copias independientes. ¿Deseas continuar?',
      'AVISO: 14 referencias sin certificación',
      [System.Windows.Forms.MessageBoxButtons]::YesNo,
      [System.Windows.Forms.MessageBoxIcon]::Warning)
    if ($answer -ne [System.Windows.Forms.DialogResult]::Yes) {return}
  }
  try {
    [System.IO.Directory]::CreateDirectory($dest) | Out-Null
    $cfgDir = [System.IO.Path]::Combine([System.IO.Path]::GetTempPath(),'LaPucelle_ES_GUI')
    [System.IO.Directory]::CreateDirectory($cfgDir) | Out-Null
    $session = [guid]::NewGuid().ToString('N')
    $script:cfgFile = [System.IO.Path]::Combine($cfgDir,$session+'.json')
    $script:logFile = [System.IO.Path]::Combine($cfgDir,$session+'.log')
    $config = @{
      iso = $(if ($wantIso) {$iso} else {''})
      dlc = $(if ($wantDlc) {$dlc} else {''})
      output = $dest
      fontOnly = [bool]$fontOnly.Checked
      investigation = [bool]$includeInvestigation.Checked
      segment = $true
      atlas = [bool]$atlasUI.Checked
      reductions = [bool]$reductions.Checked
      scripts = [bool]$scripts.Checked
      preserveEboot = [bool]$preserveEboot.Checked
      scriptMode = $(if ($scriptPhase.Checked) {'fase'} else {'conservador'})
      log = $script:logFile
    } | ConvertTo-Json -Compress
    [System.IO.File]::WriteAllText($script:cfgFile, $config, (New-Object System.Text.UTF8Encoding($false)))
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $Executable
    $psi.Arguments = '--worker --config "' + $script:cfgFile + '"'
    $psi.CreateNoWindow = $true
    $psi.UseShellExecute = $false
    $psi.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Hidden
    $script:process = [System.Diagnostics.Process]::Start($psi)
    if (-not $script:process) {throw 'No se pudo iniciar el proceso de parcheo.'}
    $script:cancelled = $false
    $script:previousLog = ''
    $log.Text = 'Preparando recursos y comprobando los archivos...'
    $status.Text = 'Procesando copias. Puede requerir varios minutos.'
    $status.ForeColor = $blue
    SetBusy $true
    $timer.Start()
  } catch {
    SetBusy $false
    $status.Text = 'No se pudo iniciar el proceso.'
    [System.Windows.Forms.MessageBox]::Show($form, $_.Exception.Message, 'Error al iniciar') | Out-Null
  }
})

$btnCancel.Add_Click({
  if (-not $script:process -or $script:process.HasExited) {return}
  $r = [System.Windows.Forms.MessageBox]::Show($form,'Se detendra el proceso en curso. Los archivos originales no se alteran; las copias incompletas pueden quedar en la salida.','Cancelar parcheo',[System.Windows.Forms.MessageBoxButtons]::YesNo,[System.Windows.Forms.MessageBoxIcon]::Question)
  if ($r -eq [System.Windows.Forms.DialogResult]::Yes) {
    $script:cancelled = $true
    $pidNum = $script:process.Id
    try {& "$env:WINDIR\System32\taskkill.exe" /PID $pidNum /T /F 2>&1 | Out-Null} catch {}
  }
})
$btnOpen.Add_Click({
  $p = $outBox.Text.Trim().Trim('"')
  if (-not [System.IO.Directory]::Exists($p)) {[System.IO.Directory]::CreateDirectory($p) | Out-Null}
  [System.Diagnostics.Process]::Start('explorer.exe', ('"'+$p+'"')) | Out-Null
})
$form.Add_FormClosing({
  if ($script:process -and -not $script:process.HasExited) {
    $r = [System.Windows.Forms.MessageBox]::Show($form,'Hay un parcheo en curso. ¿Deseas cancelarlo y salir?','Parcheo activo',[System.Windows.Forms.MessageBoxButtons]::YesNo)
    if ($r -ne [System.Windows.Forms.DialogResult]::Yes) {$_.Cancel = $true;return}
    try {& "$env:WINDIR\System32\taskkill.exe" /PID $script:process.Id /T /F 2>&1 | Out-Null} catch {}
  }
})

UpdateTargetState
[void]$form.ShowDialog()
