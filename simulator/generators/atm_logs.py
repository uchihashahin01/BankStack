"""ATM / POS log generator."""

import random
from datetime import datetime, timezone, timedelta

BST = timezone(timedelta(hours=6))

ATM_LOCATIONS = [
    ("ATM-DHK-001", "Gulshan-1, Dhaka", "BD"),
    ("ATM-DHK-002", "Banani, Dhaka", "BD"),
    ("ATM-DHK-003", "Dhanmondi, Dhaka", "BD"),
    ("ATM-DHK-004", "Motijheel, Dhaka", "BD"),
    ("ATM-CTG-001", "Agrabad, Chittagong", "BD"),
    ("ATM-CTG-002", "GEC Circle, Chittagong", "BD"),
    ("ATM-RAJ-001", "Rajshahi City", "BD"),
    ("ATM-KHL-001", "Khulna City", "BD"),
    ("ATM-SYL-001", "Sylhet City", "BD"),
]


def _masked_card():
    return f"4{random.randint(100, 999)}XXXXXXXX{random.randint(1000, 9999)}"


class ATMLogGenerator:
    def __init__(self, weight: float = 0.10):
        self.weight = weight

    def generate(self) -> tuple[str, dict]:
        now = datetime.now(BST)
        atm_id, location, country = random.choice(ATM_LOCATIONS)
        card = _masked_card()
        amount = random.choices(
            [random.randint(500, 5000),
             random.randint(5000, 20000),
             random.randint(20000, 50000)],
            weights=[50, 35, 15],
            k=1
        )[0]
        # Round to nearest 500
        amount = (amount // 500) * 500

        log_line = (
            f"BANKSTACK_ATM: ATM_WITHDRAWAL card_number={card} "
            f"atm_id={atm_id} atm_location={country} amount_bdt={amount}"
        )
        event = {
            "timestamp": now.isoformat(),
            "source": "atm",
            "action": "ATM_WITHDRAWAL",
            "card_number": card,
            "atm_id": atm_id,
            "atm_location": country,
            "location_detail": location,
            "amount_bdt": amount,
        }
        return log_line, event
