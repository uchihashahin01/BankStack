"""Firewall / Network log generator."""

import random
from datetime import datetime, timezone, timedelta

BST = timezone(timedelta(hours=6))

ZONES = ["swift", "cbs", "dmz", "internal", "management", "atm_network"]
ACTIONS_FW = ["ALLOW", "DENY", "DENY", "DROP"]
PROTOCOLS = ["TCP", "UDP", "ICMP"]


def _random_ip():
    return f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"


def _internal_ip():
    subnet = random.choice(["10.10", "10.20", "10.30", "172.16", "192.168.1"])
    return f"{subnet}.{random.randint(1, 254)}"


class FirewallLogGenerator:
    def __init__(self, weight: float = 0.10):
        self.weight = weight

    def generate(self) -> tuple[str, dict]:
        now = datetime.now(BST)
        action = random.choice(ACTIONS_FW)
        src = random.choice([_random_ip(), _internal_ip()])
        dst = _internal_ip()
        port = random.choice([22, 80, 443, 1433, 1521, 3306, 3389, 8080, 8443, 48002])
        zone = random.choice(ZONES)
        bytes_transferred = random.randint(64, 1048576)

        log_line = (
            f"BANKSTACK_FW: {action} src={src} dst={dst} "
            f"port={port} target_zone={zone} bytes={bytes_transferred}"
        )
        event = {
            "timestamp": now.isoformat(),
            "source": "firewall",
            "action": action,
            "srcip": src,
            "dstip": dst,
            "dstport": port,
            "target_zone": zone,
            "bytes": bytes_transferred,
            "protocol": random.choice(PROTOCOLS),
        }
        return log_line, event
