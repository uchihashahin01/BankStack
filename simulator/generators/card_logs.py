"""Card transaction / fraud log generator."""

import random
from datetime import datetime, timezone, timedelta

BST = timezone(timedelta(hours=6))

MERCHANTS = [
    "ShopUp-DHK", "Daraz-BD", "Pathao-DHK", "FoodPanda-BD",
    "AmazonUS", "AliExpress-CN", "BookingCom-NL", "SteamStore-US",
    "MerchanXY-IN", "UnknownPOS-RU",
]

COUNTRIES = ["BD", "BD", "BD", "BD", "BD", "US", "IN", "CN", "SG", "RU", "GB", "KP"]


def _masked_card():
    return f"4{random.randint(100, 999)}XXXXXXXX{random.randint(1000, 9999)}"


ACTIONS_NORMAL = ["CARD_TXN", "CARD_TXN", "CARD_TXN"]
ACTIONS_FRAUD = [
    "CARD_NOT_PRESENT_FRAUD",
    "CARD_COUNTRY_MISMATCH",
    "CARD_VELOCITY_BREACH",
]


class CardLogGenerator:
    def __init__(self, weight: float = 0.03):
        self.weight = weight

    def generate(self) -> tuple[str, dict]:
        now = datetime.now(BST)
        card = _masked_card()
        merchant = random.choice(MERCHANTS)
        country = random.choice(COUNTRIES)
        amount = random.choices(
            [random.randint(100, 5000),
             random.randint(5000, 50000),
             random.randint(50000, 500000)],
            weights=[60, 30, 10],
            k=1,
        )[0]

        action = random.choices(
            ACTIONS_NORMAL + ACTIONS_FRAUD,
            weights=[50, 25, 10, 5, 5, 5],
            k=1,
        )[0]

        log_line = (
            f"BANKSTACK_CARD: {action} card_number={card} "
            f"merchant={merchant} amount={amount} country={country}"
        )
        event = {
            "timestamp": now.isoformat(),
            "source": "card",
            "action": action,
            "card_number": card,
            "merchant": merchant,
            "amount": amount,
            "country": country,
        }
        return log_line, event
