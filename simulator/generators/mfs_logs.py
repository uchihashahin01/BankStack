"""MFS (bKash/Nagad/Rocket) log generator."""

import random
from datetime import datetime, timezone, timedelta

BST = timezone(timedelta(hours=6))

MFS_PROVIDERS = ["BKASH", "NAGAD", "ROCKET", "UPAY"]
MFS_TXN_TYPES = ["send_money", "cashout", "cashin", "payment",
                  "mobile_recharge", "utility_bill"]

AGENT_IDS = [f"AGT-{d}-{random.randint(1000, 9999)}"
             for d in ["DHK", "CTG", "RAJ", "KHL", "SYL", "RNG", "BAR"]]


def _random_bd_phone():
    prefix = random.choice(["013", "014", "015", "016", "017", "018", "019"])
    return prefix + str(random.randint(10000000, 99999999))


class MFSLogGenerator:
    def __init__(self, weight: float = 0.20):
        self.weight = weight

    def generate(self) -> tuple[str, dict]:
        now = datetime.now(BST)
        action = random.choices(
            ["MFS_TRANSACTION", "MFS_TRANSACTION", "MFS_PIN_FAILED"],
            weights=[85, 10, 5],
            k=1
        )[0]

        provider = random.choice(MFS_PROVIDERS)
        phone = _random_bd_phone()

        if action == "MFS_PIN_FAILED":
            return self._pin_failed(now, provider, phone)
        return self._transaction(now, provider, phone)

    def _transaction(self, now: datetime, provider: str, phone: str) -> tuple[str, dict]:
        txn_type = random.choice(MFS_TXN_TYPES)
        agent_id = random.choice(AGENT_IDS)

        # BDT amounts for MFS (mostly small)
        amount = random.choices(
            [random.randint(50, 1000),
             random.randint(1000, 10000),
             random.randint(10000, 50000),
             random.randint(50000, 200000)],
            weights=[40, 35, 20, 5],
            k=1
        )[0]

        log_line = (
            f"BANKSTACK_MFS: MFS_TRANSACTION provider={provider} "
            f"phone={phone} txn_type={txn_type} "
            f"amount_bdt={amount} agent_id={agent_id}"
        )
        event = {
            "timestamp": now.isoformat(),
            "source": "mfs",
            "action": "MFS_TRANSACTION",
            "provider": provider,
            "phone_number": phone,
            "txn_type": txn_type,
            "amount_bdt": amount,
            "agent_id": agent_id,
        }
        return log_line, event

    def _pin_failed(self, now: datetime, provider: str, phone: str) -> tuple[str, dict]:
        log_line = (
            f"BANKSTACK_MFS: MFS_PIN_FAILED provider={provider} "
            f"phone={phone} txn_type=auth amount_bdt=0 agent_id=NONE"
        )
        event = {
            "timestamp": now.isoformat(),
            "source": "mfs",
            "action": "MFS_PIN_FAILED",
            "provider": provider,
            "phone_number": phone,
        }
        return log_line, event
