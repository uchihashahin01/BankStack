"""Active Directory / Authentication log generator."""

import random
from datetime import datetime, timezone, timedelta

BST = timezone(timedelta(hours=6))

USERS = [
    ("admin_rafiq", "admin", "service_account"),
    ("teller_karim", "teller", "standard"),
    ("officer_rahim", "officer", "standard"),
    ("swift_operator_01", "swift_operator", "standard"),
    ("dba_hasan", "dba", "standard"),
    ("mgr_fatima", "manager", "standard"),
    ("it_support_01", "it_support", "standard"),
    ("audit_user", "auditor", "standard"),
    ("batch_scheduler", "batch", "service_account"),
    ("hr_nusrat", "hr", "standard"),
]

SYSTEMS = ["CBS", "SWIFT", "AD", "EMAIL", "VPN", "FIREWALL", "RTGS", "BEFTN", "IBANKING"]

COUNTRIES = [
    ("BD", 85), ("US", 3), ("IN", 3), ("SG", 2),
    ("GB", 2), ("DE", 1), ("CN", 1), ("RU", 1),
    ("KP", 0.5), ("IR", 0.5), ("UNKNOWN", 1),
]


def _random_ip():
    return f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"


class ADLogGenerator:
    def __init__(self, weight: float = 0.10):
        self.weight = weight

    def generate(self) -> tuple[str, dict]:
        now = datetime.now(BST)
        action = random.choices(
            ["LOGIN_SUCCESS", "LOGIN_FAILED", "PASSWORD_CHANGE", "SESSION_ACTIVITY"],
            weights=[60, 25, 5, 10],
            k=1
        )[0]

        username, role, user_type = random.choice(USERS)
        system = random.choice(SYSTEMS)
        src_ip = _random_ip()
        country = random.choices(
            [c[0] for c in COUNTRIES],
            weights=[c[1] for c in COUNTRIES],
            k=1
        )[0]

        log_line = (
            f"BANKSTACK_AUTH: {action} user={username} src={src_ip} "
            f"system={system} user_type={user_type} source_country={country}"
        )
        event = {
            "timestamp": now.isoformat(),
            "source": "auth",
            "action": action,
            "user": username,
            "user_role": role,
            "user_type": user_type,
            "srcip": src_ip,
            "system": system,
            "source_country": country,
        }
        return log_line, event
