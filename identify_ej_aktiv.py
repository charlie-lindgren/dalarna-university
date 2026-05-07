#!/usr/bin/env python3
"""Convenience launcher for qa/identify_ej_aktiv.py."""

from pathlib import Path
import runpy
import sys


if __name__ == "__main__":
    script_path = Path(__file__).resolve().parent / "qa" / "identify_ej_aktiv.py"
    if not script_path.exists():
        raise SystemExit(f"Could not find target script: {script_path}")

    # Keep original CLI args while delegating execution to the real script.
    sys.argv[0] = str(script_path)
    runpy.run_path(str(script_path), run_name="__main__")
