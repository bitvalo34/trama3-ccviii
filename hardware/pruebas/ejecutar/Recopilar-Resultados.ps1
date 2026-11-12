param(
 [Parameter(Mandatory=$true)][ValidateSet('BBB-A','BBB-B')][string]$Placa,
 [ValidateSet('SSH','Serial')][string]$Modo='SSH',
 [ValidatePattern('^[a-zA-Z0-9_.-]+@[a-zA-Z0-9_.:-]+$')][string]$Destino='debian@192.168.7.2',
 [ValidatePattern('^COM[0-9]+$')][string]$Puerto,
 [string]$Carpeta=(Join-Path $PWD 'evidencias')
)
$ErrorActionPreference='Stop'
$salidaBBB=Join-Path $Carpeta ($Placa+'-'+(Get-Date -Format 'yyyyMMdd-HHmmss')+'.tar.gz')
New-Item -ItemType Directory -Force -Path $Carpeta | Out-Null
if($Modo -eq 'SSH') {
 & ssh $Destino "test -d trama3-resultados/$Placa && tar -czf /tmp/trama3-evidencias-$Placa.tar.gz -C trama3-resultados $Placa"
 if($LASTEXITCODE -ne 0){throw 'Sin resultados o fallo al empaquetar'}
 & scp "${Destino}:/tmp/trama3-evidencias-$Placa.tar.gz" $salidaBBB
 if($LASTEXITCODE -ne 0){throw 'Recuperacion fallo'}
} else {
 if(!$Puerto){throw 'Especificar puerto COM'}
 & "$PSScriptRoot/Transferir-Consola.ps1" -Puerto $Puerto -Accion Recibir -Archivo $salidaBBB -Placa $Placa
}
Get-FileHash -LiteralPath $salidaBBB -Algorithm SHA256
Write-Host "Evidencias guardadas: $salidaBBB. Revisar antes de compartir; no publicar logs privados."
