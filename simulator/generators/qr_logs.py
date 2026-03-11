"""QR payment / Binimoy log generator."""

import random
from datetime import datetime, timezone, timedelta

BST = timezone(timedelta(hours=6))

MERCHANTS = [
    "MER-DHK-001", "MER-DHK-002", "MER-CTG-001", "MER-RAJ-001",
    "MER-KHL-001", "MER-SYL-001", "MER-DHK-003", "MER-BAR-001",
]

PAYERS = [
    "01711XXXXX1", "01811XXXXX2", "01911XXXXX3", "01611XXXXX4",
    "01511XXXXX5", "01711XXXXX6", "01311XXXXX7", "01411XXXXX8",
]

PROVIDERS = ["bKash", "Nagad", "Rocket", "Upay", "Binimoy"]

NORMAL_ACTIONS = ["QR_PAYMENT", "QR_PAYMENT", "QR_PAYMENT"]
ATTACK_ACTIONS = ["QR_TAMPERED"]


class QRLogGenerator:
    def __init__(self, weight: float = 0.03):
        self.weight = weight

    def generate(self) -> tuple[str, dict]:
        now = datetime.now(BST)
        merchant = random.choice(MERCHANTS)
        payer = random.choice(PAYERS)
        provider = random.choice(PROVIDERS)
        amount = random.choices(
            [random.randint(50, 5000),
             random.randint(5000, 50000),
             random.randint(50000, 500000)],
            weights=[65, 25, 10],
            k=1,
        )[0]

        action = random.choices(
            NORMAL_ACTIONS + ATTACK_ACTIONS,
            weights=[45, 30, 15, 10],
            k=1,
        )[0]

        log_line = (
            f"BANKSTACK_QR: {action} merchant_id={merchant} "
            f"payer={payer} amount_bdt={amount} provider={provider}"
        )
        event = {
            "timestamp": now.isoformat(),
            "source": "qr_payment",
            "action": action,
            "merchant_id": merchant,
            "payer": payer,
            "amount_bdt": amount,
            "provider": provider,
        }
        return log_line, event
