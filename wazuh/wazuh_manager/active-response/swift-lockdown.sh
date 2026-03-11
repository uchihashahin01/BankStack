#!/bin/bash
# ================================================================
# BankStack — Active Response: SWIFT Lockdown
# Emergency lockdown of SWIFT environment upon threat detection
# ================================================================

LOCAL=$(dirname "$0")
cd "$LOCAL" || exit 1
cd ../.. || exit 1
PWD=$(pwd)

LOG_FILE="${PWD}/logs/active-responses.log"
SWIFT_DIR="/opt/swift"
LOCKDOWN_FLAG="${PWD}/var/swift_lockdown.flag"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') swift-lockdown: $1" >> "${LOG_FILE}"
}

read -r INPUT_JSON

ACTION=$(echo "${INPUT_JSON}" | python3 -c "import sys,json; print(json.load(sys.stdin).get('command',''))" 2>/dev/null)
RULE_ID=$(echo "${INPUT_JSON}" | python3 -c "import sys,json; print(json.load(sys.stdin).get('parameters',{}).get('alert',{}).get('rule',{}).get('id',''))" 2>/dev/null)
USER=$(echo "${INPUT_JSON}" | python3 -c "import sys,json; print(json.load(sys.stdin).get('parameters',{}).get('alert',{}).get('data',{}).get('user','unknown'))" 2>/dev/null)

case "${ACTION}" in
    add)
        log "SWIFT LOCKDOWN INITIATED — Rule: ${RULE_ID}, User: ${USER}"

        # 1. Set SWIFT directories to read-only
        if [ -d "${SWIFT_DIR}" ]; then
            chmod -R a-w "${SWIFT_DIR}" 2>/dev/null
            log "SWIFT directory set to read-only: ${SWIFT_DIR}"
        fi

        # 2. Block SWIFT network ports (FIN messaging)
        if command -v iptables &>/dev/null; then
            # Block SWIFT Alliance Lite2 and SWIFTNet ports
            iptables -I OUTPUT -p tcp --dport 48002 -j DROP 2>/dev/null
            iptables -I OUTPUT -p tcp --dport 48003 -j DROP 2>/dev/null
            iptables -I OUTPUT -p tcp --dport 7800 -j DROP 2>/dev/null
            log "SWIFT network ports blocked (48002, 48003, 7800)"
        fi

        # 3. Lock SWIFT operator accounts
        if command -v getent &>/dev/null; then
            getent group swift-operators 2>/dev/null | cut -d: -f4 | tr ',' '\n' | while read -r swift_user; do
                if [ -n "${swift_user}" ]; then
                    passwd -l "${swift_user}" 2>/dev/null
                    log "Locked SWIFT operator account: ${swift_user}"
                fi
            done
        fi

        # 4. Create lockdown flag
        mkdir -p "$(dirname "${LOCKDOWN_FLAG}")"
        echo "LOCKDOWN_TIME=$(date -Iseconds)" > "${LOCKDOWN_FLAG}"
        echo "TRIGGER_RULE=${RULE_ID}" >> "${LOCKDOWN_FLAG}"
        echo "TRIGGER_USER=${USER}" >> "${LOCKDOWN_FLAG}"

        log "SWIFT LOCKDOWN COMPLETE — Manual review required before restoration"
        ;;

    delete)
        log "SWIFT LOCKDOWN RELEASE INITIATED"

        # 1. Restore SWIFT directory permissions
        if [ -d "${SWIFT_DIR}" ]; then
            chmod -R u+w "${SWIFT_DIR}" 2>/dev/null
            log "SWIFT directory write permissions restored"
        fi

        # 2. Unblock SWIFT network ports
        if command -v iptables &>/dev/null; then
            iptables -D OUTPUT -p tcp --dport 48002 -j DROP 2>/dev/null
            iptables -D OUTPUT -p tcp --dport 48003 -j DROP 2>/dev/null
            iptables -D OUTPUT -p tcp --dport 7800 -j DROP 2>/dev/null
            log "SWIFT network ports unblocked"
        fi

        # 3. Unlock SWIFT operator accounts
        if command -v getent &>/dev/null; then
            getent group swift-operators 2>/dev/null | cut -d: -f4 | tr ',' '\n' | while read -r swift_user; do
                if [ -n "${swift_user}" ]; then
                    passwd -u "${swift_user}" 2>/dev/null
                    log "Unlocked SWIFT operator account: ${swift_user}"
                fi
            done
        fi

        # 4. Remove lockdown flag
        rm -f "${LOCKDOWN_FLAG}"

        log "SWIFT LOCKDOWN RELEASED"
        ;;

    *)
        log "ERROR: Unknown action: ${ACTION}"
        exit 1
        ;;
esac

exit 0
