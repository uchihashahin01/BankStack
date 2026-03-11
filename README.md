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
- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [Wazuh Custom Rules](#-wazuh-custom-rules)
- [Splunk SPL Correlation Searches](#-splunk-spl-correlation-searches)
- [Splunk Dashboards](#-splunk-dashboards)
- [Banking Log Simulator](#-banking-log-simulator)
- [Active Response Scripts](#-active-response-scripts)
- [SCA Policy — BD Banking](#-sca-policy--bd-banking)
- [Compliance Coverage](#-compliance-coverage)
- [Testing](#-testing)
- [Configuration](#-configuration)
- [Interview Demo Guide](#-interview-demo-guide)
- [Tech Stack](#-tech-stack)
- [License](#-license)

---

## 🏦 Overview

**BankStack** is a unified Security Operations Center (SOC) deployment that combines **Wazuh XDR** (free, open-source endpoint detection & response) with **Splunk Free** (enterprise SIEM analytics). It's specifically designed for **Bangladesh banking operations**, with pre-configured rules, decoders, dashboards, and a realistic log simulator.

### Why BankStack?

Every SOC analyst job posting in Bangladesh requires experience with **Splunk SPL** and **Wazuh**. BankStack provides:

- **Hands-on proof** of deploying and operating both platforms
- **Banking-specific detections** that are directly relevant to BD financial institutions
- **One-command deployment** via `docker compose up -d`
- **Realistic attack simulations** including SWIFT heist patterns, MFS fraud, and BEFTN smurfing

### What Problems Does This Solve?

| Challenge | BankStack Solution |
|---|---|
| Banks need both Wazuh (XDR) and Splunk (SIEM) | Unified stack with alert forwarding |
| BD-specific compliance (BB ICT v4.0) | Pre-built compliance dashboard + SCA policy |
| SWIFT security (Bangladesh Bank heist 2016) | Custom SWIFT rules + active response lockdown |
| MFS fraud detection (bKash/Nagad) | Dedicated MFS monitoring + SIM swap detection |
| No realistic test data | Python banking log simulator with attack injection |
| Complex multi-service deployment | Single `docker compose up` command |

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
│               │ • Analytics       │◀────────────│ • 4 Dashboards││
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
5. **Splunk** receives Wazuh alerts via syslog forwarding (JSON/9515), runs 25+ SPL correlation searches across 4 dashboards
6. **Active Response** automatically triggers lockdown scripts (brute force blocking, web shell quarantine, SWIFT emergency lockdown)

### Network Architecture

| Service | Container | IP | Ports |
|---|---|---|---|
| Wazuh Indexer | bankstack-wazuh-indexer | 172.25.0.10 | 9200 |
| Wazuh Manager | bankstack-wazuh-manager | 172.25.0.11 | 1514, 1515, 514/udp, 55000 |
| Wazuh Dashboard | bankstack-wazuh-dashboard | 172.25.0.12 | 443→443 |
| Splunk | bankstack-splunk | 172.25.0.20 | 8000, 8088, 9515 |
| Log Simulator | bankstack-log-simulator | 172.25.0.30 | — |

---

## ✨ Features

### Wazuh Layer (XDR + Endpoint Security)

- **60+ Custom Rules** in `local_rules.xml` organized by banking domain:
  - Authentication & access control (100100-100107)
  - Brute force & account abuse (100110-100114)
  - Privilege escalation & control bypass (100120-100123)
  - Web application attacks (100130-100133)
  - SWIFT operations & heist patterns (100200-100207)
  - Core Banking System (CBS) monitoring (100220-100227)
  - MFS fraud — bKash/Nagad/Rocket (100240-100247)
  - BEFTN/NPSB/RTGS payment system anomalies (100260-100272)
  - ATM/POS fraud detection (100280-100285)
  - Agent banking monitoring (100290-100293)
  - BB ICT v4.0 / PCI DSS compliance (100300-100305)
  - Data exfiltration detection (100320-100323)
  - Insider threat indicators (100330-100332)
  - Network anomalies / C2 detection (100340-100343)
  - Card fraud patterns (100400-100403)
  - QR payment (Binimoy) security (100410-100413)

- **File Integrity Monitoring (FIM)** for:
  - SWIFT Alliance directories (`/opt/swift/`)
  - CBS directories (Ababil, Flora, Stelar, TCS BaNCS)
  - Payment system directories (BEFTN, NPSB, RTGS)
  - ATM software binaries

- **3 Active Response Scripts**:
  - `brute-force-lockout.sh` — IP blocking with iptables
  - `webshell-quarantine.sh` — Forensic isolation of web shells
  - `swift-lockdown.sh` — Emergency SWIFT environment lockdown

- **SCA Policy** — 25+ checks covering BB ICT v4.0, PCI DSS v4.0, and SWIFT CSP

### Splunk Layer (SIEM + Analytics)

- **25+ SPL Correlation Searches** covering:
  - Authentication attacks (brute force, distributed, after-hours)
  - SWIFT threat detection (after-hours transfers, sanctions, rapid burst)
  - CBS transaction fraud (high-value, backdated, maker-checker bypass)
  - MFS fraud (rapid cashout, PIN brute force, SIM swap, smurfing)
  - BEFTN/NPSB/RTGS anomalies (smurfing, settlement window)
  - ATM fraud (jackpotting, card country mismatch)
  - Data exfiltration and insider threats
  - Compliance monitoring (audit log tampering)

- **4 Pre-built Dashboards**:
  - **BB ICT v4.0 Compliance** — Real-time compliance scoring
  - **SOC KPI** — MTTD, MTTR, alert volume, severity distribution
  - **Banking Threat Monitor** — SWIFT, CBS, ATM, payment system alerts
  - **MFS Monitoring** — bKash/Nagad/Rocket transaction security

- **Bangladesh-Specific Lookups**:
  - 45+ BD bank codes with SWIFT BICs
  - MFS provider registry

### Banking Log Simulator

- **8 Log Generators**: CBS, SWIFT, MFS, AD/Auth, Firewall, ATM, BEFTN, RTGS
- **5 Attack Scenarios**: Brute force, transaction fraud, privilege escalation, SWIFT heist, data exfiltration
- **Realistic BD Banking Data**: BD bank codes, branch names, MFS providers, BDT amounts, BD phone numbers
- **Configurable**: Log rate, attack probability, CBS type (Ababil/Flora/Stelar)

---

## 🚀 Quick Start

### Prerequisites

- **Docker** 24.0+ and **Docker Compose** v2.20+
- **8 GB RAM** minimum (16 GB recommended)
- **20 GB** free disk space
- **OpenSSL** for certificate generation

### One-Command Deployment

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/BankStack.git
cd BankStack

# Full setup: generate certs + start all services
make setup
```

### Manual Step-by-Step

```bash
# 1. Generate SSL certificates
chmod +x scripts/generate-certs.sh scripts/health-check.sh
bash scripts/generate-certs.sh

# 2. Start all services
docker compose up -d

# 3. Check health
make status
```

### Access Points

| Service | URL | Credentials |
|---|---|---|
| Wazuh Dashboard | https://localhost:443 | admin / admin |
| Splunk Web | http://localhost:8000 | admin / BankStack@Splunk2026 |
| Wazuh API | https://localhost:55000 | wazuh-wui / BankStack@S0C2026 |

---

## 📁 Project Structure

```
BankStack/
├── docker-compose.yml              # Full stack orchestration
├── .env                            # Environment configuration
├── Makefile                        # Convenience commands
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
│   │       └── bd_banking_server.yml  # BB ICT + PCI DSS + SWIFT CSP
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
│       │   ├── inputs.conf
│       │   ├── props.conf
│       │   ├── transforms.conf
│       │   ├── savedsearches.conf  # 25+ SPL correlation searches
│       │   └── data/ui/views/
│       │       ├── bb_ict_compliance.xml
│       │       ├── soc_kpi.xml
│       │       ├── banking_threats.xml
│       │       └── mfs_monitoring.xml
│       └── lookups/
│           ├── bd_bank_codes.csv   # 45+ Bangladesh banks
│           └── mfs_providers.csv   # MFS provider registry
│
├── simulator/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── config.yml
│   ├── banklog_simulator.py        # Main simulator orchestrator
│   ├── generators/                  # 8 log generators
│   │   ├── cbs_logs.py             # Core Banking System
│   │   ├── swift_logs.py           # SWIFT messaging
│   │   ├── mfs_logs.py             # bKash/Nagad/Rocket
│   │   ├── ad_logs.py              # Active Directory/Auth
│   │   ├── firewall_logs.py        # Network/Firewall
│   │   ├── atm_logs.py             # ATM/POS
│   │   ├── beftn_logs.py           # BEFTN transfers
│   │   └── rtgs_logs.py            # RTGS transfers
│   └── attacks/                     # 5 attack scenarios
│       ├── brute_force.py
│       ├── transaction_fraud.py
│       ├── privilege_escalation.py
│       ├── swift_attack.py
│       └── data_exfiltration.py
│
├── scripts/
│   ├── generate-certs.sh           # SSL certificate generator
│   └── health-check.sh             # Service health checker
│
└── tests/
    ├── test_simulator.py            # Simulator unit tests
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
*Critical for bKash/Nagad fraud where attackers perform SIM swaps to take over accounts.*

**BEFTN Smurfing (Rule 100262)**
```xml
<rule id="100262" level="14" frequency="20" timeframe="600">
  <if_matched_sid>100260</if_matched_sid>
  <same_field>source_account</same_field>
  <description>BankStack: BEFTN smurfing — 20+ transfers from same account in 10 min</description>
</rule>
```
*Detects money laundering via transaction structuring through BEFTN.*

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

### Example SPL Query — SWIFT After Hours Transfer

```spl
index=bankstack_wazuh action="SWIFT_MSG_SENT"
| eval hour=strftime(_time, "%H")
| where hour >= 22 OR hour < 6
| table _time, user, data.msg_type, data.sender_bic, data.receiver_bic, data.amount_usd
```

---

## 📊 Splunk Dashboards

### 1. BB ICT v4.0 Compliance Dashboard
- Overall compliance score percentage
- BB ICT, PCI DSS, and SWIFT CSP violation counters
- Control-by-control status table
- Authentication and access control violation trends
- SCA assessment results

### 2. SOC KPI Dashboard
- Total alerts (24h) and critical alert counts
- Mean Time to Detect (MTTD)
- Active response action counter
- Alert volume trend (7-day)
- Top alert categories and source IPs
- Severity distribution

### 3. Banking Threat Monitor
- SWIFT/CBS/ATM/Payment system alert counters
- SWIFT transaction monitoring with destination countries
- CBS transaction volume by branch
- ATM threat map
- BEFTN/NPSB/RTGS anomaly table
- File integrity monitoring alerts

### 4. MFS Monitoring Dashboard
- MFS transaction volume by provider (bKash/Nagad/Rocket)
- SIM swap and PIN brute force alerts
- Suspicious activity table with severity coloring
- Cashout heatmap (hourly distribution)
- Top agents by transaction volume

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
| Transaction Fraud | After-hours transfers, rapid cashouts, smurfing | CBS backdating, MFS SIM swap + cashout, BEFTN structuring |
| Privilege Escalation | Role elevation, maker-checker bypass | Teller→admin, service account interactive login |
| SWIFT Heist | After-hours high-value transfers | Bangladesh Bank 2016 heist pattern replication |
| Data Exfiltration | Large uploads, bulk queries, DNS tunneling | USB on critical systems, 10K+ record extractions |

### Configuration

```bash
# Environment variables
LOG_RATE=10                  # Logs per second
ATTACK_PROBABILITY=0.15      # 15% chance per cycle
CBS_TYPE=ababil              # CBS platform type
```

---

## ⚡ Active Response Scripts

### 1. Brute Force Lockout (`brute-force-lockout.sh`)
- Triggered by Rule 100110 (5+ failed logins in 2 min)
- Blocks attacker IP via iptables and hosts.deny
- Auto-unblock after 1 hour timeout
- Skips private/loopback IPs

### 2. Web Shell Quarantine (`webshell-quarantine.sh`)
- Triggered by Rule 100130 (web shell detection)
- Moves web shell to quarantine directory
- Preserves forensic evidence (metadata, hashes)
- Sets file permissions to 000

### 3. SWIFT Lockdown (`swift-lockdown.sh`)
- Triggered by Rules 100201, 100202 (after-hours SWIFT, high-value)
- Sets SWIFT directories to read-only
- Blocks SWIFT network ports (48002, 48003, 7800)
- Locks all SWIFT operator accounts
- Creates lockdown flag for SOC review
- 2-hour timeout, requires manual review

---

## 📋 SCA Policy — BD Banking

Security Configuration Assessment with **25+ checks** covering three frameworks:

### Bangladesh Bank ICT Guidelines v4.0

| Section | Checks | Description |
|---|---|---|
| 5 | Password length, complexity, lockout, timeout | Authentication controls |
| 6 | Root login, SSH config, key auth | Access control |
| 8 | Auto updates | Patch management |
| 9 | Firewall, IP forwarding | Network security |
| 10 | TLS 1.2+ enforcement | Encryption |
| 11 | Audit daemon, syslog forwarding, retention | Logging & monitoring |

### SWIFT CSP Controls

| Control | Check |
|---|---|
| 1.1 | SWIFT environment restricted permissions |
| 2.2 | Security updates applied |
| 5.1 | Logical access control |

### PCI DSS v4.0

| Requirement | Check |
|---|---|
| 2.2.1 | Unnecessary services disabled |
| 10.5.1 | Audit logs protected |

---

## ✅ Compliance Coverage

| Framework | Coverage | Notes |
|---|---|---|
| BB ICT Guidelines v4.0 | Sections 5, 6, 8, 9, 10, 11, 12, 13 | Core compliance monitoring |
| PCI DSS v4.0 | Requirements 1, 2, 4, 6, 8, 10 | Card data protection |
| SWIFT CSP v2024 | Controls 1.1, 2.2, 5.1 | Mandatory security controls |

---

## 🧪 Testing

### Unit Tests (Simulator)

```bash
cd BankStack
python tests/test_simulator.py
```

Tests all 8 log generators and 5 attack scenarios for correct output format and decoder compatibility.

### Integration Tests (Full Stack)

```bash
# After services are running
make test
# Or directly:
bash tests/test_stack.sh
```

Tests:
- All 5 Docker containers running
- Service health endpoints responding
- Custom configurations loaded
- Log flow from simulator to Wazuh to Splunk

---

## ⚙️ Configuration

### Environment Variables (`.env`)

| Variable | Default | Description |
|---|---|---|
| `WAZUH_VERSION` | 4.9.2 | Wazuh Docker image version |
| `SPLUNK_VERSION` | 9.3 | Splunk Docker image version |
| `SPLUNK_PASSWORD` | BankStack@Splunk2026 | Splunk admin password |
| `INDEXER_PASSWORD` | SecureIndex@2026 | Wazuh Indexer admin password |
| `WAZUH_API_PASSWORD` | BankStack@S0C2026 | Wazuh API password |
| `SIMULATOR_LOG_RATE` | 10 | Logs per second |
| `SIMULATOR_ATTACK_PROBABILITY` | 0.15 | Attack injection rate |

### Makefile Commands

```bash
make setup        # Generate certs + start stack
make start        # Start all services
make stop         # Stop all services  
make restart      # Restart services
make status       # Show service health
make logs         # Follow all logs
make test         # Run integration tests
make clean        # Stop + remove all data (DESTRUCTIVE)
make shell-wazuh  # Shell into Wazuh Manager
make shell-splunk # Shell into Splunk
```

---

## 🎤 Interview Demo Guide

### 30-Second Pitch
> "Here's my home lab — a full banking SOC stack running Wazuh and Splunk with 60+ custom rules for Bangladesh banking. I can demo SWIFT attack detection, MFS fraud monitoring, and BB ICT v4.0 compliance right now."

### Demo Flow

1. **Show Architecture**: Explain the data flow from simulator → Wazuh → Splunk
2. **Wazuh Dashboard**: Show custom rules firing for SWIFT and CBS
3. **Splunk Dashboards**:
   - BB ICT v4.0 compliance score
   - SOC KPI metrics (MTTD, alert volume)
   - Banking threat monitor showing SWIFT alerts
   - MFS monitoring for bKash/Nagad
4. **Active Response**: Demonstrate SWIFT lockdown triggering
5. **Code Walk-through**: Show custom rules, decoders, and SPL searches

### Key Talking Points

- "Modeled SWIFT detection rules after the 2016 Bangladesh Bank heist pattern"
- "Custom SCA policy covers BB ICT v4.0 sections 5-13"
- "MFS fraud detection covers bKash SIM swap + rapid cashout chains"
- "BEFTN smurfing detection catches transaction structuring patterns"
- "Full compliance mapping: BB ICT v4.0 + PCI DSS v4.0 + SWIFT CSP"

---

## 🔧 Tech Stack

| Component | Technology | Version | Purpose |
|---|---|---|---|
| XDR Platform | Wazuh | 4.9.2 | Endpoint detection, FIM, active response |
| SIEM | Splunk Free | 9.3 | Log correlation, dashboards, SPL analytics |
| Search Engine | OpenSearch (Wazuh Indexer) | — | Alert storage and full-text search |
| Orchestration | Docker Compose | v2 | One-command deployment |
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
<sub>BankStack — Because every Bangladeshi bank needs a SOC, and every SOC analyst needs proof of skill.</sub>
</div>
