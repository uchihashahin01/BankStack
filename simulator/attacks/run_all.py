"""
BankStack — On-Demand Attack Burst Runner
Triggers all 5 attack types simultaneously for SOC testing.
Usage: python -m attacks.run_all
"""

import os
import socket
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from attacks.brute_force import BruteForceAttack
from attacks.transaction_fraud import TransactionFraudAttack
from attacks.privilege_escalation import PrivilegeEscalationAttack
from attacks.swift_attack import SWIFTAttack
from attacks.data_exfiltration import DataExfiltrationAttack


def main():
    wazuh_host = os.environ.get("WAZUH_MANAGER_HOST", "wazuh-manager")
    wazuh_port = int(os.environ.get("WAZUH_SYSLOG_PORT", "514"))
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    attacks = [
        ("Brute Force", BruteForceAttack()),
        ("Transaction Fraud", TransactionFraudAttack()),
        ("Privilege Escalation", PrivilegeEscalationAttack()),
        ("SWIFT Heist", SWIFTAttack()),
        ("Data Exfiltration", DataExfiltrationAttack()),
    ]

    print("=" * 60)
    print("BankStack — On-Demand Attack Burst")
    print("=" * 60)
    total = 0

    for name, attack in attacks:
        logs = attack.generate()
        print(f"[*] {name}: generating {len(logs)} events...")
        for log_line, _ in logs:
            sock.sendto(log_line.encode("utf-8"), (wazuh_host, wazuh_port))
            total += 1
            time.sleep(0.02)
        print(f"    ✓ {name} complete")

    sock.close()
    print("=" * 60)
    print(f"Attack burst complete: {total} events sent to Wazuh")
    print("Check Wazuh Dashboard and Splunk for high-severity alerts.")
    print("=" * 60)


if __name__ == "__main__":
    main()
