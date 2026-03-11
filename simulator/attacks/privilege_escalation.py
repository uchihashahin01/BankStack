"""Privilege escalation attack simulation."""

import random
from datetime import datetime, timezone, timedelta

BST = timezone(timedelta(hours=6))


class PrivilegeEscalationAttack:
    def __init__(self, weight: float = 0.15):
        self.weight = weight

    def generate(self) -> list[tuple[str, dict]]:
        scenario = random.choice([
            self._role_elevation,
            self._maker_checker_bypass,
            self._service_account_abuse,
        ])
        return scenario()

    def _role_elevation(self) -> list[tuple[str, dict]]:
        now = datetime.now(BST)
        user = random.choice(["teller_003", "it_support_01", "hr_nusrat"])
        new_role = random.choice(["admin", "dba", "swift_operator", "super_user"])

        log_line = (
            f"BANKSTACK_AUTH: ROLE_CHANGE user={user} user_role=standard "
            f"new_role={new_role}"
        )
        event = {
            "timestamp": now.isoformat(),
            "source": "auth",
            "action": "ROLE_CHANGE",
            "user": user,
            "user_role": "standard",
            "new_role": new_role,
            "attack_type": "privilege_escalation",
        }
        return [(log_line, event)]

    def _maker_checker_bypass(self) -> list[tuple[str, dict]]:
        now = datetime.now(BST)
        user = random.choice(["officer_001", "manager_002"])

        log_line = (
            f"BANKSTACK_CBS: MAKER_CHECKER_BYPASS txn_type=transfer "
            f"account=1{random.randint(100, 999)}{random.randint(100000, 999999)} "
            f"amount_bdt={random.randint(1000000, 50000000)} user={user} branch=0101"
        )
        event = {
            "timestamp": now.isoformat(),
            "source": "cbs",
            "action": "MAKER_CHECKER_BYPASS",
            "user": user,
            "attack_type": "control_bypass",
        }
        return [(log_line, event)]

    def _service_account_abuse(self) -> list[tuple[str, dict]]:
        now = datetime.now(BST)
        src_ip = f"{random.choice([45, 91, 185])}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"

        log_line = (
            f"BANKSTACK_AUTH: LOGIN_SUCCESS user=batch_scheduler src={src_ip} "
            f"system=CBS user_type=service_account source_country=UNKNOWN"
        )
        event = {
            "timestamp": now.isoformat(),
            "source": "auth",
            "action": "LOGIN_SUCCESS",
            "user": "batch_scheduler",
            "user_type": "service_account",
            "srcip": src_ip,
            "system": "CBS",
            "attack_type": "service_account_abuse",
        }
        return [(log_line, event)]
