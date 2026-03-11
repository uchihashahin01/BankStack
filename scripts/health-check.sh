#!/bin/bash
# ============================================================
# BankStack — Health Check Script
# ============================================================

set -uo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

check_service() {
    local name=$1
    local container=$2
    local check_cmd=$3

    if docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
        if docker inspect --format='{{.State.Health.Status}}' "${container}" 2>/dev/null | grep -q "healthy"; then
            echo -e "  ${GREEN}✓${NC} ${name}: healthy"
        else
            echo -e "  ${YELLOW}●${NC} ${name}: running (initializing)"
        fi
    else
        echo -e "  ${RED}✗${NC} ${name}: not running"
    fi
}

echo ""
echo "BankStack Service Health"
echo "========================"
check_service "Wazuh Indexer"   "bankstack-wazuh-indexer"   ""
check_service "Wazuh Manager"   "bankstack-wazuh-manager"   ""
check_service "Wazuh Dashboard" "bankstack-wazuh-dashboard" ""
check_service "Splunk"          "bankstack-splunk"          ""
check_service "Log Simulator"   "bankstack-log-simulator"   ""
echo ""
echo "Access Points:"
echo "  Wazuh Dashboard : https://localhost:443"
echo "  Splunk Web      : http://localhost:8000"
echo "  Wazuh API       : https://localhost:55000"
echo ""
