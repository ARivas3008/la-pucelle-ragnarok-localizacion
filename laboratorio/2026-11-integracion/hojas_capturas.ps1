$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Drawing
$files=@(Get-ChildItem -LiteralPath (Join-Path $PSScriptRoot 'capturas_usuario_20261116') -File | Sort-Object Name)
$font=[System.Drawing.Font]::new('Arial',12)
for($page=0;$page -lt 6;$page++) {
 $bmp=[System.Drawing.Bitmap]::new(1440,1000)
 $g=[System.Drawing.Graphics]::FromImage($bmp)
 $g.Clear([System.Drawing.Color]::White)
 for($j=0;$j -lt 4;$j++) {
  $i=$page*4+$j
  $im=[System.Drawing.Image]::FromFile($files[$i].FullName)
  $x=($j%2)*720; $y=[int][Math]::Floor($j/2)*500
  $scale=[Math]::Min(720.0/$im.Width,465.0/$im.Height)
  $g.DrawImage($im,[int]$x,[int]($y+30),[int]($im.Width*$scale),[int]($im.Height*$scale))
  $g.DrawString(($i.ToString()+' '+$files[$i].Name),$font,[System.Drawing.Brushes]::Black,$x,$y)
  $im.Dispose()
 }
 $bmp.Save((Join-Path $PSScriptRoot ('informes/capturas_usuario_'+$page+'.png')))
 $g.Dispose();$bmp.Dispose()
}
$font.Dispose()
