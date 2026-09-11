# ZsecureWeb

ZsecureWeb is available under two distinct licenses:

1. **Open Source (AGPLv3):** Free for community, personal, and open-source use under the terms of the GNU Affero General Public License v3.0. Any network-hosted modifications or derivative works must be made publicly available under AGPLv3.
2. **Commercial License:** For enterprises seeking to embed, modify, or deploy ZsecureWeb without the copyleft obligations of AGPLv3. Commercial licenses include enterprise SLAs, dedicated support, and custom deployment options.

To inquire about commercial licensing, contact: golengeeks@gmail.com

The Open-Source, Hybrid-Local SASE & Enterprise Browser Enclave Platform

ZsecureWeb is a disruptive, unified SASE and Security Service Edge (SSE) platform designed to replace legacy hairpinned proxies (Zscaler, Netskope, Palo Alto Networks). By converging Zero Trust Network Access (ZTNA 2.0), Data Loss Prevention (DLP), Inline AI Security, and Endpoint Posture into a single local-first architecture, ZsecureWeb delivers sub-10ms enforcement latency and a 90% reduction in cloud infrastructure egress costs.

ZsecureWeb - Open-Source Hybrid SASE & Enterprise Browser Platform
Copyright (C) 2026 ZsecureWeb Contributors

//project structure
1. ZsecureWeb (Meta / Orchestration Repo)
   └── https://github.com/techpoctech/ZsecureWeb
       ├── Contains: Build tools, setup scripts, docs, CI workflows, .gitmodules
       └── Tracks: The exact committed states/hashes of the two submodules

2. chromium (Forked Upstream Source)
   └── https://github.com/techpoctech/chromium
       ├── Lives at: thirdParty/chromium/src
       └── Contains: Upstream Google Chromium code + minimal 1-line integration hooks

3. zsecureweb-core (IP & Core Engine)
   └── https://github.com/techpoctech/zsecureweb-core
       ├── Lives at: thirdParty/chromium/src/zsecureweb
       └── Contains: 100% of your proprietary C++ DLP, V8 hooks, custom UI, and BUILD.gn
