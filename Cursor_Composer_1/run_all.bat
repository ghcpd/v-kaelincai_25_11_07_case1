@echo off
REM Master script to run both Project A and Project B tests and generate comparison report (Windows)

echo ==========================================
echo API Migration Evaluation - Full Test Suite
echo ==========================================
echo.

REM Create results directory
if not exist results mkdir results

REM Step 1: Run Project A (Pre-Change) tests
echo ==========================================
echo Step 1: Running Project A - Pre-Change Tests
echo ==========================================
cd Project_A_PreChange
call run_tests.bat
cd ..

REM Step 2: Run Project B (Post-Change) tests
echo.
echo ==========================================
echo Step 2: Running Project B - Post-Change Tests
echo ==========================================
cd Project_B_PostChange
call run_tests.bat
cd ..

REM Step 3: Generate comparison report
echo.
echo ==========================================
echo Step 3: Generating Comparison Report
echo ==========================================

REM Copy results to shared results directory
copy Project_A_PreChange\results\results_pre.json results\ 2>nul
copy Project_B_PostChange\results\results_post.json results\ 2>nul

REM Run comparison script
python generate_comparison_report.py

echo.
echo ==========================================
echo Evaluation Complete!
echo ==========================================
echo Results available in:
echo   - results\results_pre.json
echo   - results\results_post.json
echo   - results\aggregated_metrics.json
echo   - compare_report.md
echo ==========================================
pause

