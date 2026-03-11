"""Transaction fraud simulation — CBS, MFS, BEFTN fraud patterns."""

import random
from datetime import datetime, timezone, timedelta

BST = timezone(timedelta(hours=6))


class TransactionFraudAttack:
    def __init__(self, weight: float = 0.25):
        self.weight = weight

    def generate(self) -> list[tuple[str, dict]]:
        scenario = random.choice([
            self._cbs_after_hours_transfer,
            self._mfs_rapid_cashout,
            self._beftn_smurfing,
            self._cbs_backdated_txn,
            self._mfs_sim_swap_cashout,
        ])
        return scenario()

    def _cbs_after_hours_transfer(self) -> list[tuple[str, dict]]:
        """Large CBS transfer at 2 AM."""
        now = datetime.now(BST)
        amount = random.randint(10000000, 100000000)
        user = random.choice(["teller_002", "officer_001", "dba_hasan"])
        logs = []

        log_line = (
            f"BANKSTACK_CBS: CBS_TRANSACTION txn_type=transfer "
            f"account=1{random.randint(100, 999)}{random.randint(100000, 999999)} "
            f"amount_bdt={amount} user={user} branch=0101"
        )
        event = {
            "timestamp": now.isoformat(),
            "source": "cbs",
            "action": "CBS_TRANSACTION",
            "txn_type": "transfer",
            "amount_bdt": amount,
            "user": user,
            "branch": "0101",
            "attack_type": "after_hours_transfer",
        }
        logs.append((log_line, event))
        return logs

    def _mfs_rapid_cashout(self) -> list[tuple[str, dict]]:
        """Multiple rapid cashouts from same phone — account takeover."""
        now = datetime.now(BST)
        phone = f"017{random.randint(10000000, 99999999)}"
        provider = random.choice(["BKASH", "NAGAD"])
        logs = []

        for _ in range(random.randint(8, 15)):
            amount = random.randint(20000, 50000)
            agent_id = f"AGT-DHK-{random.randint(1000, 9999)}"
            log_line = (
                f"BANKSTACK_MFS: MFS_TRANSACTION provider={provider} "
                f"phone={phone} txn_type=cashout "
                f"amount_bdt={amount} agent_id={agent_id}"
            )
            event = {
                "timestamp": now.isoformat(),
                "source": "mfs",
                "action": "MFS_TRANSACTION",
                "provider": provider,
                "phone_number": phone,
                "txn_type": "cashout",
                "amount_bdt": amount,
                "attack_type": "rapid_cashout",
            }
            logs.append((log_line, event))

        return logs

    def _beftn_smurfing(self) -> list[tuple[str, dict]]:
        """Many BEFTN transfers just under reporting threshold."""
        now = datetime.now(BST)
        src_account = f"010{random.randint(1000000, 9999999)}"
        logs = []

        for _ in range(random.randint(20, 30)):
            amount = random.randint(80000, 99999)  # Just under 1 Lakh
            dst_bank = random.choice(["015", "020", "055", "070", "085", "100"])
            log_line = (
                f"BANKSTACK_BEFTN: BEFTN_TRANSFER source_bank=010 "
                f"dest_bank={dst_bank} source_account={src_account} "
                f"amount_bdt={amount}"
            )
            event = {
                "timestamp": now.isoformat(),
                "source": "beftn",
                "action": "BEFTN_TRANSFER",
                "source_account": src_account,
                "amount_bdt": amount,
                "attack_type": "smurfing",
            }
            logs.append((log_line, event))

        return logs

    def _cbs_backdated_txn(self) -> list[tuple[str, dict]]:
        """Backdated transaction in CBS."""
        now = datetime.now(BST)
        user = random.choice(["officer_001", "manager_001"])
        log_line = (
            f"BANKSTACK_CBS: CBS_BACKDATED_TXN txn_type=transfer "
            f"account=1{random.randint(100, 999)}{random.randint(100000, 999999)} "
            f"amount_bdt={random.randint(100000, 5000000)} user={user} branch=0101"
        )
        event = {
            "timestamp": now.isoformat(),
            "source": "cbs",
            "action": "CBS_BACKDATED_TXN",
            "user": user,
            "attack_type": "backdated_transaction",
        }
        return [(log_line, event)]

    def _mfs_sim_swap_cashout(self) -> list[tuple[str, dict]]:
        """SIM swap followed by immediate cashout."""
        now = datetime.now(BST)
        phone = f"018{random.randint(10000000, 99999999)}"
        provider = random.choice(["BKASH", "NAGAD"])
        logs = []

        # SIM swap event
        log_line = (
            f"BANKSTACK_MFS: MFS_SIM_SWAP provider={provider} "
            f"phone={phone} txn_type=sim_swap amount_bdt=0 agent_id=SYSTEM"
        )
        event = {
            "timestamp": now.isoformat(),
            "source": "mfs",
            "action": "MFS_SIM_SWAP",
            "provider": provider,
            "phone_number": phone,
            "attack_type": "sim_swap",
        }
        logs.append((log_line, event))

        # Followed by cashout
        for _ in range(3):
            amount = random.randint(25000, 50000)
            log_line = (
                f"BANKSTACK_MFS: MFS_TRANSACTION provider={provider} "
                f"phone={phone} txn_type=cashout "
                f"amount_bdt={amount} agent_id=AGT-DHK-{random.randint(1000, 9999)}"
            )
            event = {
                "timestamp": now.isoformat(),
                "source": "mfs",
                "action": "MFS_TRANSACTION",
                "provider": provider,
                "phone_number": phone,
                "txn_type": "cashout",
                "amount_bdt": amount,
                "attack_type": "post_sim_swap_cashout",
            }
            logs.append((log_line, event))

        return logs
