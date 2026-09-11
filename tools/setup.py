#!/usr/bin/env python3
import os
import subprocess

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEPOT_TOOLS = os.path.join(ROOT_DIR, "tools", "depot_tools")
CHROMIUM_SRC = os.path.join(ROOT_DIR, "thirdParty", "chromium", "src")

def run(cmd, cwd=ROOT_DIR):
    subprocess.run(cmd, cwd=cwd, check=True)

def setup():
    # 1. Initialize Git Submodules
    print("=== Step 1: Syncing Git Submodules ===")
    run(["git", "submodule", "update", "--init", "--recursive"])

    # 2. Fetch depot_tools if missing
    if not os.path.exists(DEPOT_TOOLS):
        print("=== Step 2: Fetching depot_tools ===")
        run(["git", "clone", "https://chromium.googlesource.com/chromium/tools/depot_tools.git", DEPOT_TOOLS])

    # 3. Run gclient sync for third-party dependencies (V8, WebRTC, etc.)
    print("=== Step 3: Syncing Chromium Third-Party Dependencies ===")
    env = os.environ.copy()
    env["PATH"] = DEPOT_TOOLS + os.path.pathsep + env.get("PATH", "")
    run(["gclient", "sync", "--no-history"], cwd=CHROMIUM_SRC, env=env)

if __name__ == "__main__":
    setup()
