"""Core Banking System log generator — Ababil, Flora, Stelar, TCS BaNCS."""

import random
from datetime import datetime, timezone, timedelta

BST = timezone(timedelta(hours=6))

BRANCHES = [
    ("0101", "Motijheel Main"), ("0102", "Gulshan Corporate"),
    ("0201", "Agrabad"), ("0301", "Rajshahi Main"),
    ("0401", "Khulna"), ("0501", "Sylhet"),
    ("0601", "Rangpur"), ("0701", "Barisal"),
    ("0103", "Dhanmondi"), ("0104", "Uttara"),
]

CBS_USERS = [
    "teller_001", "teller_002", "teller_003",
    "officer_001", "officer_002",
    "manager_001", "manager_002",
    "dba_admin", "cbs_batch",
]

TXN_TYPES = ["deposit", "withdrawal", "transfer", "loan_disbursement",
             "loan_repayment", "fd_creation", "fd_encashment", "utility_payment"]


class CBSLogGenerator:
    def __init__(self, weight: float = 0.30):
        self.weight = weight

    def generate(self) -> tuple[str, dict]:
        now = datetime.now(BST)
        action = random.choice([
            "CBS_TRANSACTION", "CBS_TRANSACTION", "CBS_TRANSACTION",
            "CBS_ACCOUNT_MODIFY", "CBS_GL_MODIFY",
        ])

        if action == "CBS_TRANSACTION":
            return self._transaction(now)
        elif action == "CBS_ACCOUNT_MODIFY":
            return self._account_modify(now)
        else:
            return self._gl_modify(now)

    def _transaction(self, now: datetime) -> tuple[str, dict]:
        user = random.choice(CBS_USERS)
        branch_code, branch_name = random.choice(BRANCHES)
        txn_type = random.choice(TXN_TYPES)
        # Realistic BDT amounts (most small, occasional large)
        amount = random.choices(
            [random.randint(500, 50000),
             random.randint(50000, 500000),
             random.randint(500000, 10000000),
             random.randint(10000000, 100000000)],
            weights=[60, 25, 10, 5],
            k=1
        )[0]
        account = f"1{branch_code}{random.randint(100000, 999999)}"

        log_line = (
            f"BANKSTACK_CBS: CBS_TRANSACTION txn_type={txn_type} "
            f"account={account} amount_bdt={amount} "
            f"user={user} branch={branch_code}"
        )
        event = {
            "timestamp": now.isoformat(),
            "source": "cbs",
            "action": "CBS_TRANSACTION",
            "txn_type": txn_type,
            "account": account,
            "amount_bdt": amount,
            "user": user,
            "branch": branch_code,
            "branch_name": branch_name,
        }
        return log_line, event

    def _account_modify(self, now: datetime) -> tuple[str, dict]:
        user = random.choice(CBS_USERS[:5])
        field = random.choice(["dormant_flag", "freeze_flag", "limit",
                               "address", "phone", "nominee"])
        account = f"1{random.choice(BRANCHES)[0]}{random.randint(100000, 999999)}"

        log_line = (
            f"BANKSTACK_CBS: CBS_ACCOUNT_MODIFY field_changed={field} "
            f"account={account} user={user} beneficiary_type=customer"
        )
        event = {
            "timestamp": now.isoformat(),
            "source": "cbs",
            "action": "CBS_ACCOUNT_MODIFY",
            "field_changed": field,
            "account": account,
            "user": user,
            "beneficiary_type": "customer",
        }
        return log_line, event

    def _gl_modify(self, now: datetime) -> tuple[str, dict]:
        user = random.choice(["officer_001", "manager_001", "dba_admin"])
        log_line = (
            f"BANKSTACK_CBS: CBS_GL_MODIFY field_changed=gl_entry "
            f"account=GL{random.randint(1000, 9999)} user={user} "
            f"beneficiary_type=internal"
        )
        event = {
            "timestamp": now.isoformat(),
            "source": "cbs",
            "action": "CBS_GL_MODIFY",
            "user": user,
        }
        return log_line, event
