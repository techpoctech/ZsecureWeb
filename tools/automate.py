#!/usr/bin/env python3
# Copyright (c) 2026 ZsecureWeb Contributors
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

def get_env(manifest):
    """Configures a hermetic execution environment."""
    env = os.environ.copy()
    # Prepend local depot_tools to PATH
    env["PATH"] = DEPOT_TOOLS_DIR + os.path.pathsep + env.get("PATH", "")
    # Disable automatic depot_tools self-updates to preserve determinism
    env["DEPOT_TOOLS_UPDATE"] = "0"
    env["DEPOT_TOOLS_WIN_TOOLCHAIN"] = "0"
    return env

def run_cmd(cmd, cwd=None, env=None):
    print(f"\n[ZsecureAutomate] Executing: {' '.join(cmd)}")
    subprocess.run(cmd, cwd=cwd, env=env, check=True)

def sync_depot_tools(manifest):
    """Syncs depot_tools to an exact immutable commit hash."""
    depot_hash = manifest["depot_tools"]["commit_hash"]
    print(f"=== Syncing depot_tools to Hash: {depot_hash} ===")
    
    if not os.path.exists(DEPOT_TOOLS_DIR):
        run_cmd(["git", "clone", "https://chromium.googlesource.com/chromium/tools/depot_tools.git", DEPOT_TOOLS_DIR])
    
    # Detach HEAD at exact commit
    run_cmd(["git", "fetch", "origin"], cwd=DEPOT_TOOLS_DIR)
    run_cmd(["git", "checkout", "--force", depot_hash], cwd=DEPOT_TOOLS_DIR)

def generate_gclient_config(manifest):
    """Generates an explicit .gclient file to lock Chromium dependencies."""
    os.makedirs(THIRD_PARTY_DIR, exist_ok=True)
    gclient_path = os.path.join(THIRD_PARTY_DIR, ".gclient")
    
    chrom_url = manifest["chromium"]["upstream_url"]
    
    gclient_content = f"""solutions = [
  {{
    "name": "src",
    "url": "{chrom_url}",
    "deps_file": "DEPS",
    "managed": False,
    "custom_deps": {{}},
  }},
]
"""
    with open(gclient_path, "w") as f:
        f.write(gclient_content)
    print(f"[ZsecureAutomate] Wrote deterministic .gclient config.")

def sync_chromium_tree(manifest):
    """Checks out the pinned Chromium release tag and runs gclient sync."""
    env = get_env(manifest)
    tag = manifest["chromium"]["version_tag"]
    
    generate_gclient_config(manifest)
    
    if not os.path.exists(CHROMIUM_SRC):
        print(f"=== Initializing Chromium Source Target Tag: {tag} ===")
        run_cmd(["fetch", "--no-history", "chrome"], cwd=THIRD_PARTY_DIR, env=env)

    print(f"=== Checking out deterministic Chromium Tag: {tag} ===")
    run_cmd(["git", "fetch", "--tags", "origin"], cwd=CHROMIUM_SRC, env=env)
    run_cmd(["git", "checkout", "--force", f"tags/{tag}"], cwd=CHROMIUM_SRC, env=env)

    print("=== Running Hermetic gclient sync ===")
    # Sync third-party hooks and dependencies without auto-updating depot_tools
    run_cmd(["gclient", "sync", "--nohooks", "--no-history", "--revision", f"src@refs/tags/{tag}"], cwd=THIRD_PARTY_DIR, env=env)
    run_cmd(["gclient", "runhooks"], cwd=THIRD_PARTY_DIR, env=env)

def main():
    manifest = load_manifest()
    sync_depot_tools(manifest)
    sync_chromium_tree(manifest)
    print("\n[ZsecureAutomate] Deterministic workspace sync complete!")

if __name__ == "__main__":
    main()
