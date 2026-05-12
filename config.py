import sys
import os

# Add project root to Python path
sys.dont_write_bytecode = True
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
