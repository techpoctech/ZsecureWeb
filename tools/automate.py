#!/usr/bin/env python3
# Copyright (c) 2026 zsecureweb Contributors
# License: AGPLv3

import json
import os
import subprocess
import sys

# Define workspace root directory
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERSION_FILE = os.path.join(ROOT_DIR, "version.json")
TOOLS_DIR = os.path.join(ROOT_DIR, "tools")
DEPOT_TOOLS_DIR = os.path.join(TOOLS_DIR, "depot_tools")
THIRD_PARTY_DIR = os.path.join(ROOT_DIR, "thirdParty", "chromium")
CHROMIUM_SRC = os.path.join(THIRD_PARTY_DIR, "src")


def load_manifest():
    if not os.path.exists(VERSION_FILE):
        print(f"Error: Manifest file {VERSION_FILE} does not exist.")
        sys.exit(1)
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
    """Clones and syncs depot_tools to a specific pinned hash or ref."""
    print(f"=== Step 2: Syncing depot_tools to Hash/Branch: {target_hash} ===")

    if not os.path.exists(os.path.join(depot_tools_dir, ".git")):
        print(f"Cloning depot_tools into {depot_tools_dir}...")
        subprocess.run(
            ["git", "clone", "https://chromium.googlesource.com/chromium/tools/depot_tools.git", depot_tools_dir],
            check=True
        )

    print("Fetching latest refs for depot_tools...")
    subprocess.run(["git", "fetch", "origin"], cwd=depot_tools_dir, check=True)
    subprocess.run(["git", "fetch", "origin", target_hash], cwd=depot_tools_dir, check=False)
    subprocess.run(["git", "checkout", "-f", target_hash], cwd=depot_tools_dir, check=True)

    print("✓ depot_tools successfully synced.\n")


def generate_gclient_config(manifest):
    """Generates .gclient config with managed: False to respect Git submodule state."""
    os.makedirs(THIRD_PARTY_DIR, exist_ok=True)
    gclient_path = os.path.join(THIRD_PARTY_DIR, ".gclient")

    fork_url = manifest.get("chromium", {}).get("upstream_url", "https://github.com/techpoctech/chromium.git")

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
    print(f"✓ Generated .gclient pointing to {fork_url}")


def sync_chromium_deps():
    """Syncs third-party dependencies and runs toolchain hooks."""
    env = get_env()

    print("=== Step 3: Running Hermetic gclient sync ===")
    subprocess.run(
        ["gclient", "sync", "--no-history", "--nohooks"],
        cwd=THIRD_PARTY_DIR,
        env=env,
        check=True
    )

    print("=== Step 4: Running gclient runhooks ===")
    subprocess.run(["gclient", "runhooks"], cwd=THIRD_PARTY_DIR, env=env, check=True)


def sync_submodules(root_dir=ROOT_DIR):
    """Initializes and synchronizes Chromium and zsecureweb-core submodules."""
    print("=== Step: Syncing Git Submodules ===")

    # Neutralize any nested internal gitmodules in chromium if present
    chromium_gitmodules = os.path.join(root_dir, "thirdParty", "chromium", "src", ".gitmodules")
    if os.path.exists(chromium_gitmodules):
        os.remove(chromium_gitmodules)

    # Sync submodule URLs and configuration first to prevent pathspec errors
    subprocess.run(
        ["git", "submodule", "sync"],
        cwd=root_dir,
        check=True
    )

    # Initialize and update submodules recursively
    subprocess.run(
        ["git", "submodule", "update", "--init", "--recursive"],
        cwd=root_dir,
        check=True
    )
    print("✓ All submodules successfully synchronized.\n")

def main():
    manifest = load_manifest()

    depot_tools_hash = (
        manifest.get("depot_tools", {}).get("hash")
        if isinstance(manifest.get("depot_tools"), dict)
        else manifest.get("depot_tools_hash") or "main"
    )

    sync_submodules(ROOT_DIR)
    sync_depot_tools(DEPOT_TOOLS_DIR, depot_tools_hash)
    generate_gclient_config(manifest)
    #sync_chromium_deps()
    print("\n[zsecureweb] Submodules and workspace successfully synchronized!")


if __name__ == "__main__":
    main()