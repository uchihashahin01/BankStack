"""Tests for Banking Log Simulator generators and attacks."""

import sys
import os
import pytest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulator.generators.cbs_logs import CBSLogGenerator
from simulator.generators.swift_logs import SWIFTLogGenerator
from simulator.generators.mfs_logs import MFSLogGenerator
from simulator.generators.ad_logs import ADLogGenerator
from simulator.generators.firewall_logs import FirewallLogGenerator
from simulator.generators.atm_logs import ATMLogGenerator
from simulator.generators.beftn_logs import BEFTNLogGenerator
from simulator.generators.rtgs_logs import RTGSLogGenerator
from simulator.attacks.brute_force import BruteForceAttack
from simulator.attacks.transaction_fraud import TransactionFraudAttack
from simulator.attacks.privilege_escalation import PrivilegeEscalationAttack
from simulator.attacks.swift_attack import SWIFTAttack
from simulator.attacks.data_exfiltration import DataExfiltrationAttack


GENERATORS = [
    (CBSLogGenerator, "CBS Log Generator"),
    (SWIFTLogGenerator, "SWIFT Log Generator"),
    (MFSLogGenerator, "MFS Log Generator"),
    (ADLogGenerator, "AD Log Generator"),
    (FirewallLogGenerator, "Firewall Log Generator"),
    (ATMLogGenerator, "ATM Log Generator"),
    (BEFTNLogGenerator, "BEFTN Log Generator"),
    (RTGSLogGenerator, "RTGS Log Generator"),
]

ATTACKS = [
    (BruteForceAttack, "Brute Force Attack"),
    (TransactionFraudAttack, "Transaction Fraud Attack"),
    (PrivilegeEscalationAttack, "Privilege Escalation Attack"),
    (SWIFTAttack, "SWIFT Attack"),
    (DataExfiltrationAttack, "Data Exfiltration Attack"),
]


def _check_generator(gen_class, name):
    gen = gen_class()
    for _ in range(10):
        log_line, event = gen.generate()
        assert isinstance(log_line, str), f"{name}: log_line is not string"
        assert len(log_line) > 10, f"{name}: log_line too short"
        assert isinstance(event, dict), f"{name}: event is not dict"
        assert "timestamp" in event, f"{name}: missing timestamp"
        assert "action" in event, f"{name}: missing action"
        assert "source" in event, f"{name}: missing source"


def _check_attack(attack_class, name):
    attack = attack_class()
    for _ in range(5):
        logs = attack.generate()
        assert isinstance(logs, list), f"{name}: result is not list"
        assert len(logs) >= 1, f"{name}: no logs generated"
        for log_line, event in logs:
            assert isinstance(log_line, str), f"{name}: log_line is not string"
            assert isinstance(event, dict), f"{name}: event is not dict"


@pytest.mark.parametrize("gen_class,name", GENERATORS)
def test_generator(gen_class, name):
    _check_generator(gen_class, name)


@pytest.mark.parametrize("attack_class,name", ATTACKS)
def test_attack(attack_class, name):
    _check_attack(attack_class, name)


def test_decoder_format():
    """Verify log lines match expected decoder patterns."""
    generators = [
        (CBSLogGenerator, "BANKSTACK_CBS:"),
        (SWIFTLogGenerator, "BANKSTACK_SWIFT:"),
        (MFSLogGenerator, "BANKSTACK_MFS:"),
        (ADLogGenerator, "BANKSTACK_AUTH:"),
        (FirewallLogGenerator, "BANKSTACK_FW:"),
        (ATMLogGenerator, "BANKSTACK_ATM:"),
        (BEFTNLogGenerator, "BANKSTACK_BEFTN:"),
        (RTGSLogGenerator, "BANKSTACK_RTGS:"),
    ]

    for gen_class, prefix in generators:
        gen = gen_class()
        log_line, _ = gen.generate()
        assert log_line.startswith(prefix), \
            f"Expected prefix '{prefix}', got: {log_line[:30]}"
    print("  [PASS] All decoder prefixes match expected patterns")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("BankStack — Simulator Unit Tests")
    print("=" * 60)

    print("\n[*] Testing log generators...")
    for gen_class, name in GENERATORS:
        _check_generator(gen_class, name)
        print(f"  [PASS] {name} — 10 logs generated successfully")

    print("\n[*] Testing attack generators...")
    for attack_class, name in ATTACKS:
        _check_attack(attack_class, name)
        print(f"  [PASS] {name} — 5 attack sequences generated successfully")
    print("\n[*] Testing decoder format compatibility...")
    test_decoder_format()

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED")
    print("=" * 60 + "\n")
