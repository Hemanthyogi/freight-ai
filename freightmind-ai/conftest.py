"""
FreightMind AI — pytest conftest.py

Sets up the Python path so that 'src' imports work without installing the package.
"""

import sys
from pathlib import Path

# Add project root to sys.path so `from src.xxx import yyy` works in tests
sys.path.insert(0, str(Path(__file__).parent))
