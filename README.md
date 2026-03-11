# BankStack — Unified Wazuh + Splunk Banking SOC Deployment

<div align="center">

![BankStack](https://img.shields.io/badge/BankStack-Banking%20SOC-blue?style=for-the-badge)
![Wazuh](https://img.shields.io/badge/Wazuh-4.9.2-00A4EF?style=for-the-badge&logo=wazuh)
![Splunk](https://img.shields.io/badge/Splunk-9.3-000000?style=for-the-badge&logo=splunk)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**A production-grade banking SOC platform combining Wazuh XDR and Splunk SIEM, pre-configured with 60+ custom rules for Bangladesh banking operations — SWIFT, CBS, MFS (bKash/Nagad), BEFTN, NPSB, RTGS, ATM monitoring, and BB ICT v4.0 compliance.**

[Quick Start](#-quick-start) · [Architecture](#-architecture) · [Custom Rules](#-wazuh-custom-rules) · [SPL Searches](#-splunk-spl-correlation-searches) · [Dashboards](#-splunk-dashboards) · [Simulator](#-banking-log-simulator)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Architecture](#-architecture)
- [Features](#-features)
- [Prerequisites](#-prerequisites)
- [Quick Start](#-quick-start)
- [Step-by-Step Beginner Guide](#-step-by-step-beginner-guide)
- [Using the Platform](#-using-the-platform)
- [Running Tests](#-running-tests)
- [Shutting Everything Down](#-shutting-everything-down)
- [Project Structure](#-project-structure)
- [Wazuh Custom Rules](#-wazuh-custom-rules)
- [Splunk SPL Correlation Searches](#-splunk-spl-correlation-searches)
- [Splunk Dashboards](#-splunk-dashboards)
- [Banking Log Simulator](#-banking-log-simulator)
- [Active Response Scripts](#-active-response-scripts)
- [SCA Policy — BD Banking](#-sca-policy--bd-banking)
- [Compliance Coverage](#-compliance-coverage)
- [Backup and Restore](#-backup-and-restore)
- [Makefile Commands](#-makefile-commands)
- [Configuration](#-configuration)
- [Troubleshooting](#-troubleshooting)
- [Tech Stack](#-tech-stack)
- [License](#-license)

---

## 🏦 Overview

**BankStack** is a unified Security Operations Center (SOC) deployment that combines **Wazuh XDR** (free, open-source endpoint detection & response) with **Splunk Free** (enterprise SIEM analytics). It's specifically designed for **Bangladesh banking operations**, with pre-configured rules, decoders, dashboards, and a realistic log simulator.

### Why BankStack?

- **Banking-specific detections** directly relevant to BD financial institutions
- **One-command deployment** via `make setup`
- **Realistic attack simulations** including SWIFT heist patterns, MFS fraud, and BEFTN smurfing
- **Compliance dashboards** for BB ICT v4.0, PCI DSS v4.0, and SWIFT CSP
- **Hands-on SOC experience** with production-grade tooling

### What Problems Does This Solve?

| Challenge | BankStack Solution |
|---|---|
| Banks need both Wazuh (XDR) and Splunk (SIEM) | Unified stack with alert forwarding |
| BD-specific compliance (BB ICT v4.0) | Pre-built compliance dashboard + SCA policy |
| SWIFT security (Bangladesh Bank heist 2016) | Custom SWIFT rules + active response lockdown |
| MFS fraud detection (bKash/Nagad) | Dedicated MFS monitoring + SIM swap detection |
| No realistic test data | Python banking log simulator with attack injection |
| Complex multi-service deployment | Single `make setup` command |

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    BankStack SOC Platform                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    syslog/514    ┌───────────────────┐        │
│  │  Banking Log  │───────────────▶│   Wazuh Manager    │        │
│  │  Simulator    │                 │  (XDR Engine)      │        │
│  │              │                 │                     │        │
│  │ • CBS Logs    │                 │ • 60+ Custom Rules  │        │
│  │ • SWIFT Logs  │                 │ • Custom Decoders   │        │
│  │ • MFS Logs    │                 │ • Active Response   │        │
│  │ • ATM Logs    │                 │ • FIM (SWIFT/CBS)   │        │
│  │ • BEFTN/RTGS  │                 │ • SCA (BB ICT v4.0) │        │
│  │ • AD/Auth     │                 │ • Vuln Detection    │        │
│  │ • Firewall    │                 └──────┬──────┬──────┘        │
│  │ • Attack Sim  │                        │      │               │
│  └──────────────┘                        │      │               │
│                                           │      │               │
│                          ┌────────────────┘      └──────────┐    │
│                          ▼                                   ▼    │
│               ┌──────────────────┐              ┌───────────────┐│
│               │  Wazuh Indexer   │              │    Splunk     ││
│               │  (OpenSearch)    │              │  (Free SIEM)  ││
│               │                  │              │               ││
│               │ • Alert Storage   │  syslog/    │ • 25+ SPL     ││
│               │ • Full-text Search│  JSON/9515  │   Searches    ││
│               │ • Analytics       │◀────────────│ • 5 Dashboards││
│               └────────┬─────────┘              │ • BD Bank     ││
│                        │                        │   Lookups     ││
│                        ▼                        └───────┬───────┘│
│               ┌──────────────────┐                      │        │
│               │ Wazuh Dashboard  │                      │        │
│               │ (Visualization)   │                      │        │
│               │                  │                      │        │
│               │ :443             │              :8000   │        │
│               └──────────────────┘              ────────┘        │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│  Docker Network: bankstack-net (172.25.0.0/24)                  │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Banking Log Simulator** generates realistic Bangladesh banking logs (CBS, SWIFT, MFS, ATM, BEFTN, NPSB, RTGS, AD, Firewall) with configurable attack injection
2. **Wazuh Manager** receives logs via syslog (UDP/514), processes through custom decoders and 60+ banking-specific rules
3. **Wazuh Indexer** (OpenSearch) stores all alerts for search and analytics
4. **Wazuh Dashboard** provides real-time Wazuh visualization
5. **Splunk** receives Wazuh alerts via syslog forwarding (JSON/9515), runs 25+ SPL correlation searches across 5 dashboards
6. **Active Response** automatically triggers lockdown scripts (brute force blocking, web shell quarantine, SWIFT emergency lockdown)

### Network Architecture

| Service | Container | IP | Ports |
|---|---|---|---|
| Wazuh Indexer | bankstack-wazuh-indexer | 172.25.0.10 | 9200 |
| Wazuh Manager | bankstack-wazuh-manager | 172.25.0.11 | 1514, 1515, 514/udp, 55000 |
| Wazuh Dashboard | bankstack-wazuh-dashboard | 172.25.0.12 | 443 |
| Splunk | bankstack-splunk | 172.25.0.20 | 8000, 8088, 9515/udp |
| Log Simulator | bankstack-log-simulator | 172.25.0.30 | — |

---

## ✨ Features

### Wazuh Layer (XDR + Endpoint Security)

- **60+ Custom Rules** organized by banking domain (SWIFT, CBS, MFS, BEFTN, ATM, Auth, Compliance, etc.)
- **File Integrity Monitoring (FIM)** for SWIFT Alliance, CBS, payment system, and ATM directories
- **3 Active Response Scripts**: brute-force lockout, web shell quarantine, SWIFT emergency lockdown
- **SCA Policy** — 25+ checks covering BB ICT v4.0, PCI DSS v4.0, and SWIFT CSP

### Splunk Layer (SIEM + Analytics)

- **25+ SPL Correlation Searches** for banking-specific threat detection
- **5 Pre-built Dashboards**: SOC KPI, Banking Threats, MFS Monitoring, BB ICT Compliance, Threat Intelligence
- **Bangladesh-Specific Lookups**: 45+ BD bank codes, MFS providers, threat intel IOCs

### Banking Log Simulator

- **8 Log Generators** with time-of-day patterns and **5 Attack Scenarios**
- **On-demand attack injection** via `make simulate-attack`
- **Realistic BD Banking Data**: bank codes, branch names, MFS providers, BDT amounts

---

## 📦 Prerequisites

| Requirement | Minimum Version | Check Command |
|---|---|---|
| **Docker** | 24.0+ | `docker --version` |
| **Docker Compose** | v1.29+ or v2.20+ | `docker compose version` or `docker-compose --version` |
| **OpenSSL** | any | `openssl version` |
| **Make** | any | `make --version` |
| **Git** | any | `git --version` |

**System Requirements:**
- **RAM**: 8 GB minimum (16 GB recommended)
- **Disk**: 20 GB free space
- **OS**: Linux (tested on Ubuntu 24.04), macOS, or Windows with WSL2

### Installing Docker (Ubuntu/Debian)

```bash
# Install Docker
curl -fsSL https://get.docker.com | sh

# Add your user to docker group
sudo usermod -aG docker $USER

# IMPORTANT: Activate the docker group in your current shell
# (otherwise you'll get "Permission denied" errors)
newgrp docker

# Install Docker Compose v1 (if not available as docker compose plugin)
sudo apt install docker-compose
```

> **Important:** After running `sudo usermod -aG docker $USER`, you must either:
> 1. Run `newgrp docker` (activates docker group in current terminal), or
> 2. Log out and log back in (permanent fix for all terminals)
>
> Without this, any `make` command that uses Docker will fail with "Permission denied".

---

## 🚀 Quick Start

For experienced users — get running in 3 commands:

```bash
git clone https://github.com/uchihashahin01/BankStack.git
cd BankStack
make setup
```

This generates SSL certificates, starts all 5 services, and shows you the access URLs. Skip to [Using the Platform](#-using-the-platform) once everything is healthy.

---

## 📖 Step-by-Step Beginner Guide

If you're new to Docker or SOC platforms, follow this complete walkthrough.

### Step 1: Clone the Repository

```bash
git clone https://github.com/uchihashahin01/BankStack.git
cd BankStack
```

### Step 2: Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your preferred passwords (optional — defaults work fine)
nano .env
```

The default values work out of the box. Change passwords only if you want custom credentials.

### Step 3: Generate SSL Certificates

```bash
# Make scripts executable
chmod +x scripts/*.sh

# Generate SSL certificates for Wazuh inter-service TLS
bash scripts/generate-certs.sh
```

You'll see output like:
```
[*] Generating Root CA...
[*] Generating Wazuh Indexer certificate...
[*] Generating Wazuh Manager certificate...
[*] Generating Wazuh Dashboard certificate...
[*] All certificates generated successfully!
```

### Step 4: Start All Services

```bash
# Start the entire stack
make start

# Or equivalently:
docker compose up -d
# (or docker-compose up -d if you use v1)
```

### Step 5: Wait for Services to Initialize

Services take 2-3 minutes to fully start. Check their status:

```bash
# Check container status (run this a few times)
make status
```

Wait until you see all containers showing **(healthy)**:

```
NAME                        STATUS
bankstack-wazuh-indexer     Up 2 minutes (healthy)
bankstack-wazuh-manager     Up 2 minutes (healthy)
bankstack-wazuh-dashboard   Up 2 minutes (healthy)
bankstack-splunk            Up 2 minutes (healthy)
bankstack-log-simulator     Up 2 minutes
```

### Step 6: Access the Web Interfaces

| Service | URL | Username | Password |
|---|---|---|---|
| **Wazuh Dashboard** | https://localhost:443 | `admin` | `admin` |
| **Splunk Web** | http://localhost:8000 | `admin` | `BankStack@Splunk2026` |
| **Wazuh API** | https://localhost:55000 | `wazuh-wui` | `BankStack@S0C2026` |

> **Note:** The Wazuh Dashboard uses a self-signed SSL certificate. Your browser will show a security warning — click "Advanced" → "Proceed" to continue. This is expected for local deployments.

### Step 7: Explore the Dashboards

**In Wazuh Dashboard (https://localhost:443):**
1. Log in with `admin` / `admin`
2. Go to **Security Events** to see real-time alerts
3. Check **Modules** → **Security Configuration Assessment** for compliance results
4. The simulator is already generating banking logs — you'll see SWIFT, CBS, MFS alerts appearing

**In Splunk (http://localhost:8000):**
1. Log in with `admin` / `BankStack@Splunk2026`
2. Click **Apps** → **BankStack SOC** from the left sidebar
3. Open the dashboards:
   - **SOC KPI** — Overall alert metrics and trends
   - **Banking Threats** — SWIFT, CBS, ATM, payment system alerts
   - **MFS Monitoring** — bKash/Nagad/Rocket specific view
   - **BB ICT Compliance** — Compliance scoring
   - **Threat Intelligence** — IOC and geo-source tracking
4. To run a manual search: Click **Search & Reporting**, then enter:
   ```spl
   index=bankstack_wazuh | stats count by rule.description | sort -count | head 20
   ```

---

## 🖥 Using the Platform

### Viewing Live Logs

```bash
# Follow ALL service logs in real-time
make logs

# Follow only a specific service
make logs-wazuh      # Wazuh Manager logs
make logs-splunk     # Splunk logs
make logs-simulator  # Banking Log Simulator output
```

Press `Ctrl+C` to stop following logs.

### Triggering Attack Simulations

The simulator injects attacks automatically (15% probability per cycle). To trigger a manual burst of all 5 attack types at once:

```bash
make simulate-attack
```

This triggers: brute force, transaction fraud, privilege escalation, SWIFT heist pattern, and data exfiltration. Watch the Wazuh and Splunk dashboards light up with high-severity alerts.

### Opening a Shell into Containers

```bash
# Access Wazuh Manager shell (inspect rules, logs, configs)
make shell-wazuh

# Inside the Wazuh Manager, useful commands:
#   cat /var/ossec/logs/alerts/alerts.json | tail -20
#   /var/ossec/bin/wazuh-control status
#   cat /var/ossec/etc/rules/local_rules.xml

# Access Splunk shell
make shell-splunk
```

### Monitoring Container Resources

```bash
# Live resource monitoring (CPU/RAM/Net) — updates every 5s
make monitor

# One-time resource usage snapshot
make resources
```

### Backing Up Data

```bash
# Create a timestamped backup of all Wazuh and Splunk data
make backup

# Restore from a backup
make restore BACKUP=backups/bankstack-backup-20260311-143000.tar.gz
```

---

## 🧪 Running Tests

### Unit Tests (Simulator Logic)

```bash
# Install test dependencies (if not already installed)
pip install pytest

# Run all 14 unit tests
pytest tests/test_simulator.py -v
```

You should see:
```
tests/test_simulator.py::test_generator[CBS] PASSED
tests/test_simulator.py::test_generator[SWIFT] PASSED
...
tests/test_simulator.py::test_attack[DataExfiltration] PASSED
============= 14 passed =============
```

### Integration Tests (Full Stack)

With the stack running:

```bash
make test
```

This checks:
- All 5 Docker containers are running and healthy
- Wazuh API is responding
- Splunk Web is accessible
- Custom rules and decoders are loaded
- Logs are flowing from simulator → Wazuh → Splunk

---

## 🛑 Shutting Everything Down

### Stop Services (Keep Data)

```bash
make stop
```

This stops all containers but **preserves your data** (Wazuh alerts, Splunk indices, etc.). You can restart later with `make start`.

### Full Cleanup (Destroy Everything)

```bash
make clean
```

> **⚠️ Warning:** This stops all containers AND deletes all persistent data (Docker volumes, generated certificates). You'll need to run `make setup` again from scratch.

### Restarting After a Stop

```bash
# If you used 'make stop', just start again:
make start

# Check health:
make status
```

---

## 📁 Project Structure

```
BankStack/
├── docker-compose.yml              # Full stack orchestration
├── .env.example                    # Environment template (copy to .env)
├── Makefile                        # All operational commands
│
├── config/
│   └── wazuh_indexer_ssl_certs/    # Generated SSL certificates
│
├── wazuh/
│   ├── wazuh_manager/
│   │   ├── ossec.conf              # Wazuh Manager configuration
│   │   ├── local_rules.xml         # 60+ custom banking rules
│   │   ├── local_decoders.xml      # Custom log decoders
│   │   ├── active-response/
│   │   │   ├── brute-force-lockout.sh
│   │   │   ├── webshell-quarantine.sh
│   │   │   └── swift-lockdown.sh
│   │   └── sca/
│   │       └── bd_banking_server.yml
│   ├── wazuh_indexer/
│   │   └── wazuh.indexer.yml
│   └── wazuh_dashboard/
│       ├── wazuh_dashboards.yml
│       └── wazuh.yml
│
├── splunk/
│   └── apps/bankstack/
│       ├── default/
│       │   ├── app.conf
│       │   ├── indexes.conf        # Wazuh + Banking data indices
│       │   ├── inputs.conf
│       │   ├── props.conf
│       │   ├── transforms.conf
│       │   ├── savedsearches.conf  # 25+ SPL correlation searches
│       │   └── data/ui/views/
│       │       ├── bb_ict_compliance.xml
│       │       ├── soc_kpi.xml
│       │       ├── banking_threats.xml
│       │       ├── mfs_monitoring.xml
│       │       └── threat_intelligence.xml
│       └── lookups/
│           ├── bd_bank_codes.csv
│           ├── mfs_providers.csv
│           └── threat_intel_ioc.csv
│
├── simulator/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── config.yml
│   ├── banklog_simulator.py        # Main simulator orchestrator
│   ├── generators/                  # 8 log generators
│   └── attacks/                     # 5 attack scenarios + runner
│       └── run_all.py              # On-demand attack burst trigger
│
├── scripts/
│   ├── generate-certs.sh           # SSL certificate generator
│   ├── health-check.sh             # Service health checker
│   └── backup-restore.sh           # Backup and restore utility
│
└── tests/
    ├── test_simulator.py            # Simulator unit tests (14 tests)
    └── test_stack.sh                # Integration tests
```

---

## 🛡 Wazuh Custom Rules

### Rule ID Allocation

| Range | Category | Count |
|---|---|---|
| 100100-100107 | Authentication & Access Control | 8 |
| 100110-100114 | Brute Force & Account Abuse | 5 |
| 100120-100123 | Privilege Escalation | 4 |
| 100130-100133 | Web Application Attacks | 4 |
| 100140-100143 | File Integrity — SWIFT | 4 |
| 100150-100152 | File Integrity — CBS | 3 |
| 100160-100161 | File Integrity — Payment Systems | 2 |
| 100200-100207 | SWIFT Operations | 8 |
| 100220-100227 | CBS Operations | 8 |
| 100240-100247 | MFS (bKash/Nagad/Rocket) | 8 |
| 100260-100272 | BEFTN/NPSB/RTGS | 7 |
| 100280-100285 | ATM/POS Operations | 6 |
| 100290-100293 | Agent Banking | 4 |
| 100300-100305 | Compliance (BB ICT/PCI DSS) | 6 |
| 100320-100323 | Data Exfiltration | 4 |
| 100330-100332 | Insider Threat | 3 |
| 100340-100343 | Network Anomalies | 4 |
| 100400-100403 | Card Fraud | 4 |
| 100410-100413 | QR Payment (Binimoy) | 4 |

### Key Detection Examples

**SWIFT After-Hours Transfer (Rule 100201)**
```xml
<rule id="100201" level="14">
  <decoded_as>bankstack-swift</decoded_as>
  <match>SWIFT_MSG_SENT</match>
  <time>22:00-06:00</time>
  <description>BankStack: SWIFT message sent outside business hours — CRITICAL</description>
</rule>
```
*Modeled after the 2016 Bangladesh Bank heist where $81M was stolen via after-hours SWIFT messages.*

**MFS SIM Swap Detection (Rule 100246)**
```xml
<rule id="100246" level="12">
  <decoded_as>bankstack-mfs</decoded_as>
  <match>MFS_SIM_SWAP</match>
  <description>BankStack: SIM swap detected for MFS-linked number</description>
</rule>
```

**BEFTN Smurfing (Rule 100262)**
```xml
<rule id="100262" level="14" frequency="20" timeframe="600">
  <if_matched_sid>100260</if_matched_sid>
  <same_field>source_account</same_field>
  <description>BankStack: BEFTN smurfing — 20+ transfers from same account in 10 min</description>
</rule>
```

---

## 🔍 Splunk SPL Correlation Searches

### 25+ Pre-Built Searches

| # | Search Name | Severity | Schedule |
|---|---|---|---|
| 1 | Brute Force on Critical Systems | High | Every 5 min |
| 2 | Distributed Brute Force | High | Every 10 min |
| 3 | After Hours Critical Login | Medium | Hourly (22-06) |
| 4 | Non-BD IP Critical Access | High | Every 15 min |
| 5 | SWIFT After Hours Transfer | Critical | Hourly (22-06) |
| 6 | SWIFT High Value Transfer | High | Every 15 min |
| 7 | SWIFT Sanctioned Country | Critical | Every 30 min |
| 8 | SWIFT Rapid Burst | High | Every 10 min |
| 9 | CBS High Value After Hours | High | Hourly (22-06) |
| 10 | CBS Rapid Transactions | Medium | Every 5 min |
| 11 | CBS Maker Checker Bypass | High | Every 4 hours |
| 12 | CBS Backdated Transaction | High | Every 6 hours |
| 13 | MFS Large Cashout Unusual Hours | High | Hourly (23-05) |
| 14 | MFS PIN Brute Force | High | Every 5 min |
| 15 | MFS SIM Swap Detection | High | Every 2 hours |
| 16 | MFS Smurfing Pattern | Medium | Every 2 hours |
| 17 | BEFTN Smurfing Pattern | High | Every 15 min |
| 18 | RTGS Outside Settlement Window | High | 17-08 daily |
| 19 | NPSB Card Rapid Transfers | Medium | Every 10 min |
| 20 | ATM Jackpotting Pattern | Critical | Every 10 min |
| 21 | Card Country Mismatch | Medium | Every 2 hours |
| 22 | Large Data Upload | High | Every 30 min |
| 23 | Bulk CBS Database Query | High | Every 3 hours |
| 24 | Terminated Employee Login | Critical | Every 4 hours |
| 25 | Audit Log Tampering | Critical | Every 6 hours |

### Example SPL Query

```spl
index=bankstack_wazuh action="SWIFT_MSG_SENT"
| eval hour=strftime(_time, "%H")
| where hour >= 22 OR hour < 6
| table _time, user, data.msg_type, data.sender_bic, data.receiver_bic, data.amount_usd
```

---

## 📊 Splunk Dashboards

### 1. BB ICT v4.0 Compliance Dashboard
- Overall compliance score, violation counters, control-by-control status

### 2. SOC KPI Dashboard
- Total alerts, critical count, MTTD, alert trends, severity distribution

### 3. Banking Threat Monitor
- SWIFT/CBS/ATM/Payment system alerts, transaction monitoring by country and branch

### 4. MFS Monitoring Dashboard
- Transaction volumes by provider, SIM swap and PIN brute force alerts, cashout heatmap

### 5. Threat Intelligence Dashboard
- IOC match tracking, geographic source analysis, threat severity trends, TI-enriched events

---

## 🎮 Banking Log Simulator

### Generators (8 Types)

| Generator | Log Prefix | Description |
|---|---|---|
| CBS | `BANKSTACK_CBS:` | Ababil/Flora/Stelar transactions, account mods, GL entries |
| SWIFT | `BANKSTACK_SWIFT:` | MT103/MT202 messages with realistic BICs and amounts |
| MFS | `BANKSTACK_MFS:` | bKash/Nagad/Rocket transactions, PIN failures |
| Auth/AD | `BANKSTACK_AUTH:` | Login success/fail, role changes, session activity |
| Firewall | `BANKSTACK_FW:` | Allow/deny/drop with zone-based filtering |
| ATM | `BANKSTACK_ATM:` | ATM withdrawals across BD locations |
| BEFTN | `BANKSTACK_BEFTN:` | Inter-bank electronic fund transfers |
| RTGS | `BANKSTACK_RTGS:` | High-value real-time gross settlements |

### Attack Scenarios (5 Types)

| Attack | Pattern | Description |
|---|---|---|
| Brute Force | 5-15 failed logins then optional success | Targets SWIFT, CBS, RTGS systems from foreign IPs |
| Transaction Fraud | After-hours transfers, rapid cashouts | CBS backdating, MFS SIM swap, BEFTN structuring |
| Privilege Escalation | Role elevation, maker-checker bypass | Teller→admin, service account interactive login |
| SWIFT Heist | After-hours high-value transfers | Bangladesh Bank 2016 heist pattern replication |
| Data Exfiltration | Large uploads, bulk queries | USB on critical systems, 10K+ record extractions |

---

## ⚡ Active Response Scripts

| Script | Trigger | Action |
|---|---|---|
| `brute-force-lockout.sh` | Rule 100110 (5+ failed logins/2min) | IP block via iptables, 1hr timeout |
| `webshell-quarantine.sh` | Rule 100130 (web shell detected) | Forensic isolation, evidence preservation |
| `swift-lockdown.sh` | Rules 100201, 100202 (after-hours SWIFT) | Read-only SWIFT dirs, port blocks, account locks |

---

## 📋 SCA Policy — BD Banking

25+ Security Configuration Assessment checks covering:

- **BB ICT v4.0**: Authentication, access control, patch management, network security, encryption, logging
- **SWIFT CSP**: Environment restrictions, security updates, logical access control
- **PCI DSS v4.0**: Service hardening, audit log protection

---

## ✅ Compliance Coverage

| Framework | Coverage | Notes |
|---|---|---|
| BB ICT Guidelines v4.0 | Sections 5, 6, 8, 9, 10, 11, 12, 13 | Core compliance monitoring |
| PCI DSS v4.0 | Requirements 1, 2, 4, 6, 8, 10 | Card data protection |
| SWIFT CSP v2024 | Controls 1.1, 2.2, 5.1 | Mandatory security controls |

---

## 💾 Backup and Restore

```bash
# Create a timestamped backup
make backup

# List available backups
ls backups/

# Restore from a specific backup (destructive — stops services first)
make restore BACKUP=backups/bankstack-backup-20260311-143000.tar.gz
```

---

## 🔧 Makefile Commands

| Command | Description |
|---|---|
| `make setup` | Full setup: generate certs + start all services |
| `make start` | Start all services |
| `make stop` | Stop all services (preserves data) |
| `make restart` | Restart all services |
| `make status` | Show service health status |
| `make logs` | Follow all service logs |
| `make logs-wazuh` | Follow Wazuh Manager logs |
| `make logs-splunk` | Follow Splunk logs |
| `make logs-simulator` | Follow simulator logs |
| `make test` | Run integration tests |
| `make simulate-attack` | Inject a burst of all 5 attack types |
| `make monitor` | Live resource monitoring (CPU/RAM/Net) |
| `make resources` | One-time resource usage snapshot |
| `make backup` | Create a timestamped data backup |
| `make restore BACKUP=<path>` | Restore from a backup file |
| `make shell-wazuh` | Open bash shell in Wazuh Manager |
| `make shell-splunk` | Open bash shell in Splunk |
| `make build` | Rebuild the simulator Docker image |
| `make clean` | Stop + destroy all data (DESTRUCTIVE) |

---

## ⚙️ Configuration

### Environment Variables (`.env`)

| Variable | Default | Description |
|---|---|---|
| `WAZUH_VERSION` | 4.9.2 | Wazuh Docker image version |
| `SPLUNK_VERSION` | 9.3 | Splunk Docker image version |
| `SPLUNK_PASSWORD` | BankStack@Splunk2026 | Splunk admin password |
| `INDEXER_PASSWORD` | admin | Wazuh Indexer admin password |
| `WAZUH_API_PASSWORD` | BankStack@S0C2026 | Wazuh API password |
| `SIMULATOR_LOG_RATE` | 10 | Logs per second |
| `SIMULATOR_ATTACK_PROBABILITY` | 0.15 | Attack injection rate |

---

## 🔥 Troubleshooting

### Containers Not Starting

```bash
# Check logs for errors
docker compose logs wazuh-manager 2>&1 | tail -30
docker compose logs splunk 2>&1 | tail -30

# Verify certificates exist
ls config/wazuh_indexer_ssl_certs/

# Regenerate if missing
bash scripts/generate-certs.sh
```

### Splunk Shows No Data

```bash
# Verify csyslogd is running inside Wazuh Manager
make shell-wazuh
/var/ossec/bin/wazuh-control status | grep csyslogd

# Restart Wazuh services if csyslogd is not running
/var/ossec/bin/wazuh-control restart
```

### Wazuh Dashboard Shows "Connection Error"

Wait 2-3 minutes after startup for the indexer to be fully ready, then refresh.

### Permission Denied on Docker

If you see `PermissionError: Permission denied` or `Cannot connect to Docker daemon`:

```bash
# Option 1: Activate docker group in your current shell (quick fix)
newgrp docker

# Option 2: Log out and log back in (permanent fix)
sudo usermod -aG docker $USER
# Then log out and log back in to your desktop session

# Option 3: Run with sudo
sudo make <target>
```

The Makefile will detect this and show a helpful error message if Docker access is missing.

### Browser SSL Warning

Expected behavior — self-signed certificates. Click "Advanced" → "Proceed to localhost".

---

## 🔧 Tech Stack

| Component | Technology | Version | Purpose |
|---|---|---|---|
| XDR Platform | Wazuh | 4.9.2 | Endpoint detection, FIM, active response |
| SIEM | Splunk Free | 9.3 | Log correlation, dashboards, SPL analytics |
| Search Engine | OpenSearch (Wazuh Indexer) | — | Alert storage and full-text search |
| Orchestration | Docker Compose | v1/v2 | One-command deployment |
| Log Simulator | Python | 3.12 | Realistic banking log generation |
| Rule Language | Wazuh XML | — | 60+ custom detection rules |
| Query Language | SPL | — | 25+ correlation searches |
| SCA | YAML | — | 25+ compliance checks |
| Active Response | Bash | — | 3 automated response scripts |
| SSL/TLS | OpenSSL | — | Certificate generation |

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

<div align="center">
<strong>Built for Bangladesh Banking SOC Operations</strong>
<br>
<sub>BankStack — A production-grade banking security operations platform.</sub>
</div>
