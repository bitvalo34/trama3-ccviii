param(
 [Parameter(Mandatory=$true)][ValidatePattern('^COM[0-9]+$')][string]$Puerto,
 [Parameter(Mandatory=$true)][ValidateSet('Enviar','Recibir')][string]$Accion,
 [Parameter(Mandatory=$true)][string]$Archivo,
 [ValidateSet('BBB-A','BBB-B')][string]$Placa='BBB-B'
)
# Transporte de ARCHIVOS, complementa T04-ConsolaUSB.ps1 (diagnostico individual).
# Primero iniciar sesion Debian en PuTTY y CERRAR PuTTY dejando shell autenticada.
$ErrorActionPreference='Stop'
$spBBB=[IO.Ports.SerialPort]::new($Puerto,115200,[IO.Ports.Parity]::None,8,[IO.Ports.StopBits]::One)
$spBBB.Handshake=[IO.Ports.Handshake]::None
$spBBB.DtrEnable=$true
$spBBB.ReadTimeout=1000
$spBBB.WriteTimeout=10000
$spBBB.Encoding=[Text.Encoding]::ASCII
$sttyBBB=$null
function Comando-ArchivoBBB([string]$cmd,[int]$Timeout=60) {
 $tokenBBB='T06_END_'+[guid]::NewGuid().ToString('N')
 $spBBB.Write($cmd+"; printf '\n"+$tokenBBB+" %s\n' "+'$?'+"`r")
 $clockBBB=[Diagnostics.Stopwatch]::StartNew()
 $textBBB=''
 while($clockBBB.Elapsed.TotalSeconds -lt $Timeout){
  if($spBBB.BytesToRead -gt 0){$textBBB+=$spBBB.ReadExisting()}
  if($textBBB -match ("(?m)^"+$tokenBBB+" ([0-9]+)\r?$")){
   if([int]$Matches[1] -ne 0){throw 'Comando de transporte fallo; no ejecutar paquete parcial'}
   return $textBBB
  }
  Start-Sleep -Milliseconds 20
 }
 throw 'Timeout de consola. Recuperar terminal; no continuar ni repetir pruebas activas.'
}
try {
 $spBBB.Open()
 # CR real, no secuencia literal de shell.
 $spBBB.Write([string][char]13)
 Start-Sleep -Milliseconds 200
 $null=$spBBB.ReadExisting()
 $osBBB=Comando-ArchivoBBB 'uname -s' 5
 if($osBBB -notmatch '(?m)^Linux\r?$'){throw 'Inicie sesion en PuTTY y cierre PuTTY antes de transferir'}
 $null=Comando-ArchivoBBB 'cd "$HOME"'
 $sttyOutBBB=Comando-ArchivoBBB 'stty -g'
 $sttyBBB=($sttyOutBBB -split "\r?\n" | Where-Object {$_ -match '^[0-9a-f:]+$'} | Select-Object -First 1)
 if(!$sttyBBB){throw 'No se obtuvo estado de terminal'}
 $null=Comando-ArchivoBBB 'stty -echo'
 if($Accion -eq 'Enviar'){
  $bytesBBB=[IO.File]::ReadAllBytes((Resolve-Path -LiteralPath $Archivo))
  if($bytesBBB.Length -gt 8MB){throw 'Paquete >8MB: usar microSD/USB existente o SSH; no saturar consola'}
  $b64BBB=[Convert]::ToBase64String($bytesBBB)
  $dirBBB='trama3-t06-t08-'+[guid]::NewGuid().ToString('N').Substring(0,8)
  $null=Comando-ArchivoBBB ("umask 077; mkdir "+$dirBBB)
  for($offBBB=0;$offBBB -lt $b64BBB.Length;$offBBB+=768){
   $chunkBBB=$b64BBB.Substring($offBBB,[Math]::Min(768,$b64BBB.Length-$offBBB))
   $null=Comando-ArchivoBBB ("printf %s '"+$chunkBBB+"' >> "+$dirBBB+"/paquete.b64")
  }
  $shaBBB=[Security.Cryptography.SHA256]::Create()
  try {$hashBBB=([BitConverter]::ToString($shaBBB.ComputeHash($bytesBBB))).Replace('-','').ToLowerInvariant()} finally {$shaBBB.Dispose()}
  $null=Comando-ArchivoBBB ("base64 -d "+$dirBBB+"/paquete.b64 > "+$dirBBB+"/paquete.tar.gz && printf '%s  %s\n' "+$hashBBB+" "+$dirBBB+"/paquete.tar.gz | sha256sum -c -")
  $null=Comando-ArchivoBBB ("tar -xzf "+$dirBBB+"/paquete.tar.gz -C "+$dirBBB+" && cd "+$dirBBB+" && sha256sum -c SHA256SUMS && cd ..")
  Write-Host "Paquete verificado. En Debian: cd ~/$dirBBB"
 } else {
  $remoteBBB='/tmp/trama3-evidencias-'+$Placa+'.tar.gz'
  $null=Comando-ArchivoBBB ("test -d trama3-resultados/"+$Placa+" && tar -czf "+$remoteBBB+" -C trama3-resultados "+$Placa)
  $payloadBBB=Comando-ArchivoBBB ("printf 'DATA_BEGIN\n'; base64 "+$remoteBBB+"; printf 'DATA_END\n'") 300
  $matchBBB=[regex]::Match($payloadBBB,'(?s)DATA_BEGIN\r?\n(.*?)DATA_END')
  if(!$matchBBB.Success){throw 'Respuesta sin delimitadores'}
  $receivedBBB=[Convert]::FromBase64String($matchBBB.Groups[1].Value)
  $digestBBB=Comando-ArchivoBBB ("sha256sum "+$remoteBBB)
  $matchHashBBB=[regex]::Match($digestBBB,'(?m)^([0-9a-f]{64})\s')
  $shaBBB=[Security.Cryptography.SHA256]::Create()
  try {$localHashBBB=([BitConverter]::ToString($shaBBB.ComputeHash($receivedBBB))).Replace('-','').ToLowerInvariant()} finally {$shaBBB.Dispose()}
  if(!$matchHashBBB.Success -or $localHashBBB -ne $matchHashBBB.Groups[1].Value){throw 'Hash de evidencia no coincide'}
  if(Test-Path -LiteralPath $Archivo){throw 'No sobrescribir evidencia existente'}
  [IO.File]::WriteAllBytes([IO.Path]::GetFullPath($Archivo),$receivedBBB)
 }
} finally {
 if($spBBB.IsOpen){
  if($sttyBBB){
   try {$spBBB.Write("stty "+$sttyBBB+[char]13)} catch {Write-Warning 'Recuperar eco con stty sane en consola'}
  }
  $spBBB.Close()
 }
 $spBBB.Dispose()
}
