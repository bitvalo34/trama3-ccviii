param(
 [Parameter(Mandatory=$true)][ValidateSet('BBB-A','BBB-B')][string]$Placa,
 [ValidateSet('Local','SSH','Serial')][string]$Modo='Local',
 [string]$Paquete,
 [ValidatePattern('^[a-zA-Z0-9_.-]+@[a-zA-Z0-9_.:-]+$')][string]$Destino='debian@192.168.7.2',
 [ValidatePattern('^COM[0-9]+$')][string]$Puerto
)
$ErrorActionPreference='Stop'
# No cambia drivers, red ni firmware. No guarda contrasenas.
Write-Host "Placa declarada: $Placa. Conectar SOLO esa BBB."
Get-PnpDevice -PresentOnly | Where-Object { $_.Class -in @('Ports','Net') -and $_.FriendlyName -match 'USB|RNDIS|serial|CDC' } | Select-Object Status,Class,FriendlyName
if ($Modo -eq 'Local') {
 Write-Host 'Seleccione paquete .tar.gz ya entregado. Use -Modo SSH o -Modo Serial para transferir.'
 return
}
if (!$Paquete -or !(Test-Path -LiteralPath $Paquete -PathType Leaf)) { throw 'Falta paquete .tar.gz' }
if ([IO.Path]::GetFileName($Paquete) -notmatch '\.tar\.gz$') { throw 'Transferir el archivo tar.gz, no el ZIP' }
Get-FileHash -Algorithm SHA256 -LiteralPath $Paquete
if ($Modo -eq 'SSH') {
 # Carpeta unica; no sobrescribir trabajo previo.
 $nombreBBB='trama3-t06-t08-'+[guid]::NewGuid().ToString('N').Substring(0,8)
 & ssh $Destino "mkdir -m 700 $nombreBBB"
 if($LASTEXITCODE -ne 0){throw 'SSH no creo destino; revisar acceso existente'}
 & scp -- $Paquete "${Destino}:$nombreBBB/paquete.tar.gz"
 if($LASTEXITCODE -ne 0){throw 'Transferencia incompleta'}
 & ssh $Destino "tar -xzf $nombreBBB/paquete.tar.gz -C $nombreBBB && cd $nombreBBB && sha256sum -c SHA256SUMS"
 if($LASTEXITCODE -ne 0){throw 'Integridad/extraccion fallo; no ejecutar pruebas'}
 Write-Host "Entrada Debian: cd ~/$nombreBBB"
} else {
 if(!$Puerto){throw 'Especificar puerto COM observado'}
 & "$PSScriptRoot/Transferir-Consola.ps1" -Puerto $Puerto -Accion Enviar -Archivo $Paquete
}
