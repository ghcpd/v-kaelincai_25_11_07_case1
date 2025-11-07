# Quick Start Guide

## Prerequisites
- Python 3.8+
- pip package manager
- Git (optional, for version control)

## Windows (Recommended)

### Option 1: One-Click Execution (Fastest)
```batch
cd c:\chatWorkspace
run_all.bat
```

This will:
1. Set up Python environments for both projects
2. Install dependencies
3. Start mock API servers
4. Run all tests
5. Generate comparison report
6. Display results

**Expected output**: `results/compare_report.md`

### Option 2: Manual Step-by-Step

**Project A Setup:**
```batch
cd c:\chatWorkspace\Project_A_PreChange
setup.bat
run_tests.bat
```

**Project B Setup:**
```batch
cd c:\chatWorkspace\Project_B_PostChange
setup.bat
run_tests.bat
```

**Generate Report:**
```batch
cd c:\chatWorkspace
python generate_comparison_report.py results
```

---

## macOS/Linux

### Option 1: One-Click Execution
```bash
cd /path/to/repo
bash run_all.sh
```

### Option 2: Manual Step-by-Step
```bash
cd Project_A_PreChange
bash setup.sh
bash run_tests.sh

cd ../Project_B_PostChange
bash setup.sh
bash run_tests.sh

cd ..
python3 generate_comparison_report.py results
```

---

## Viewing Results

After execution completes:

1. **Summary Report (Read this first)**
   ```
   results/compare_report.md
   ```

2. **Raw Results - Project A (v1)**
   ```
   results/results_pre.json
   ```

3. **Raw Results - Project B (v2)**
   ```
   results/results_post.json
   ```

4. **Aggregated Metrics**
   ```
   results/aggregated_metrics.json
   ```

5. **Test Logs**
   ```
   Project_A_PreChange/logs/test_run.log
   Project_B_PostChange/logs/test_run.log
   ```

---

## What Gets Tested?

| Test Case | Focus Area |
|-----------|-----------|
| TC001 | Basic availability check |
| TC002 | Boundary conditions |
| TC003 | Async polling (v2 only) |
| TC004 | Input validation |
| TC005 | Error handling & retries |
| TC006 | Out-of-stock scenarios |
| CART tests | End-to-end cart operations |

---

## Troubleshooting

### Port Already in Use
```
Error: Address already in use
```
**Solution**: Kill existing Python processes
```batch
REM Windows
taskkill /F /IM python.exe

REM Linux/macOS
pkill -f python
```

### Import Errors
```
ImportError: No module named 'flask'
```
**Solution**: Reinstall requirements
```batch
cd Project_A_PreChange
setup.bat
```

### Tests Won't Run
```
pytest: command not found
```
**Solution**: Ensure virtual environment is activated
```batch
Project_A_PreChange\venv\Scripts\activate.bat
pip list  # Should show installed packages
```

---

## Understanding the Reports

### Key Metrics
- **Pass Rate**: % of tests passed (target: 100%)
- **Latency p50**: Median request time (50th percentile)
- **Latency p95**: 95th percentile (slower requests)
- **Fallback Rate**: % of requests using fallback (target: <1%)

### What's Different?
- **v1**: Simple, synchronous, no region awareness
- **v2**: Region-aware, async-capable, with retry logic

### Recommendations
The report includes:
1. Rollout strategy (phased deployment)
2. Observability checklist
3. Common pitfalls and mitigations
4. Production testing guidance

---

## Example Results

### compare_report.md Output
```markdown
# API Migration Evaluation Report

## Executive Summary
Compares Project A (v1) vs Project B (v2)...

## Test Results Summary
| Metric | Project A (v1) | Project B (v2) |
|--------|---|---|
| Tests Passed | 8/8 | 10/10 |
| Pass Rate | 100% | 100% |
| Latency p50 | 145ms | 156ms |
| Latency p95 | 280ms | 320ms |

[Additional analysis and recommendations...]
```

---

## Next Steps

1. **Review Results**
   - Read `results/compare_report.md`
   - Check test logs for details

2. **Understand Differences**
   - v1 behavior vs v2 behavior
   - Performance comparison
   - Error handling improvements

3. **Plan Deployment**
   - Follow phased rollout recommendations
   - Set up observability metrics
   - Prepare feature flag configuration

4. **Deploy to Staging**
   - Use suggested canary strategy
   - Monitor metrics
   - Validate in representative environment

---

## File Locations Summary

| File | Purpose |
|------|---------|
| `run_all.bat` | Master execution script |
| `test_data.json` | Shared test cases |
| `compare_report.md` | Final analysis |
| `results_pre.json` | v1 test results |
| `results_post.json` | v2 test results |
| `aggregated_metrics.json` | Combined metrics |

---

**Created**: November 7, 2025  
**Evaluation**: API Migration (Feature & Improvement)
