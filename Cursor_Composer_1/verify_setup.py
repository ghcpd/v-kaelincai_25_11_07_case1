"""
Verification script to check project setup
"""
import os
import sys

def check_file_exists(filepath, description):
    """Check if a file exists"""
    exists = os.path.exists(filepath)
    status = "✓" if exists else "✗"
    print(f"{status} {description}: {filepath}")
    return exists

def check_directory_exists(dirpath, description):
    """Check if a directory exists"""
    exists = os.path.isdir(dirpath)
    status = "✓" if exists else "✗"
    print(f"{status} {description}: {dirpath}")
    return exists

def main():
    print("=" * 60)
    print("Project Setup Verification")
    print("=" * 60)
    print()
    
    all_ok = True
    
    # Check Project A
    print("Project A - Pre-Change:")
    all_ok &= check_file_exists("Project_A_PreChange/src/cart_service_v1.py", "Service code")
    all_ok &= check_file_exists("Project_A_PreChange/mocks/mock_v1_api.py", "Mock API")
    all_ok &= check_file_exists("Project_A_PreChange/tests/test_pre_change.py", "Test harness")
    all_ok &= check_file_exists("Project_A_PreChange/data/test_data.json", "Test data")
    all_ok &= check_file_exists("Project_A_PreChange/requirements.txt", "Requirements")
    all_ok &= check_file_exists("Project_A_PreChange/setup.sh", "Setup script")
    all_ok &= check_file_exists("Project_A_PreChange/run_tests.sh", "Test runner")
    all_ok &= check_file_exists("Project_A_PreChange/setup.bat", "Windows setup")
    all_ok &= check_file_exists("Project_A_PreChange/run_tests.bat", "Windows test runner")
    print()
    
    # Check Project B
    print("Project B - Post-Change:")
    all_ok &= check_file_exists("Project_B_PostChange/src/cart_service_v2.py", "Service code")
    all_ok &= check_file_exists("Project_B_PostChange/mocks/mock_v2_api.py", "Mock API")
    all_ok &= check_file_exists("Project_B_PostChange/tests/test_post_change.py", "Test harness")
    all_ok &= check_file_exists("Project_B_PostChange/data/test_data.json", "Test data")
    all_ok &= check_file_exists("Project_B_PostChange/data/expected_postchange.json", "Expected outputs")
    all_ok &= check_file_exists("Project_B_PostChange/requirements.txt", "Requirements")
    all_ok &= check_file_exists("Project_B_PostChange/setup.sh", "Setup script")
    all_ok &= check_file_exists("Project_B_PostChange/run_tests.sh", "Test runner")
    all_ok &= check_file_exists("Project_B_PostChange/setup.bat", "Windows setup")
    all_ok &= check_file_exists("Project_B_PostChange/run_tests.bat", "Windows test runner")
    print()
    
    # Check shared artifacts
    print("Shared Artifacts:")
    all_ok &= check_file_exists("test_data.json", "Canonical test data")
    all_ok &= check_file_exists("run_all.sh", "Master execution script")
    all_ok &= check_file_exists("run_all.bat", "Windows master script")
    all_ok &= check_file_exists("generate_comparison_report.py", "Report generator")
    all_ok &= check_file_exists("README.md", "Documentation")
    all_ok &= check_directory_exists("results", "Results directory")
    print()
    
    # Check Python dependencies
    print("Python Dependencies:")
    try:
        import requests
        print("✓ requests module available")
    except ImportError:
        print("✗ requests module not found")
        all_ok = False
    
    try:
        import flask
        print("✓ flask module available")
    except ImportError:
        print("✗ flask module not found")
        all_ok = False
    
    print()
    print("=" * 60)
    if all_ok:
        print("✓ All checks passed! Project is ready to use.")
        print()
        print("Next steps:")
        print("  Linux/Mac: bash run_all.sh")
        print("  Windows:   run_all.bat")
    else:
        print("✗ Some checks failed. Please review the output above.")
        sys.exit(1)
    print("=" * 60)

if __name__ == "__main__":
    main()

