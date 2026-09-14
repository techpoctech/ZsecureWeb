# Contributing Guidelines

Thank you for considering contributing! We welcome bug fixes, documentation improvements, and feature contributions.

---

## 1. Code License & Licensing Model

* **Primary License:** This project is licensed under the **GNU Affero General Public License v3.0 (AGPLv3)**.
* **Headers Required:** All original source code files must include the standard AGPLv3 notice header.
* **Third-Party Code:** Do not remove existing license headers from third-party libraries (e.g., Apache 2.0, BSD, MIT). Keep them in their original state.

---

## 2. Contributor License Agreement (CLA)

To accept pull requests, we require all contributors to sign our [Contributor License Agreement (CLA.md)](CLA.md). 

### Why do we require a CLA?
The CLA ensures that:
1. You retain ownership and copyright of your work while granting us the right to distribute it.
2. The codebase remains legally protected against copyright and patent disputes.
3. We retain the flexibility to re-license the software (e.g., for commercial distributions or enterprise offerings alongside AGPLv3).

### How to Sign the CLA
1. Fork the repository and create a Pull Request (PR).
2. Our **CLA Assistant** GitHub Action will automatically check if you have signed.
3. If you haven't signed, the bot will block the PR and post a comment with instructions.
4. To sign, reply directly to the PR comment with:
   ```text
   I have read the CLA Document and I hereby sign the CLA


Quick Start

1. Clone and Set Up

Bash
git clone https://github.com/techpoctech/zsecureweb.git
cd zsecureweb
python3 tools/automate.py
(This automatically configures gclient, pulls Chromium, and clones zsecureweb-core into thirdParty/chromium/src/zsecureweb.)

2. Build the Project

Bash
python3 tools/build.py
Contributing

Top-Level Repository (zsecureweb): For updates to automation scripts, manifests, or documentation, work directly in the root directory. Create a branch, commit your changes (git add . && git commit -m "msg"), and push to the main repository.

Core Logic (zsecureweb-core): For code changes inside the core application, navigate to cd thirdParty/chromium/src/zsecureweb. Since it operates as an independent Git repository, create your feature branch, commit locally, and push straight to the zsecureweb-core remote to open a Pull Request.

Chromium: Treated as a managed external dependency via gclient. Code modifications are not pushed back to upstream Chromium; dependencies are managed through your workspace configuration and manifest.
Think of Chromium as the massive engine block for a custom car. You didn't build the engine yourself, and you don't send changes back to the factory that made it. You just bolt your own custom parts (zsecureweb) right onto it, and your build tools handle keeping everything connected.

[ First PR Signed via CLA ] ──► [ Contributor ] ──► [ Committer (Write Access) ] ──► [ Core Reviewer / CODEOWNERS ]
