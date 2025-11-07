# PowerShell wrapper to run all tests
Set-StrictMode -Version Latest

Write-Host "Running Project A Pre-Change tests"
Push-Location Project_A_PreChange
./run_tests.sh
Pop-Location

Copy-Item -Path Project_A_PreChange\results\results_pre.json -Destination results\results_pre.json -Force

Write-Host "Running Project B Post-Change tests"
Push-Location Project_B_PostChange
./run_tests.sh
Pop-Location

Copy-Item -Path Project_B_PostChange\results\results_post.json -Destination results\results_post.json -Force

python generate_report.py
Write-Host "Finished. Review compare_report.md and results/aggregated_metrics.json"
