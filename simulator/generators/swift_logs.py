"""SWIFT messaging log generator."""

import random
from datetime import datetime, timezone, timedelta

BST = timezone(timedelta(hours=6))

SWIFT_USERS = ["swift_op_01", "swift_op_02", "swift_sup_01", "swift_admin"]
SENDER_BIC = "EXBKBDDH"  # Example BD bank BIC

RECEIVER_BICS = [
    ("CHASUS33", "US"), ("DEUTDEFF", "DE"), ("BKENGB2L", "GB"),
    ("ABORDHXXX", "BD"), ("SCBLBDDH", "BD"), ("HSBCBDDH", "BD"),
    ("CITIBDDH", "BD"), ("BOFAUS3N", "US"), ("ANZBAU3M", "AU"),
    ("SBININBB", "IN"), ("ICBKCNBJ", "CN"), ("BKKBTHBK", "TH"),
    ("DBSSSGSG", "SG"), ("MABORDHXXX", "BD"), ("CABORDHXXX", "BD"),
]

MSG_TYPES = ["MT103", "MT103", "MT103", "MT202", "MT202", "MT199",
             "MT900", "MT910", "MT940", "MT950"]


class SWIFTLogGenerator:
    def __init__(self, weight: float = 0.10):
        self.weight = weight

    def generate(self) -> tuple[str, dict]:
        now = datetime.now(BST)
        user = random.choice(SWIFT_USERS)
        receiver_bic, dest_country = random.choice(RECEIVER_BICS)
        msg_type = random.choice(MSG_TYPES)

        # Amount distribution (USD)
        amount = random.choices(
            [random.randint(1000, 50000),
             random.randint(50000, 500000),
             random.randint(500000, 5000000),
             random.randint(5000000, 50000000)],
            weights=[50, 30, 15, 5],
            k=1
        )[0]

        log_line = (
            f"BANKSTACK_SWIFT: SWIFT_MSG_SENT msg_type={msg_type} "
            f"sender={SENDER_BIC} receiver={receiver_bic} "
            f"amount_usd={amount} dest_country={dest_country} user={user}"
        )
        event = {
            "timestamp": now.isoformat(),
            "source": "swift",
            "action": "SWIFT_MSG_SENT",
            "msg_type": msg_type,
            "sender_bic": SENDER_BIC,
            "receiver_bic": receiver_bic,
            "amount_usd": amount,
            "dest_country": dest_country,
            "user": user,
        }
        return log_line, event
