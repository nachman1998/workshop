# run_python_on_csvs.ps1

param (
    [Parameter(Mandatory = $true)]
    [string]$InputDir,

    [Parameter(Mandatory = $true)]
    [string]$PythonScript,

    [Parameter(Mandatory = $false)]
    [string]$PythonFilterScript,

    [Parameter(Mandatory = $true)]
    [string]$OutputDir
)

# Create output directory if needed
if (!(Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
}

# Get all CSV files
$csvFiles = Get-ChildItem -Path $InputDir -Filter "*.csv"

# Get all CSV files
foreach ($csvFile in $csvFiles) {

    $baseName = $csvFile.BaseName

    # Output file
    $outputFile = Join-Path $OutputDir ($baseName + "_output")

    # Temp filter CSV
    $filterCsv = Join-Path $OutputDir ($baseName + "_Filter_HAR.csv")

    Write-Host "Processing:"
    Write-Host "  CSV: $($csvFile.Name)"

    try {

        # If filter script was provided
        if ($PythonFilterScript) {

            # Find matching HAR file only when needed
            $harFile = Join-Path $InputDir ($baseName + ".har")

            if (!(Test-Path $harFile)) {
                Write-Warning "HAR file not found for $($csvFile.Name), skipping..."
                continue
            }

            Write-Host "  HAR: $(Split-Path $harFile -Leaf)"

            # Run filter script
            python $PythonFilterScript `
                --input "$harFile" `
                --out_name "$filterCsv"

            if (!(Test-Path $filterCsv)) {
                Write-Warning "Filter CSV was not created, skipping..."
                continue
            }

            # Run main script with filter
            python $PythonScript `
                --input "$($csvFile.FullName)" `
                --filter_csv "$filterCsv" `
                --out_file "$outputFile"

            # Remove temp file
            if (Test-Path $filterCsv) {
                Remove-Item $filterCsv
            }

        }
        else {

            # Run main script without filter
            python $PythonScript `
                --input "$($csvFile.FullName)" `
                --All `
                --out_file "$outputFile"
        }

        Write-Host "Saved output to $outputFile"
        Write-Host ""

    }
    catch {
        Write-Error "Failed processing $($csvFile.Name): $_"
    }
}
Write-Host "Done."