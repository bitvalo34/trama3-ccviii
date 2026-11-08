param(
 [Parameter(Mandatory=$true)][ValidateSet('A','B')][string]$Placa,
 [Parameter(Mandatory=$true)][ValidatePattern('^COM[0-9]+$')][string]$Puerto,
 [ValidateSet('audit','pin-test','clean-cache','headless')][string]$Accion='audit',
 [switch]$SinCargas
)
# Windows PowerShell 5.1 / PowerShell 7. Credenciales solo por consola local.
$ErrorActionPreference='Stop'
if ($Accion -eq 'pin-test' -and -not $SinCargas) { throw 'Quite todas las cargas de P8/P9 y agregue -SinCargas.' }
$archivoBBB=Join-Path $PSScriptRoot 't04-bbb.sh'
if (!(Test-Path -LiteralPath $archivoBBB)) { throw 'Falta t04-bbb.sh junto a este archivo.' }
$carpetaBBB=Join-Path $env:USERPROFILE ('Documents\TRAMA3-resultados\'+$Placa+'-'+(Get-Date -Format 'yyyyMMdd-HHmmss'))
New-Item -ItemType Directory -Force $carpetaBBB | Out-Null
$serialBBB=[System.IO.Ports.SerialPort]::new($Puerto,115200,[System.IO.Ports.Parity]::None,8,[System.IO.Ports.StopBits]::One)
$serialBBB.DtrEnable=$true
$serialBBB.Handshake=[System.IO.Ports.Handshake]::None
$serialBBB.RtsEnable=$false
$serialBBB.WriteTimeout=5000
$serialBBB.ReadTimeout=1000
$serialBBB.Encoding=[Text.Encoding]::ASCII
$etapaBBB='abrir puerto'
$transporteSanoBBB=$true
$terminalPreparadaBBB=$false
function Enviar-BBB([string]$texto) {
 try { $serialBBB.Write($texto) }
 catch { $script:transporteSanoBBB=$false; throw }
}
function Leer-BBB([int]$ms=700) {
 $relojBBB=[Diagnostics.Stopwatch]::StartNew()
 $textoBBB=''
 while($relojBBB.ElapsedMilliseconds -lt $ms) {
  if($serialBBB.BytesToRead -gt 0){$textoBBB+=$serialBBB.ReadExisting()}
  Start-Sleep -Milliseconds 40
 }
 return $textoBBB
}
function Clave-BBB {
 $secretoBBB=Read-Host 'Contrasena de Debian (no se guardara)' -AsSecureString
 $ptrBBB=[Runtime.InteropServices.Marshal]::SecureStringToBSTR($secretoBBB)
 try {
  Enviar-BBB ([Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptrBBB)+"`r")
 } finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptrBBB);$secretoBBB.Dispose() }
}
function Comando-BBB([string]$comando,[int]$segundos=45) {
 $tokenBBB='T04_END_'+[guid]::NewGuid().ToString('N')
 Enviar-BBB ($comando+"; printf '\n"+$tokenBBB+" %s\n' `$?`r")
 $textoBBB=''
 $relojBBB=[Diagnostics.Stopwatch]::StartNew()
 while($relojBBB.Elapsed.TotalSeconds -lt $segundos) {
  $textoBBB+=Leer-BBB 100
  if($textoBBB -match ("(?m)^"+$tokenBBB+" ([0-9]+)\r?$")) {
   return [pscustomobject]@{Text=$textoBBB;Code=[int]$Matches[1]}
  }
 }
 Enviar-BBB ([string][char]3)
 throw "Tiempo agotado en comando. No continuar cambios. Salida parcial: $textoBBB"
}
try {
 $serialBBB.Open()
 Start-Sleep -Milliseconds 500
 $etapaBBB='contacto inicial'
 Enviar-BBB ([string][char]3)
 Enviar-BBB ("`r")
 $pantallaBBB=Leer-BBB 1000
 for($intentoBBB=0;$intentoBBB -lt 3;$intentoBBB++) {
  if($pantallaBBB -match '(?im)login:\s*$') {
   Enviar-BBB ("debian`r")
   $pantallaBBB=Leer-BBB 1000
  }
  if($pantallaBBB -match '(?im)password:\s*$') {
   Clave-BBB
   $pantallaBBB=Leer-BBB 1500
  }
  if($pantallaBBB -match '(?m)^[^\r\n]*[#$]\s*$'){break}
  Enviar-BBB ("`r")
  $pantallaBBB=Leer-BBB 1000
 }
 if($pantallaBBB -notmatch '(?m)^[^\r\n]*[#$]\s*$'){throw "No aparece terminal Linux. Salida: $pantallaBBB"}
 $etapaBBB='verificar terminal Linux'
 $checkBBB=Comando-BBB 'uname -s'
 if($checkBBB.Text -notmatch '(?m)^Linux\r?$'){throw 'No se verifico Linux.'}
 $etapaBBB='autenticar sudo'
 # sudo puede pedir clave: no escribirla en logs, historial o linea de comandos.
 Enviar-BBB ("sudo -v`r")
 $pantallaBBB=Leer-BBB 1000
 if($pantallaBBB -match '(?i)password'){Clave-BBB;$pantallaBBB=Leer-BBB 1000}
 $sudoBBB=Comando-BBB 'sudo -n true'
 if($sudoBBB.Code -ne 0){
  if($Accion -ne 'audit'){throw 'Sin privilegios sudo. No se aplican cambios.'}
  Write-Host 'Auditoria parcial sin sudo; registrar las comprobaciones inaccesibles.'
 }
 $echoBBB=Comando-BBB 'stty -echo'
 if($echoBBB.Code -ne 0){throw 'No se pudo preparar la terminal.'}
 $terminalPreparadaBBB=$true
 $etapaBBB='transferir archivo'
 $bytesBBB=[Text.Encoding]::UTF8.GetBytes(([IO.File]::ReadAllText($archivoBBB)).Replace("`r`n","`n"))
 $baseBBB=[Convert]::ToBase64String($bytesBBB)
 $rutaBBB='/tmp/trama3-t04-'+[guid]::NewGuid().ToString('N')
 $initBBB=Comando-BBB ("umask 077; mkdir '"+$rutaBBB+"'")
 if($initBBB.Code -ne 0){throw 'No se creo carpeta temporal.'}
 for($offsetBBB=0;$offsetBBB -lt $baseBBB.Length;$offsetBBB+=900){
  $trozoBBB=$baseBBB.Substring($offsetBBB,[Math]::Min(900,$baseBBB.Length-$offsetBBB))
  $envioBBB=Comando-BBB ("printf %s '"+$trozoBBB+"' >> '"+$rutaBBB+"/script.b64'")
  if($envioBBB.Code -ne 0){throw 'Fallo transferencia; no ejecutar archivo parcial.'}
 }
 $decodeBBB=Comando-BBB ("base64 -d '"+$rutaBBB+"/script.b64' > '"+$rutaBBB+"/t04.sh' && bash -n '"+$rutaBBB+"/t04.sh'")
 if($decodeBBB.Code -ne 0){throw 'Archivo incompleto o sintaxis incorrecta.'}
 $prefijoBBB=if($SinCargas){'T04_SIN_CARGAS=SI '}else{''}
 Write-Host "Ejecutando $Accion en la placa declarada $Placa. Puede tardar varios minutos."
 $etapaBBB='ejecutar revision'
 $resultadoBBB=Comando-BBB ($prefijoBBB+"bash '"+$rutaBBB+"/t04.sh' "+$Placa+' '+$Accion) 600
 [IO.File]::WriteAllText((Join-Path $carpetaBBB 'resultado.txt'),$resultadoBBB.Text,[Text.UTF8Encoding]::new($false))
 Write-Host $resultadoBBB.Text
 Write-Host "Codigo final: $($resultadoBBB.Code). Registro local: $carpetaBBB"
} catch {
 $mensajeBBB="Etapa: $etapaBBB. "+$_.Exception.Message
 [IO.File]::WriteAllText((Join-Path $carpetaBBB 'error.txt'),$mensajeBBB,[Text.UTF8Encoding]::new($false))
 Write-Error $mensajeBBB
} finally {
 # No volver a escribir en un enlace averiado ni ocultar el error original.
 if($serialBBB.IsOpen -and $transporteSanoBBB -and $terminalPreparadaBBB){
  try {
   $serialBBB.Write([string][char]3)
   $serialBBB.Write("stty echo"+[char]13)
   Start-Sleep -Milliseconds 300
  } catch { Write-Warning 'No se pudo restaurar eco; recuperar conexion antes de continuar.' }
 }
 try { if($serialBBB.IsOpen){$serialBBB.Close()} } catch { Write-Warning 'El controlador no confirmo cierre del puerto.' }
 try { $serialBBB.Dispose() } catch { Write-Warning 'No se completo liberacion del puerto.' }
}
