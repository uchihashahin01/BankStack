#!/bin/bash
# ================================================================
# BankStack — Active Response: Brute Force Lockout
# Blocks source IP after brute force detection on banking systems
# ================================================================

LOCAL=$(dirname "$0")
cd "$LOCAL" || exit 1
cd ../.. || exit 1
PWD=$(pwd)

# Logging
LOG_FILE="${PWD}/logs/active-responses.log"
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') brute-force-lockout: $1" >> "${LOG_FILE}"
}

# Read input from STDIN (Wazuh passes JSON)
read -r INPUT_JSON

ACTION=$(echo "${INPUT_JSON}" | python3 -c "import sys,json; print(json.load(sys.stdin).get('command',''))" 2>/dev/null)
SRCIP=$(echo "${INPUT_JSON}" | python3 -c "import sys,json; print(json.load(sys.stdin).get('parameters',{}).get('alert',{}).get('data',{}).get('srcip',''))" 2>/dev/null)
RULE_ID=$(echo "${INPUT_JSON}" | python3 -c "import sys,json; print(json.load(sys.stdin).get('parameters',{}).get('alert',{}).get('rule',{}).get('id',''))" 2>/dev/null)

if [ -z "${SRCIP}" ]; then
    log "ERROR: No source IP provided"
    exit 1
fi

# Validate IP format
if ! echo "${SRCIP}" | grep -qE '^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$'; then
    log "ERROR: Invalid IP format: ${SRCIP}"
    exit 1
fi

# Do not block private/loopback ranges
if echo "${SRCIP}" | grep -qE '^(127\.|10\.|172\.(1[6-9]|2[0-9]|3[01])\.|192\.168\.)'; then
    log "WARNING: Skipping private/loopback IP: ${SRCIP}"
    exit 0
fi

case "${ACTION}" in
    add)
        log "BLOCKING IP ${SRCIP} (Rule: ${RULE_ID})"
        # Block using iptables
        if command -v iptables &>/dev/null; then
            iptables -I INPUT -s "${SRCIP}" -j DROP 2>/dev/null
            iptables -I FORWARD -s "${SRCIP}" -j DROP 2>/dev/null
        fi
        # Also add to hosts.deny
        if [ -f /etc/hosts.deny ]; then
            echo "ALL: ${SRCIP}" >> /etc/hosts.deny
        fi
        log "BLOCKED ${SRCIP} successfully"
        ;;
    delete)
        log "UNBLOCKING IP ${SRCIP}"
        if command -v iptables &>/dev/null; then
            iptables -D INPUT -s "${SRCIP}" -j DROP 2>/dev/null
            iptables -D FORWARD -s "${SRCIP}" -j DROP 2>/dev/null
        fi
        if [ -f /etc/hosts.deny ]; then
            sed -i "/ALL: ${SRCIP//./\\.}/d" /etc/hosts.deny
        fi
        log "UNBLOCKED ${SRCIP} successfully"
        ;;
    *)
        log "ERROR: Unknown action: ${ACTION}"
        exit 1
        ;;
esac

exit 0
