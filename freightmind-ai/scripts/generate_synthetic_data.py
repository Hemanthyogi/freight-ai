#!/usr/bin/env python
"""
FreightMind AI — Synthetic Data Generation Script
scripts/generate_synthetic_data.py

Convenience runner for generating all synthetic demo data.

Usage:
    python scripts/generate_synthetic_data.py
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.data.synthetic_generator import save_datasets, print_summary, SYNTHETIC_DIR

if __name__ == "__main__":
    print("\n[FreightMind AI] Running synthetic data generator...")
    saved = save_datasets(output_dir=SYNTHETIC_DIR, verbose=True)
    print_summary(saved)
