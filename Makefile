# ============================================================
# BankStack Makefile
# ============================================================

.PHONY: help setup certs start stop restart status logs clean test simulate-attack monitor resources backup restore

COMPOSE := $(shell command -v docker-compose 2>/dev/null || echo "docker compose")

# Docker socket connectivity check
_check-docker:
	@docker info >/dev/null 2>&1 || { \
		echo ""; \
		echo "ERROR: Cannot connect to Docker daemon (permission denied)."; \
		echo ""; \
		echo "  Fix with one of these:"; \
		echo "    1. newgrp docker          (activate docker group in current shell)"; \
		echo "    2. Log out and log back in (permanent fix)"; \
		echo "    3. sudo make <target>     (run as root)"; \
		echo ""; \
		exit 1; \
	}

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: _check-docker certs ## Full setup: generate certs and start stack
	@echo "[*] Starting BankStack SOC platform..."
	$(COMPOSE) up -d
	@echo "[*] Waiting for services to initialize..."
	@sleep 30
	@$(MAKE) status
	@echo ""
	@echo "============================================"
	@echo " BankStack SOC Platform Ready!"
	@echo "============================================"
	@echo " Wazuh Dashboard : https://localhost:443"
	@echo " Splunk Web      : http://localhost:8000"
	@echo " Wazuh API       : https://localhost:55000"
	@echo "============================================"

certs: ## Generate SSL certificates for Wazuh Indexer
	@echo "[*] Generating SSL certificates..."
	@bash scripts/generate-certs.sh

start: _check-docker ## Start all services
	$(COMPOSE) up -d

stop: _check-docker ## Stop all services
	$(COMPOSE) down

restart: _check-docker ## Restart all services
	$(COMPOSE) restart

status: _check-docker ## Show service status
	@$(COMPOSE) ps
	@echo ""
	@bash scripts/health-check.sh

logs: ## Follow all service logs
	$(COMPOSE) logs -f

logs-wazuh: ## Follow Wazuh Manager logs
	$(COMPOSE) logs -f wazuh-manager

logs-splunk: ## Follow Splunk logs
	$(COMPOSE) logs -f splunk

logs-simulator: ## Follow Log Simulator logs
	$(COMPOSE) logs -f log-simulator

clean: _check-docker ## Stop and remove all data (DESTRUCTIVE)
	@echo "[!] This will destroy all data. Press Ctrl+C to cancel..."
	@sleep 5
	$(COMPOSE) down -v
	rm -rf config/wazuh_indexer_ssl_certs/*.pem
	@echo "[*] Cleaned up."

test: _check-docker ## Run all tests
	@bash tests/test_stack.sh

simulate-attack: _check-docker ## Run attack simulation scenarios
	$(COMPOSE) exec log-simulator python -m attacks.run_all

build: _check-docker ## Rebuild simulator image
	$(COMPOSE) build log-simulator

shell-wazuh: _check-docker ## Open shell in Wazuh Manager
	$(COMPOSE) exec wazuh-manager bash

shell-splunk: _check-docker ## Open shell in Splunk
	$(COMPOSE) exec splunk bash

monitor: ## Live resource monitoring (Ctrl+C to stop)
	@docker stats --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}" \
		$$($(COMPOSE) ps -q)

resources: ## One-shot resource usage snapshot
	@docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}" \
		$$($(COMPOSE) ps -q)

backup: ## Backup all platform data
	@bash scripts/backup-restore.sh backup

restore: ## Restore from a backup (usage: make restore BACKUP=backups/<file>.tar.gz)
	@bash scripts/backup-restore.sh restore $(BACKUP)
