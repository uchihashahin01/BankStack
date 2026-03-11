#!/usr/bin/env bash
# ============================================================
# BankStack — Backup and Restore Utility
# ============================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="$PROJECT_DIR/backups"
COMPOSE=$(command -v docker-compose 2>/dev/null || echo "docker compose")

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

usage() {
    echo "Usage: $0 {backup|restore <backup-file>}"
    echo ""
    echo "Commands:"
    echo "  backup              Create a timestamped backup of all data"
    echo "  restore <file>      Restore from a backup archive"
    echo ""
    echo "Example:"
    echo "  $0 backup"
    echo "  $0 restore backups/bankstack-backup-20260311-143000.tar.gz"
    exit 1
}

do_backup() {
    mkdir -p "$BACKUP_DIR"
    TIMESTAMP=$(date +%Y%m%d-%H%M%S)
    BACKUP_FILE="$BACKUP_DIR/bankstack-backup-${TIMESTAMP}.tar.gz"
    TMP_DIR=$(mktemp -d)

    echo -e "${GREEN}[*] BankStack Backup — $TIMESTAMP${NC}"
    echo "[*] Exporting Wazuh Manager data..."
    $COMPOSE exec -T wazuh-manager tar czf - \
        /var/ossec/logs/alerts/ \
        /var/ossec/logs/archives/ \
        /var/ossec/stats/ \
        2>/dev/null > "$TMP_DIR/wazuh-manager-data.tar.gz" || true

    echo "[*] Exporting Wazuh Indexer data..."
    $COMPOSE exec -T wazuh-indexer tar czf - \
        /var/lib/wazuh-indexer/ \
        2>/dev/null > "$TMP_DIR/wazuh-indexer-data.tar.gz" || true

    echo "[*] Exporting Splunk data..."
    $COMPOSE exec -T splunk tar czf - \
        /opt/splunk/var/lib/splunk/ \
        2>/dev/null > "$TMP_DIR/splunk-data.tar.gz" || true

    echo "[*] Backing up configuration files..."
    tar czf "$TMP_DIR/configs.tar.gz" \
        -C "$PROJECT_DIR" \
        docker-compose.yml \
        .env \
        wazuh/ \
        splunk/ \
        simulator/ \
        2>/dev/null || true

    echo "[*] Creating final backup archive..."
    tar czf "$BACKUP_FILE" -C "$TMP_DIR" .
    rm -rf "$TMP_DIR"

    SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo -e "${GREEN}[✓] Backup complete: $BACKUP_FILE ($SIZE)${NC}"
}

do_restore() {
    local BACKUP_FILE="$1"

    if [[ ! -f "$BACKUP_FILE" ]]; then
        echo -e "${RED}[!] Backup file not found: $BACKUP_FILE${NC}"
        exit 1
    fi

    echo -e "${YELLOW}[!] WARNING: This will stop all services and replace current data.${NC}"
    echo -e "${YELLOW}    Press Ctrl+C within 5 seconds to cancel.${NC}"
    sleep 5

    echo "[*] Stopping services..."
    cd "$PROJECT_DIR"
    $COMPOSE down

    TMP_DIR=$(mktemp -d)
    echo "[*] Extracting backup..."
    tar xzf "$BACKUP_FILE" -C "$TMP_DIR"

    echo "[*] Starting services (empty)..."
    $COMPOSE up -d
    echo "[*] Waiting 60s for services to initialize..."
    sleep 60

    if [[ -f "$TMP_DIR/wazuh-manager-data.tar.gz" ]]; then
        echo "[*] Restoring Wazuh Manager data..."
        cat "$TMP_DIR/wazuh-manager-data.tar.gz" | \
            $COMPOSE exec -T wazuh-manager tar xzf - -C / 2>/dev/null || true
    fi

    if [[ -f "$TMP_DIR/wazuh-indexer-data.tar.gz" ]]; then
        echo "[*] Restoring Wazuh Indexer data..."
        cat "$TMP_DIR/wazuh-indexer-data.tar.gz" | \
            $COMPOSE exec -T wazuh-indexer tar xzf - -C / 2>/dev/null || true
    fi

    if [[ -f "$TMP_DIR/splunk-data.tar.gz" ]]; then
        echo "[*] Restoring Splunk data..."
        cat "$TMP_DIR/splunk-data.tar.gz" | \
            $COMPOSE exec -T splunk tar xzf - -C / 2>/dev/null || true
    fi

    rm -rf "$TMP_DIR"

    echo "[*] Restarting services..."
    $COMPOSE restart
    sleep 30

    echo -e "${GREEN}[✓] Restore complete. Services restarting.${NC}"
    echo "[*] Run 'make status' to check service health."
}

# --- Main ---
case "${1:-}" in
    backup)
        do_backup
        ;;
    restore)
        [[ -z "${2:-}" ]] && usage
        do_restore "$2"
        ;;
    *)
        usage
        ;;
esac
