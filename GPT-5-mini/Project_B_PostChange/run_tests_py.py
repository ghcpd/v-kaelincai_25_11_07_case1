import sys
import runpy
import os

sys.path.insert(0, os.getcwd())
runpy.run_path('tests/test_post_change.py', run_name='__main__')
