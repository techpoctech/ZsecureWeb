#!/usr/bin/env python3
# Copyright (c) 2026 zsecureweb Contributors
# License: AGPLv3

import os
import platform
import shutil
import subprocess
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS_DIR = os.path.join(ROOT_DIR, "tools")
DEPOT_TOOLS_DIR = os.path.join(TOOLS_DIR, "depot_tools")
CHROMIUM_SRC = os.path.join(ROOT_DIR, "thirdParty", "chromium", "src")
OUT_DIR = os.path.join(CHROMIUM_SRC, "out", "Default")


def get_env():
    """Injects pinned depot_tools into executable PATH."""
    env = os.environ.copy()
    env["PATH"] = DEPOT_TOOLS_DIR + os.path.pathsep + env.get("PATH", "")
    env["VPYTHON_CLEAR_PYTHONPATH"] = "1"
    env["DEPOT_TOOLS_WIN_TOOLCHAIN"] = "0"
    return env


def ensure_depot_tools_bootstrapped():
    """Ensures depot_tools python bootstrap is initialized."""
    bootstrap_file = os.path.join(DEPOT_TOOLS_DIR, "python3_bin_reldir.txt")
    if not os.path.exists(bootstrap_file):
        print("=== Initializing depot_tools bootstrap ===")
        env = get_env()
        env.pop("DEPOT_TOOLS_UPDATE", None)
        subprocess.run(["gclient", "--version"], cwd=DEPOT_TOOLS_DIR, env=env, check=True)
        print("✓ depot_tools bootstrap complete.\n")


def get_dynamic_gn_args():
    """Generates clean Release-mode GN args guaranteed to pass Siso validation."""
    args = [
        "is_debug=false",
        "dcheck_always_on=false",
        "is_component_build=true",  # Fast linkage for local development
        "symbol_level=0",  # Minimal symbols for high speed & low disk space
        'is_chrome_branded=false',
        'google_api_key=""',  # Clear default API key fallbacks
        "angle_enable_metal = false",
        "angle_build_metal_shaders = false",
        'google_default_client_id=""',
        'google_default_client_secret=""',
    ]

    # CPU Architecture Detection
    machine = platform.machine().lower()
    if machine in ["arm64", "aarch64"]:
        args.append('target_cpu="arm64"')
    elif machine in ["x86_64", "amd64"]:
        args.append('target_cpu="x64"')

    # Platform Workarounds
    if platform.system().lower() == "darwin":  # macOS
        args.append("angle_build_metal_shaders=false")

    return " ".join(args)


def run_gn_gen():
    print("=== Generating Clean GN Build Configuration ===")
    env = get_env()
    gn_args = get_dynamic_gn_args()
    print(f"Active GN Args: {gn_args}\n")

    # Wipe stale out/Default to prevent cache collisions from previous broken builds
    if os.path.exists(OUT_DIR):
        print(f"Clearing old build cache at {OUT_DIR}...")
        shutil.rmtree(OUT_DIR, ignore_errors=True)

    subprocess.run(
        ["gn", "gen", OUT_DIR, f"--args={gn_args}"],
        cwd=CHROMIUM_SRC,
        env=env,
        check=True
    )
    print(f"✓ GN build files successfully generated in {OUT_DIR}\n")


def run_ninja(target="chrome"):
    print(f"=== Compiling Target: {target} ===")
    env = get_env()

    try:
        subprocess.run(
            ["autoninja", "-C", OUT_DIR, target],
            cwd=CHROMIUM_SRC,
            env=env,
            check=True
        )
    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 60)
        print("!!! BUILD FAILURE DETECTED - AUTOMATIC DIAGNOSTICS !!!")
        print("=" * 60)

        # Auto-print Siso error script output if available
        siso_script = os.path.join(OUT_DIR, "siso_failed_commands.sh")
        if os.path.exists(siso_script):
            print("\n[Failed Execution Command]:")
            with open(siso_script, "r") as f:
                print(f.read())

        # Auto-print trailing log lines from siso_output
        siso_output = os.path.join(OUT_DIR, "siso_output")
        if os.path.exists(siso_output):
            print("\n[Trailing Siso Output Log]:")
            with open(siso_output, "r") as f:
                lines = f.readlines()
                print("".join(lines[-30:]))  # Print last 30 lines of exact error log

        print("=" * 60 + "\n")
        sys.exit(e.returncode)


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "chrome"
    ensure_depot_tools_bootstrapped()
    run_gn_gen()
    run_ninja(target)


if __name__ == "__main__":
    main()