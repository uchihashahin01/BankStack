"""NPSB (National Payment Switch Bangladesh) log generator."""

import random
from datetime import datetime, timezone, timedelta

BST = timezone(timedelta(hours=6))

BD_BANKS = [
    "010", "015", "020", "055", "065", "070",
    "085", "095", "100", "105", "115", "135",
]


def _masked_card():
    return f"4{random.randint(100, 999)}XXXXXXXX{random.randint(1000, 9999)}"


class NPSBLogGenerator:
    def __init__(self, weight: float = 0.03):
        self.weight = weight

    def generate(self) -> tuple[str, dict]:
        now = datetime.now(BST)
        card = _masked_card()
        src_bank = random.choice(BD_BANKS)
        dst_bank = random.choice(BD_BANKS)
        while dst_bank == src_bank:
            dst_bank = random.choice(BD_BANKS)
        amount = random.choices(
            [random.randint(100, 10000),
             random.randint(10000, 100000),
             random.randint(100000, 1000000)],
            weights=[60, 30, 10],
            k=1,
        )[0]

        log_line = (
            f"BANKSTACK_NPSB: NPSB_TRANSFER card_number={card} "
            f"source_bank={src_bank} dest_bank={dst_bank} amount_bdt={amount}"
        )
        event = {
            "timestamp": now.isoformat(),
            "source": "npsb",
            "action": "NPSB_TRANSFER",
            "card_number": card,
            "source_bank": src_bank,
            "dest_bank": dst_bank,
            "amount_bdt": amount,
        }
        return log_line, event
