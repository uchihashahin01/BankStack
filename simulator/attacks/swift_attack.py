"""SWIFT-specific attack simulation — modeled after real banking heist patterns."""

import random
from datetime import datetime, timezone, timedelta

BST = timezone(timedelta(hours=6))

SANCTIONED_COUNTRIES = [("KP", "KKBKKP22"), ("IR", "BMJIIRTH"), ("SY", "CBSYSYDA")]
HIGH_RISK_COUNTRIES = [("PH", "PHBMMKAT"), ("LK", "BABORDHXXX"), ("HK", "HSBCHKHH")]


class SWIFTAttack:
    def __init__(self, weight: float = 0.15):
        self.weight = weight

    def generate(self) -> list[tuple[str, dict]]:
        scenario = random.choice([
            self._after_hours_transfers,
            self._sanctioned_transfer,
            self._rapid_burst,
            self._config_change,
        ])
        return scenario()

    def _after_hours_transfers(self) -> list[tuple[str, dict]]:
        """Multiple high-value SWIFT transfers at 2-3 AM — Bangladesh Bank heist pattern."""
        now = datetime.now(BST)
        logs = []
        user = random.choice(["swift_op_01", "swift_op_02"])

        for _ in range(random.randint(3, 8)):
            amount = random.randint(5000000, 50000000)  # $5M-$50M
            bic, country = random.choice(HIGH_RISK_COUNTRIES)
            log_line = (
                f"BANKSTACK_SWIFT: SWIFT_MSG_SENT msg_type=MT103 "
                f"sender=EXBKBDDH receiver={bic} "
                f"amount_usd={amount} dest_country={country} user={user}"
            )
            event = {
                "timestamp": now.isoformat(),
                "source": "swift",
                "action": "SWIFT_MSG_SENT",
                "msg_type": "MT103",
                "amount_usd": amount,
                "dest_country": country,
                "user": user,
                "attack_type": "swift_heist",
            }
            logs.append((log_line, event))

        return logs

    def _sanctioned_transfer(self) -> list[tuple[str, dict]]:
        """Transfer to sanctioned country."""
        now = datetime.now(BST)
        bic, country = random.choice(SANCTIONED_COUNTRIES)
        amount = random.randint(100000, 5000000)

        log_line = (
            f"BANKSTACK_SWIFT: SWIFT_MSG_SENT msg_type=MT103 "
            f"sender=EXBKBDDH receiver={bic} "
            f"amount_usd={amount} dest_country={country} user=swift_op_01"
        )
        event = {
            "timestamp": now.isoformat(),
            "source": "swift",
            "action": "SWIFT_MSG_SENT",
            "dest_country": country,
            "amount_usd": amount,
            "attack_type": "sanctions_violation",
        }
        return [(log_line, event)]

    def _rapid_burst(self) -> list[tuple[str, dict]]:
        """Rapid automated SWIFT messages — malware pattern."""
        now = datetime.now(BST)
        logs = []
        for _ in range(random.randint(6, 12)):
            amount = random.randint(1000000, 20000000)
            log_line = (
                f"BANKSTACK_SWIFT: SWIFT_MSG_SENT msg_type=MT103 "
                f"sender=EXBKBDDH receiver=CHASUS33 "
                f"amount_usd={amount} dest_country=US user=swift_admin"
            )
            event = {
                "timestamp": now.isoformat(),
                "source": "swift",
                "action": "SWIFT_MSG_SENT",
                "amount_usd": amount,
                "attack_type": "swift_rapid_burst",
            }
            logs.append((log_line, event))
        return logs

    def _config_change(self) -> list[tuple[str, dict]]:
        """Unauthorized SWIFT configuration modification."""
        now = datetime.now(BST)
        log_line = (
            f"BANKSTACK_SWIFT: SWIFT_CONFIG_CHANGE msg_type=CONFIG "
            f"sender=EXBKBDDH receiver=SYSTEM "
            f"amount_usd=0 dest_country=BD user=swift_admin"
        )
        event = {
            "timestamp": now.isoformat(),
            "source": "swift",
            "action": "SWIFT_CONFIG_CHANGE",
            "attack_type": "swift_config_tampering",
        }
        return [(log_line, event)]
