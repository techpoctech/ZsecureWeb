# ZsecureWeb

ZsecureWeb is available under two distinct licenses:

1. **Open Source (AGPLv3):** Free for community, personal, and open-source use under the terms of the GNU Affero General Public License v3.0. Any network-hosted modifications or derivative works must be made publicly available under AGPLv3.
2. **Commercial License:** For enterprises seeking to embed, modify, or deploy ZsecureWeb without the copyleft obligations of AGPLv3. Commercial licenses include enterprise SLAs, dedicated support, and custom deployment options.

To inquire about commercial licensing, contact: golengeeks@gmail.com

The Open-Source, Hybrid-Local SASE & Enterprise Browser Enclave Platform

ZsecureWeb is a disruptive, unified SASE and Security Service Edge (SSE) platform designed to replace legacy hairpinned proxies (Zscaler, Netskope, Palo Alto Networks). By converging Zero Trust Network Access (ZTNA 2.0), Data Loss Prevention (DLP), Inline AI Security, and Endpoint Posture into a single local-first architecture, ZsecureWeb delivers sub-10ms enforcement latency and a 90% reduction in cloud infrastructure egress costs.

ZsecureWeb - Open-Source Hybrid SASE & Enterprise Browser Platform
Copyright (C) 2026 ZsecureWeb Contributors

## 🏗 System Architecture

The workspace utilizes a meta-repository pattern to isolate upstream engine changes from proprietary logic:

* **`zsecureweb/` (Root):** Orchestration tools, build engine, release manifests, and workflow scripts.
* **`thirdParty/chromium/src/` (Submodule):** Forked Chromium baseline (`techpoctech/chromium`) containing minimal integration points.
* **`thirdParty/chromium/src/zsecureweb/` (Submodule):** Core DLP engine, custom UI, and V8 hooks (`techpoctech/zsecureweb-core`).

---

## 💻 System Prerequisites

Before initializing the workspace, ensure your host environment meets the baseline requirements:

* **OS:** Linux (Ubuntu 22.04 LTS recommended), macOS, or Windows 10/11 (WSL2/Native)
* **Hardware:** x86-64 machine, minimum 16 GB RAM (32 GB+ recommended), and ≥100 GB free disk space
* **Dependencies:** `git`, `python3` (v3.9+), `curl`

---

## 🚀 Quick Start & Environment Setup

Follow these steps to set up a deterministic development environment.

### 1. Clone the Workspace
Clone the parent orchestrator repository:
```bash
git clone [https://github.com/techpoctech/zsecureweb.git](https://github.com/techpoctech/zsecureweb.git)
cd zsecureweb

2. Run Workspace Initialization
Run tools/setup.py to initialize submodules, fetch the pinned depot_tools revision, and run gclient sync automatically:

python3 tools/setup.py

Note : on Determinism: tools/setup.py delegates workspace synchronization to tools/automate.py, which reads version.json to lock depot_tools and Chromium dependencies to specific release hashes.

⚙️ Building zsecureweb
Once the setup completes, generate build configurations and compile the engine using Ninja.

1. Configure PATH Environment
Temporarily prepend the hermetic depot_tools path to your active shell session:

Bash
export PATH="$PWD/tools/depot_tools:$PATH"
2. Generate Build Files
Navigate to the Chromium source directory and initialize GN build flags:

Bash
cd thirdParty/chromium/src
gn gen out/Default --args="is_debug=false symbol_level=0 target_cpu=\"x64\""
3. Compile the Target
Compile the zsecure_browser target using autoninja:

Bash
autoninja -C out/Default zsecure_browser
🛠 Project Structure
Plaintext
zsecureweb/
├── .gitmodules             # Submodule definitions & path routing
├── version.json            # Single source of truth for toolchain & tag pins
├── tools/
│   ├── setup.py            # Machine initialization entry point
│   ├── automate.py         # Deterministic gclient orchestration engine
│   └── depot_tools/        # (Hermetic) Google Chromium build toolset
└── thirdParty/
    └── chromium/
        ├── .gclient        # Generated gclient target mapping
        └── src/            # Chromium source tree
            └── zsecureweb/ # Core DLP C++ module (zsecureweb-core)
🧹 Maintenance & Updating
Re-syncing Dependencies: If version.json is updated by other contributors, pull the changes and re-run:

python3 tools/automate.py
Git Status Cleanliness: Untracked build outputs (out/, .o, .ninja) inside Chromium are automatically ignored by Git submodule configuration to keep git status clean.
