"""BEFTN (Bangladesh Electronic Fund Transfer Network) log generator."""

import random
from datetime import datetime, timezone, timedelta

BST = timezone(timedelta(hours=6))

BD_BANKS = [
    ("010", "Sonali Bank"), ("015", "Janata Bank"), ("020", "Agrani Bank"),
    ("055", "AB Bank"), ("065", "Islami Bank"), ("070", "Pubali Bank"),
    ("085", "City Bank"), ("095", "Eastern Bank"), ("100", "BRAC Bank"),
    ("105", "DBBL"), ("115", "Prime Bank"), ("135", "Bank Asia"),
    ("185", "Standard Chartered"), ("190", "HSBC"),
]


class BEFTNLogGenerator:
    def __init__(self, weight: float = 0.05):
        self.weight = weight

    def generate(self) -> tuple[str, dict]:
        now = datetime.now(BST)
        src_bank_code, src_bank = random.choice(BD_BANKS)
        dst_bank_code, dst_bank = random.choice(BD_BANKS)
        while dst_bank_code == src_bank_code:
            dst_bank_code, dst_bank = random.choice(BD_BANKS)

        src_account = f"{src_bank_code}{random.randint(1000000, 9999999)}"
        amount = random.choices(
            [random.randint(1000, 50000),
             random.randint(50000, 500000),
             random.randint(500000, 5000000),
             random.randint(5000000, 50000000)],
            weights=[40, 35, 20, 5],
            k=1
        )[0]

        log_line = (
            f"BANKSTACK_BEFTN: BEFTN_TRANSFER source_bank={src_bank_code} "
            f"dest_bank={dst_bank_code} source_account={src_account} "
            f"amount_bdt={amount}"
        )
        event = {
            "timestamp": now.isoformat(),
            "source": "beftn",
            "action": "BEFTN_TRANSFER",
            "source_bank": src_bank_code,
            "source_bank_name": src_bank,
            "dest_bank": dst_bank_code,
            "dest_bank_name": dst_bank,
            "source_account": src_account,
            "amount_bdt": amount,
        }
        return log_line, event
