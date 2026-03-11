#!/bin/bash
# ============================================================
# BankStack — Integration Test Suite
# Tests the full stack deployment
# ============================================================

set -uo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'
PASS=0
FAIL=0

assert_true() {
    local desc=$1
    local cmd=$2
    if eval "${cmd}" &>/dev/null; then
        echo -e "  ${GREEN}✓${NC} ${desc}"
        ((PASS++))
    else
        echo -e "  ${RED}✗${NC} ${desc}"
        ((FAIL++))
    fi
}

echo ""
echo "============================================"
echo " BankStack Integration Tests"
echo "============================================"

# --- Docker Container Tests ---
echo ""
echo "[*] Docker Container Status"
assert_true "Wazuh Indexer is running" \
    "docker ps --format '{{.Names}}' | grep -q bankstack-wazuh-indexer"
assert_true "Wazuh Manager is running" \
    "docker ps --format '{{.Names}}' | grep -q bankstack-wazuh-manager"
assert_true "Wazuh Dashboard is running" \
    "docker ps --format '{{.Names}}' | grep -q bankstack-wazuh-dashboard"
assert_true "Splunk is running" \
    "docker ps --format '{{.Names}}' | grep -q bankstack-splunk"
assert_true "Log Simulator is running" \
    "docker ps --format '{{.Names}}' | grep -q bankstack-log-simulator"

# --- Service Health Tests ---
echo ""
echo "[*] Service Health Checks"
assert_true "Wazuh Indexer API responds" \
    "curl -sku admin:SecureIndex@2026 https://localhost:9200/_cluster/health 2>/dev/null | grep -qE 'green|yellow'"
assert_true "Wazuh API responds" \
    "curl -sku wazuh-wui:BankStack@S0C2026 -k https://localhost:55000/ 2>/dev/null | grep -q 'data'"
assert_true "Splunk Web responds" \
    "curl -sf http://localhost:8000/en-US/account/login 2>/dev/null | grep -qi splunk"
assert_true "Wazuh Dashboard responds" \
    "curl -sk https://localhost:443/api/status 2>/dev/null | grep -q available"

# --- Configuration Tests ---
echo ""
echo "[*] Custom Configuration Loaded"
assert_true "Custom rules file exists in container" \
    "docker exec bankstack-wazuh-manager test -f /var/ossec/etc/rules/local_rules.xml"
assert_true "Custom decoders file exists" \
    "docker exec bankstack-wazuh-manager test -f /var/ossec/etc/decoders/local_decoder.xml"
assert_true "Active response scripts exist" \
    "docker exec bankstack-wazuh-manager test -f /var/ossec/active-response/bin/swift-lockdown.sh"
assert_true "Splunk BankStack app loaded" \
    "docker exec bankstack-splunk test -d /opt/splunk/etc/apps/bankstack"

# --- Log Flow Tests ---
echo ""
echo "[*] Log Flow Verification"
assert_true "Simulator sending syslog to Wazuh" \
    "docker logs bankstack-log-simulator 2>&1 | tail -5 | grep -q 'logs sent'"
assert_true "Wazuh indexer has data" \
    "curl -sku admin:SecureIndex@2026 'https://localhost:9200/wazuh-alerts-*/_count' 2>/dev/null | grep -q 'count'"

echo ""
echo "============================================"
echo -e " Results: ${GREEN}${PASS} passed${NC}, ${RED}${FAIL} failed${NC}"
echo "============================================"
echo ""

if [ "${FAIL}" -gt 0 ]; then
    exit 1
fi
