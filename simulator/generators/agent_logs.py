"""Agent banking log generator."""

import random
from datetime import datetime, timezone, timedelta

BST = timezone(timedelta(hours=6))

AGENT_IDS = [
    "AGT-DHK-001", "AGT-DHK-002", "AGT-CTG-001", "AGT-RAJ-001",
    "AGT-KHL-001", "AGT-SYL-001", "AGT-BAR-001", "AGT-RNG-001",
    "AGT-MYM-001", "AGT-COM-001",
]

CUSTOMERS = [
    "CUST001", "CUST002", "CUST003", "CUST004", "CUST005",
    "CUST006", "CUST007", "CUST008", "CUST009", "CUST010",
]

TXN_TYPES = ["deposit", "withdrawal", "transfer", "balance_inquiry", "bill_payment"]


class AgentLogGenerator:
    def __init__(self, weight: float = 0.03):
        self.weight = weight

    def generate(self) -> tuple[str, dict]:
        now = datetime.now(BST)
        agent_id = random.choice(AGENT_IDS)
        customer = random.choice(CUSTOMERS)
        txn_type = random.choice(TXN_TYPES)
        amount = random.choices(
            [random.randint(500, 10000),
             random.randint(10000, 50000),
             random.randint(50000, 500000),
             random.randint(500000, 2000000)],
            weights=[40, 35, 20, 5],
            k=1,
        )[0]

        log_line = (
            f"BANKSTACK_AGENT: AGENT_TXN agent_id={agent_id} "
            f"customer={customer} txn_type={txn_type} amount_bdt={amount}"
        )
        event = {
            "timestamp": now.isoformat(),
            "source": "agent_banking",
            "action": "AGENT_TXN",
            "agent_id": agent_id,
            "customer": customer,
            "txn_type": txn_type,
            "amount_bdt": amount,
        }
        return log_line, event
