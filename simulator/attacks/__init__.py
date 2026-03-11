from .brute_force import BruteForceAttack
from .transaction_fraud import TransactionFraudAttack
from .privilege_escalation import PrivilegeEscalationAttack
from .swift_attack import SWIFTAttack
from .data_exfiltration import DataExfiltrationAttack

__all__ = [
    "BruteForceAttack",
    "TransactionFraudAttack",
    "PrivilegeEscalationAttack",
    "SWIFTAttack",
    "DataExfiltrationAttack",
]
