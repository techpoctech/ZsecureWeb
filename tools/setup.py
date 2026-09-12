#!/usr/bin/env python3
# Copyright (c) 2026 zsecureweb Contributors
# License: AGPLv3

import os
import subprocess
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS_DIR = os.path.join(ROOT_DIR, "tools")
AUTOMATE_SCRIPT = os.path.join(TOOLS_DIR, "automate.py")

def setup():
    print("=== Step 1: Syncing Git Submodules ===")
    subprocess.run(["git", "submodule", "update", "--init", "--recursive"], cwd=ROOT_DIR, check=True)

    print("\n=== Step 2: Running Deterministic Automation Engine ===")
    # Hands off orchestration to automate.py
    subprocess.run([sys.executable, AUTOMATE_SCRIPT], check=True)

if __name__ == "__main__":
    setup()
