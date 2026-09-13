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

def sync_depot_tools(depot_tools_dir: str, target_hash: str):
    print(f"=== Syncing depot_tools to Hash: {target_hash} ===")

    # 1. Clone if depot_tools directory does not exist
    if not os.path.exists(os.path.join(depot_tools_dir, ".git")):
        print(f"Cloning depot_tools into {depot_tools_dir}...")
        subprocess.run(
            ["git", "clone", "https://chromium.googlesource.com/chromium/tools/depot_tools.git", depot_tools_dir],
            check=True
        )

    # 2. Fetch origin to ensure the specified hash is available locally
    print("Fetching latest refs for depot_tools...")
    subprocess.run(
        ["git", "fetch", "origin"],
        cwd=depot_tools_dir,
        check=True
    )

    # 3. Explicitly fetch the target commit (handles shallow clone edge cases)
    subprocess.run(
        ["git", "fetch", "origin", target_hash],
        cwd=depot_tools_dir,
        check=False  # Ignore error if origin doesn't support fetching hashes directly
    )

    # 4. Checkout target hash and force clean state
    subprocess.run(
        ["git", "checkout", "-f", target_hash],
        cwd=depot_tools_dir,
        check=True
    )

    print("✓ depot_tools successfully synced.")

def generate_gclient_config(manifest):
    """Generates explicit .gclient file pointing directly to techpoctech SSH repository."""
    os.makedirs(THIRD_PARTY_DIR, exist_ok=True)
    gclient_path = os.path.join(THIRD_PARTY_DIR, ".gclient")

    fork_url = manifest["chromium"]["upstream_url"]

    gclient_content = f"""solutions = [
  {{
    "name": "src",
    "url": "{fork_url}",
    "deps_file": "DEPS",
    "managed": True,
    "custom_deps": {{}},
  }},
]
"""
    with open(gclient_path, "w") as f:
        f.write(gclient_content)
    print(f"✓ Generated .gclient pointing to {fork_url}")

def sync_chromium(manifest):
    """Runs deterministic gclient sync pointing to techpoctech fork."""
    env = get_env()
    generate_gclient_config(manifest)

    fork_url = manifest["chromium"]["upstream_url"]

    # 1. If src exists, ensure local git remote matches version.json URL
    if os.path.exists(os.path.join(CHROMIUM_SRC, ".git")):
        print(f"=== Aligning local origin remote to {fork_url} ===")
        subprocess.run(
            ["git", "remote", "set-url", "origin", fork_url],
            cwd=CHROMIUM_SRC,
            check=True
        )
    else:
        # 2. Clone fresh target branch if src doesn't exist
        target_branch = manifest["chromium"].get("hash", "main")
        print(f"=== Initializing src from {fork_url} ===")
        os.makedirs(CHROMIUM_SRC, exist_ok=True)
        subprocess.run(
            ["git", "clone", "--depth", "1", "-b", target_branch, fork_url, CHROMIUM_SRC],
            check=True
        )

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

    # Extract depot_tools target hash from version.json
    depot_tools_hash = manifest.get("depot_tools", {}).get("hash") or manifest.get("depot_tools_hash")
    if not depot_tools_hash:
        print("Error: Could not locate depot_tools hash key in version.json")
        sys.exit(1)

    sync_depot_tools(DEPOT_TOOLS_DIR, depot_tools_hash)
    sync_chromium(manifest)
    print("\n[zsecureweb] Workspace successfully synchronized!")

if __name__ == "__main__":
    main()