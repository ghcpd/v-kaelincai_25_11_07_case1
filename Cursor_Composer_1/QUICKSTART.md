# Quick Start Guide

## Windows Users

1. **Verify Setup**:
   ```cmd
   python verify_setup.py
   ```

2. **Run Full Evaluation**:
   ```cmd
   run_all.bat
   ```

3. **Or Run Projects Individually**:
   ```cmd
   cd Project_A_PreChange
   setup.bat
   run_tests.bat
   
   cd ..\Project_B_PostChange
   setup.bat
   run_tests.bat
   ```

## Linux/Mac Users

1. **Verify Setup**:
   ```bash
   python3 verify_setup.py
   ```

2. **Run Full Evaluation**:
   ```bash
   bash run_all.sh
   ```

3. **Or Run Projects Individually**:
   ```bash
   cd Project_A_PreChange
   bash setup.sh
   bash run_tests.sh
   
   cd ../Project_B_PostChange
   bash setup.sh
   bash run_tests.sh
   ```

## Expected Output

After running the evaluation, you should see:

- `results/results_pre.json` - Pre-change test results
- `results/results_post.json` - Post-change test results  
- `results/aggregated_metrics.json` - Aggregated metrics
- `compare_report.md` - Detailed comparison report

## Troubleshooting

### Port Already in Use

If you see port errors, kill existing processes:

**Windows**:
```cmd
netstat -ano | findstr :8001
netstat -ano | findstr :8002
taskkill /F /PID <PID>
```

**Linux/Mac**:
```bash
lsof -i :8001
lsof -i :8002
kill -9 <PID>
```

### Python Not Found

Ensure Python 3.8+ is installed and in PATH:
```bash
python --version
# or
python3 --version
```

### Dependencies Not Installed

Run setup scripts:
```bash
# Project A
cd Project_A_PreChange
bash setup.sh  # or setup.bat on Windows

# Project B
cd Project_B_PostChange
bash setup.sh  # or setup.bat on Windows
```

## What Gets Tested

- ✅ API parameter mapping (sku → sku + regionId + warehouseGroup)
- ✅ Response schema handling (availabilityStatus, syncTimestamp)
- ✅ Async/pending status handling
- ✅ Error handling and fallback mechanisms
- ✅ Input validation
- ✅ Latency and performance metrics
- ✅ Error rates and timeout handling

## Test Duration

Each project takes approximately 10-30 seconds to run, depending on system performance.

