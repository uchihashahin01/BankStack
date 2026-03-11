"""RTGS (Real-Time Gross Settlement) log generator."""

import random
from datetime import datetime, timezone, timedelta

BST = timezone(timedelta(hours=6))

BD_BANKS = [
    ("010", "Sonali Bank"), ("015", "Janata Bank"), ("020", "Agrani Bank"),
    ("085", "City Bank"), ("095", "Eastern Bank"), ("100", "BRAC Bank"),
    ("105", "DBBL"), ("115", "Prime Bank"), ("185", "StanChart"),
]

RTGS_USERS = ["rtgs_op_01", "rtgs_op_02", "rtgs_sup_01", "treasury_mgr"]


class RTGSLogGenerator:
    def __init__(self, weight: float = 0.05):
        self.weight = weight

    def generate(self) -> tuple[str, dict]:
        now = datetime.now(BST)
        src_code, src_name = random.choice(BD_BANKS)
        dst_code, dst_name = random.choice(BD_BANKS)
        while dst_code == src_code:
            dst_code, dst_name = random.choice(BD_BANKS)

        user = random.choice(RTGS_USERS)
        # RTGS is typically high-value (>1 Lakh BDT)
        amount = random.choices(
            [random.randint(100000, 1000000),
             random.randint(1000000, 50000000),
             random.randint(50000000, 500000000),
             random.randint(500000000, 5000000000)],
            weights=[30, 40, 20, 10],
            k=1
        )[0]

        log_line = (
            f"BANKSTACK_RTGS: RTGS_TRANSFER source_bank={src_code} "
            f"dest_bank={dst_code} amount_bdt={amount} user={user}"
        )
        event = {
            "timestamp": now.isoformat(),
            "source": "rtgs",
            "action": "RTGS_TRANSFER",
            "source_bank": src_code,
            "source_bank_name": src_name,
            "dest_bank": dst_code,
            "dest_bank_name": dst_name,
            "amount_bdt": amount,
            "user": user,
        }
        return log_line, event
