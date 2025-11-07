# API Migration Evaluation

This repository contains two projects:
- Project_A_PreChange — legacy integration with /api/v1/checkStock
- Project_B_PostChange — migration to /api/v2/stock/availability with region/warehouse and async handling

Use `./run_all.sh` to run both projects' tests and generate `compare_report.md`.
