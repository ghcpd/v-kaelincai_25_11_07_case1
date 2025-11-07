# PowerShell wrapper for running the full test suite
Write-Host "Running Project A PreChange tests..."
Push-Location Project_A_PreChange
bash run_tests.sh
Pop-Location

Write-Host "Running Project B PostChange tests..."
Push-Location Project_B_PostChange
bash run_tests.sh
Pop-Location

Write-Host 'Generating compare report with Python'
python -c "import scripts.compare_results as c; print('ok')" || python scripts/compare_results.py
Write-Host 'Done. See compare_report.md and results/*.json'
