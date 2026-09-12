#!/usr/bin/env python3
# Copyright (c) 2026 zsecureweb Contributors
# License: AGPLv3

import json
import os
import subprocess
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERSION_FILE = os.path.join(ROOT_DIR, "version.json")
TOOLS_DIR = os.path.join(ROOT_DIR, "tools")
DEPOT_TOOLS_DIR = os.path.join(TOOLS_DIR, "depot_tools")
THIRD_PARTY_DIR = os.path.join(ROOT_DIR, "thirdParty", "chromium")
CHROMIUM_SRC = os.path.join(THIRD_PARTY_DIR, "src")

def load_manifest():
    with open(VERSION_FILE, "r") as f:
        return json.load(f)

def get_env():
    """Builds a hermetic environment with local depot_tools locked."""
    env = os.environ.copy()
    env["PATH"] = DEPOT_TOOLS_DIR + os.path.pathsep + env.get("PATH", "")
    env["DEPOT_TOOLS_UPDATE"] = "0"  # Prevent unpinned auto-updates
    env["DEPOT_TOOLS_WIN_TOOLCHAIN"] = "0"
    return env

def sync_depot_tools(manifest):
    """Syncs depot_tools and locks it to an exact commit hash."""
    depot_hash = manifest["depot_tools"]["commit_hash"]
    print(f"=== Syncing depot_tools to Hash: {depot_hash} ===")
    
    if not os.path.exists(DEPOT_TOOLS_DIR):
        subprocess.run([
            "git", "clone", 
            "https://chromium.googlesource.com/chromium/tools/depot_tools.git", 
            DEPOT_TOOLS_DIR
        ], check=True)
    
    subprocess.run(["git", "fetch", "origin"], cwd=DEPOT_TOOLS_DIR, check=True)
    subprocess.run(["git", "checkout", "--force", depot_hash], cwd=DEPOT_TOOLS_DIR, check=True)

def generate_gclient_config(manifest):
    """Generates explicit .gclient file pointing directly to techpoctech/chromium."""
    os.makedirs(THIRD_PARTY_DIR, exist_ok=True)
    gclient_path = os.path.join(THIRD_PARTY_DIR, ".gclient")
    
    fork_url = manifest["chromium"]["upstream_url"]
    
    gclient_content = f"""solutions = [
  {{
    "name": "src",
    "url": "{fork_url}",
    "deps_file": "DEPS",
    "managed": False,
    "custom_deps": {{}},
  }},
]
"""
    with open(gclient_path, "w") as f:
        f.write(gclient_content)

def sync_chromium(manifest):
    """Runs deterministic gclient sync pointing to techpoctech fork."""
    env = get_env()
    generate_gclient_config(manifest)
    
    print("=== Running Hermetic gclient sync ===")
    subprocess.run(
        ["gclient", "sync", "--no-history", "--nohooks"], 
        cwd=THIRD_PARTY_DIR, 
        env=env, 
        check=True
    )
    
    print("=== Running gclient runhooks ===")
    subprocess.run(["gclient", "runhooks"], cwd=THIRD_PARTY_DIR, env=env, check=True)

def main():
    manifest = load_manifest()
    sync_depot_tools(manifest)
    sync_chromium(manifest)
    print("\n[zsecureweb] Workspace successfully synchronized!")

if __name__ == "__main__":
    main()
