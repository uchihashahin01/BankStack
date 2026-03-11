"""Compliance event log generator (BB ICT v4.0 / PCI DSS)."""

import random
from datetime import datetime, timezone, timedelta

BST = timezone(timedelta(hours=6))

COMPLIANCE_EVENTS = [
    # (action, system, data_type, detail, weight)
    ("AUDIT_LOG_CLEARED", "CBS", "audit", "manual_clear", 5),
    ("AUDIT_LOG_CLEARED", "SWIFT", "audit", "cron_misconfigured", 3),
    ("UNENCRYPTED_DATA", "CBS", "card", "plaintext_pan_in_log", 5),
    ("UNENCRYPTED_DATA", "IBANKING", "pin", "pin_logged_cleartext", 3),
    ("UNENCRYPTED_DATA", "ATM", "cvv", "cvv_in_transaction_log", 3),
    ("UNENCRYPTED_DATA", "CBS", "account", "account_number_exposed", 4),
    ("PATCH_OVERDUE", "CBS", "os", "windows_server_2019_eol", 8),
    ("PATCH_OVERDUE", "SWIFT", "app", "alliance_lite2_outdated", 5),
    ("PATCH_OVERDUE", "ATM", "firmware", "ncr_firmware_v3.1", 6),
    ("BACKUP_FAILED", "CBS", "database", "oracle_rman_timeout", 6),
    ("BACKUP_FAILED", "SWIFT", "config", "alliance_backup_err", 4),
    ("DR_TEST_OVERDUE", "CBS", "dr", "last_test_180d_ago", 3),
    ("DR_TEST_OVERDUE", "SWIFT", "dr", "no_test_recorded", 2),
    ("ACCESS_REVIEW_OVERDUE", "CBS", "iam", "quarterly_review_missed", 5),
    ("ACCESS_REVIEW_OVERDUE", "SWIFT", "iam", "annual_review_overdue", 3),
]


class ComplianceLogGenerator:
    def __init__(self, weight: float = 0.02):
        self.weight = weight

    def generate(self) -> tuple[str, dict]:
        now = datetime.now(BST)
        actions = COMPLIANCE_EVENTS
        weights = [e[4] for e in actions]
        action, system, data_type, detail, _ = random.choices(
            actions, weights=weights, k=1
        )[0]

        log_line = (
            f"BANKSTACK_COMPLIANCE: {action} system={system} "
            f"data_type={data_type} detail={detail}"
        )
        event = {
            "timestamp": now.isoformat(),
            "source": "compliance",
            "action": action,
            "system": system,
            "data_type": data_type,
            "detail": detail,
        }
        return log_line, event
