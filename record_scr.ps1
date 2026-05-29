param (
    [Parameter(Mandatory = $true)]
    [string]$PythonScript,

    [Parameter(Mandatory = $true)]
    [int]$Count,

    [Parameter(Mandatory = $true)]
    [string]$CaptureName,

    [Parameter(Mandatory = $false)]
    [string]$Interface = "Wi-Fi",

    [Parameter(Mandatory = $false)]
    [string]$OutputDir = "C:\captures",

    [Parameter(Mandatory = $false)]
    [string]$PythonExe = "python"
)

$TsharkPath = "C:\Program Files\Wireshark\tshark.exe"

# create output folder if missing
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

for ($i = 1; $i -le $Count; $i++) {

    $OutputFile = "$OutputDir\$CaptureName`_$i.pcap"
    $OutputHARFile = "$OutputDir\$CaptureName`_$i.har"
    Write-Host "[$i/$Count] Starting capture -> $OutputFile"

    # start tshark in background
    $process = Start-Process `
        -FilePath $TsharkPath `
        -ArgumentList "-i `"$Interface`" -F pcap -w `"$OutputFile`"" `
        -PassThru `
        -WindowStyle Hidden

    Write-Host "[$i/$Count] Running Python script..."

    # run python script and wait for it to finish
    & $PythonExe $PythonScript --output_name "$OutputHARFile"

    Write-Host "[$i/$Count] Script finished. Stopping capture..."

    # stop capture
    Stop-Process -Id $process.Id -Force

    Write-Host "[$i/$Count] Saved: $OutputFile"
    Write-Host "---"
}

Write-Host "All done. $Count captures saved to $OutputDir"