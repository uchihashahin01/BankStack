#!/bin/bash
# ================================================================
# BankStack — Active Response: Web Shell Quarantine
# Quarantines detected web shells on banking web servers
# ================================================================

LOCAL=$(dirname "$0")
cd "$LOCAL" || exit 1
cd ../.. || exit 1
PWD=$(pwd)

LOG_FILE="${PWD}/logs/active-responses.log"
QUARANTINE_DIR="${PWD}/quarantine/webshells"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') webshell-quarantine: $1" >> "${LOG_FILE}"
}

read -r INPUT_JSON

FILENAME=$(echo "${INPUT_JSON}" | python3 -c "
import sys, json
data = json.load(sys.stdin)
syscheck = data.get('parameters',{}).get('alert',{}).get('syscheck',{})
print(syscheck.get('path',''))
" 2>/dev/null)

if [ -z "${FILENAME}" ]; then
    log "ERROR: No filename provided"
    exit 1
fi

# Only quarantine files from web-accessible directories
ALLOWED_PATHS="/var/www|/opt/web|/srv/http|/opt/ibanking|/opt/cbs/web"
if ! echo "${FILENAME}" | grep -qE "^(${ALLOWED_PATHS})"; then
    log "WARNING: File not in web directory, skipping: ${FILENAME}"
    exit 0
fi

# Create quarantine directory
mkdir -p "${QUARANTINE_DIR}"

if [ -f "${FILENAME}" ]; then
    TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
    QUARANTINE_NAME="${QUARANTINE_DIR}/$(basename "${FILENAME}")_${TIMESTAMP}"

    # Preserve metadata
    stat "${FILENAME}" > "${QUARANTINE_NAME}.meta" 2>/dev/null
    md5sum "${FILENAME}" >> "${QUARANTINE_NAME}.meta" 2>/dev/null
    sha256sum "${FILENAME}" >> "${QUARANTINE_NAME}.meta" 2>/dev/null

    # Move to quarantine
    mv "${FILENAME}" "${QUARANTINE_NAME}"
    chmod 000 "${QUARANTINE_NAME}"

    log "QUARANTINED: ${FILENAME} -> ${QUARANTINE_NAME}"
    log "Evidence preserved at: ${QUARANTINE_NAME}.meta"
else
    log "WARNING: File not found: ${FILENAME}"
fi

exit 0
