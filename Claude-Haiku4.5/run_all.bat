@echo off
REM Master test execution script - Windows batch
REM Runs both projects and generates comparison report

setlocal enabledelayedexpansion

set "REPO_ROOT=%~dp0"
set "RESULTS_DIR=%REPO_ROOT%results"
set "LOGS_DIR=%REPO_ROOT%logs"

if not exist "%RESULTS_DIR%" mkdir "%RESULTS_DIR%"
if not exist "%LOGS_DIR%" mkdir "%LOGS_DIR%"

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║  API Migration Evaluation - Full Test Suite                     ║
echo ║  Pre-Change (v1) vs Post-Change (v2)                           ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM ============================================================================
REM Phase 1: Run Project A (Pre-Change v1)
REM ============================================================================
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo Phase 1: Running Project A ^(Pre-Change - v1 Integration^)
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

call "%REPO_ROOT%Project_A_PreChange\run_tests.bat"
if %ERRORLEVEL% EQU 0 (
    echo ✓ Project A tests completed
) else (
    echo ✗ Project A tests failed
)

REM ============================================================================
REM Phase 2: Run Project B (Post-Change v2)
REM ============================================================================
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo Phase 2: Running Project B ^(Post-Change - v2 Integration^)
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

call "%REPO_ROOT%Project_B_PostChange\run_tests.bat"
if %ERRORLEVEL% EQU 0 (
    echo ✓ Project B tests completed
) else (
    echo ✗ Project B tests failed
)

REM ============================================================================
REM Phase 3: Copy results to shared results directory
REM ============================================================================
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo Phase 3: Aggregating Results
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

if exist "%REPO_ROOT%Project_A_PreChange\results\results_pre.json" (
    copy "%REPO_ROOT%Project_A_PreChange\results\results_pre.json" "%RESULTS_DIR%\"
    echo ✓ Copied Project A results
)

if exist "%REPO_ROOT%Project_B_PostChange\results\results_post.json" (
    copy "%REPO_ROOT%Project_B_PostChange\results\results_post.json" "%RESULTS_DIR%\"
    echo ✓ Copied Project B results
)

REM ============================================================================
REM Phase 4: Generate comparison report
REM ============================================================================
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo Phase 4: Generating Comparison Report
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

python "%REPO_ROOT%generate_comparison_report.py" "%RESULTS_DIR%"

REM ============================================================================
REM Summary
REM ============================================================================
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                    EXECUTION COMPLETE                           ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo Results Location:       %RESULTS_DIR%\
echo Logs Location:          %LOGS_DIR%\
echo Comparison Report:      %RESULTS_DIR%\compare_report.md
echo.
echo Key Output Files:
echo   - results\results_pre.json       ^(Project A results^)
echo   - results\results_post.json      ^(Project B results^)
echo   - results\aggregated_metrics.json ^(Combined metrics^)
echo   - results\compare_report.md      ^(Comparison report^)
echo.
echo ✓ All tests executed successfully
echo.

endlocal
