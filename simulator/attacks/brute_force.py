"""Brute force attack simulation — banking system login attacks."""

import random
from datetime import datetime, timezone, timedelta

BST = timezone(timedelta(hours=6))

TARGET_USERS = ["admin_rafiq", "swift_operator_01", "dba_hasan", "manager_001"]
TARGET_SYSTEMS = ["CBS", "SWIFT", "RTGS", "AD", "VPN"]


def _attack_ip():
    return f"{random.choice([45, 91, 103, 185, 194, 212])}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"


class BruteForceAttack:
    def __init__(self, weight: float = 0.20):
        self.weight = weight

    def generate(self) -> list[tuple[str, dict]]:
        """Generate a burst of failed login attempts followed by optional success."""
        now = datetime.now(BST)
        src_ip = _attack_ip()
        target_user = random.choice(TARGET_USERS)
        target_system = random.choice(TARGET_SYSTEMS)
        num_attempts = random.randint(5, 15)
        logs = []

        for i in range(num_attempts):
            log_line = (
                f"BANKSTACK_AUTH: LOGIN_FAILED user={target_user} src={src_ip} "
                f"system={target_system} user_type=standard source_country={random.choice(['RU', 'CN', 'KP', 'IR', 'UNKNOWN'])}"
            )
            event = {
                "timestamp": now.isoformat(),
                "source": "auth",
                "action": "LOGIN_FAILED",
                "user": target_user,
                "srcip": src_ip,
                "system": target_system,
                "source_country": "UNKNOWN",
                "attack_type": "brute_force",
            }
            logs.append((log_line, event))

        # 20% chance the brute force succeeds
        if random.random() < 0.20:
            log_line = (
                f"BANKSTACK_AUTH: LOGIN_SUCCESS user={target_user} src={src_ip} "
                f"system={target_system} user_type=standard source_country=UNKNOWN"
            )
            event = {
                "timestamp": now.isoformat(),
                "source": "auth",
                "action": "LOGIN_SUCCESS",
                "user": target_user,
                "srcip": src_ip,
                "system": target_system,
                "source_country": "UNKNOWN",
                "attack_type": "brute_force_success",
            }
            logs.append((log_line, event))

        return logs
