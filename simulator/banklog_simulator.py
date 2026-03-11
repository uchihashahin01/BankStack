"""
BankStack — Banking Log Simulator
Generates realistic Bangladesh banking logs with attack injection.
Sends logs to Wazuh (syslog) and Splunk (HEC).
"""

import json
import logging
import os
import random
import signal
import socket
import sys
import time
import urllib3
from datetime import datetime, timezone, timedelta

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from generators.cbs_logs import CBSLogGenerator
from generators.swift_logs import SWIFTLogGenerator
from generators.mfs_logs import MFSLogGenerator
from generators.ad_logs import ADLogGenerator
from generators.firewall_logs import FirewallLogGenerator
from generators.atm_logs import ATMLogGenerator
from generators.beftn_logs import BEFTNLogGenerator
from generators.rtgs_logs import RTGSLogGenerator
from attacks.brute_force import BruteForceAttack
from attacks.transaction_fraud import TransactionFraudAttack
from attacks.privilege_escalation import PrivilegeEscalationAttack
from attacks.swift_attack import SWIFTAttack
from attacks.data_exfiltration import DataExfiltrationAttack

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("bankstack-simulator")

BST = timezone(timedelta(hours=6))

# Graceful shutdown
running = True

def signal_handler(_sig, _frame):
    global running
    logger.info("Shutdown signal received, stopping...")
    running = False

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


class SyslogSender:
    """Sends logs to Wazuh via UDP syslog."""

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, message: str):
        try:
            data = message.encode("utf-8")
            self.sock.sendto(data, (self.host, self.port))
        except OSError as e:
            logger.error("Syslog send failed: %s", e)

    def close(self):
        self.sock.close()


class HECSender:
    """Sends logs to Splunk via HTTP Event Collector."""

    def __init__(self, url: str, token: str, verify_ssl: bool = False):
        self.url = url + "/services/collector/event"
        self.token = token
        self.verify_ssl = verify_ssl

    def send(self, event: dict, sourcetype: str = "bankstack:simulator"):
        import requests
        payload = {
            "event": event,
            "sourcetype": sourcetype,
            "index": "bankstack_banking",
            "time": time.time(),
        }
        try:
            requests.post(
                self.url,
                json=payload,
                headers={"Authorization": f"Splunk {self.token}"},
                verify=self.verify_ssl,
                timeout=5,
            )
        except Exception as e:
            logger.debug("HEC send failed (non-critical): %s", e)


class BankLogSimulator:
    """Main simulator orchestrator."""

    def __init__(self):
        self.log_rate = int(os.environ.get("LOG_RATE", "10"))
        self.attack_prob = float(os.environ.get("ATTACK_PROBABILITY", "0.15"))

        wazuh_host = os.environ.get("WAZUH_MANAGER_HOST", "wazuh-manager")
        wazuh_port = int(os.environ.get("WAZUH_SYSLOG_PORT", "514"))
        self.syslog = SyslogSender(wazuh_host, wazuh_port)

        splunk_url = os.environ.get("SPLUNK_HEC_URL", "https://splunk:8088")
        splunk_token = os.environ.get("SPLUNK_HEC_TOKEN", "")
        self.hec = HECSender(splunk_url, splunk_token)

        # Initialize generators
        self.generators = [
            CBSLogGenerator(weight=0.30),
            SWIFTLogGenerator(weight=0.10),
            MFSLogGenerator(weight=0.20),
            ADLogGenerator(weight=0.10),
            FirewallLogGenerator(weight=0.10),
            ATMLogGenerator(weight=0.10),
            BEFTNLogGenerator(weight=0.05),
            RTGSLogGenerator(weight=0.05),
        ]

        # Initialize attack generators
        self.attacks = [
            BruteForceAttack(weight=0.20),
            TransactionFraudAttack(weight=0.25),
            PrivilegeEscalationAttack(weight=0.15),
            SWIFTAttack(weight=0.15),
            DataExfiltrationAttack(weight=0.10),
        ]

        self.stats = {"total_logs": 0, "attacks_injected": 0, "start_time": time.time()}

    def _pick_generator(self):
        weights = [g.weight for g in self.generators]
        return random.choices(self.generators, weights=weights, k=1)[0]

    def _pick_attack(self):
        weights = [a.weight for a in self.attacks]
        return random.choices(self.attacks, weights=weights, k=1)[0]

    def _emit(self, log_line: str, event_data: dict = None):
        self.syslog.send(log_line)
        if event_data:
            self.hec.send(event_data)
        self.stats["total_logs"] += 1

    def run(self):
        logger.info("=" * 60)
        logger.info("BankStack Banking Log Simulator")
        logger.info("=" * 60)
        logger.info("Log rate: %d logs/sec", self.log_rate)
        logger.info("Attack probability: %.0f%%", self.attack_prob * 100)
        logger.info(
            "Syslog target: %s:%d", self.syslog.host, self.syslog.port
        )
        logger.info("Starting log generation...")
        logger.info("=" * 60)

        interval = 1.0 / self.log_rate if self.log_rate > 0 else 1.0

        while running:
            try:
                # Normal log generation
                gen = self._pick_generator()
                log_line, event_data = gen.generate()
                self._emit(log_line, event_data)

                # Attack injection
                if random.random() < self.attack_prob:
                    attack = self._pick_attack()
                    attack_logs = attack.generate()
                    for a_line, a_data in attack_logs:
                        self._emit(a_line, a_data)
                        self.stats["attacks_injected"] += 1
                        time.sleep(0.05)  # Small delay between attack logs

                # Periodic stats
                if self.stats["total_logs"] % 500 == 0 and self.stats["total_logs"] > 0:
                    elapsed = time.time() - self.stats["start_time"]
                    rate = self.stats["total_logs"] / elapsed if elapsed > 0 else 0
                    logger.info(
                        "Stats: %d logs sent (%.1f/sec), %d attacks injected",
                        self.stats["total_logs"],
                        rate,
                        self.stats["attacks_injected"],
                    )

                time.sleep(interval)

            except Exception as e:
                logger.error("Generation error: %s", e)
                time.sleep(1)

        logger.info("Simulator stopped. Total: %d logs, %d attacks",
                     self.stats["total_logs"], self.stats["attacks_injected"])
        self.syslog.close()


if __name__ == "__main__":
    # Wait for dependent services
    logger.info("Waiting for services to initialize...")
    time.sleep(15)

    simulator = BankLogSimulator()
    simulator.run()
