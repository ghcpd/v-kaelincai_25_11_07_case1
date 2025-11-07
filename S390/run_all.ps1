# Run tests on PowerShell
$ErrorActionPreference = 'Stop'

Push-Location Project_A_PreChange
python -m pip install -r requirements.txt
python -m pytest -q
Pop-Location

Push-Location Project_B_PostChange
python -m pip install -r requirements.txt
python -m pytest -q
Pop-Location

# Copy results
if (!(Test-Path -Path results)) { New-Item -ItemType Directory -Path results }
Copy-Item -Path Project_A_PreChange\results\results_pre.json -Destination results -Force
Copy-Item -Path Project_B_PostChange\results\results_post.json -Destination results -Force

python aggregate_results.py
Write-Host 'All done. See compare_report.md and results/aggregated_metrics.json'
