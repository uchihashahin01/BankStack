"""Data exfiltration attack simulation."""

import random
from datetime import datetime, timezone, timedelta

BST = timezone(timedelta(hours=6))


class DataExfiltrationAttack:
    def __init__(self, weight: float = 0.10):
        self.weight = weight

    def generate(self) -> list[tuple[str, dict]]:
        scenario = random.choice([
            self._large_upload,
            self._bulk_db_query,
            self._dns_tunnel,
            self._usb_mount,
        ])
        return scenario()

    def _large_upload(self) -> list[tuple[str, dict]]:
        now = datetime.now(BST)
        src = f"10.{random.choice([10, 20, 30])}.{random.randint(1, 254)}.{random.randint(1, 254)}"
        dst = f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
        bytes_val = random.randint(1073741824, 10737418240)  # 1-10 GB
        zone = random.choice(["swift", "cbs", "internal"])

        log_line = (
            f"BANKSTACK_FW: LARGE_UPLOAD src={src} dst={dst} "
            f"port=443 target_zone={zone} bytes={bytes_val}"
        )
        event = {
            "timestamp": now.isoformat(),
            "source": "firewall",
            "action": "LARGE_UPLOAD",
            "srcip": src,
            "dstip": dst,
            "bytes": bytes_val,
            "target_zone": zone,
            "attack_type": "data_exfiltration",
        }
        return [(log_line, event)]

    def _bulk_db_query(self) -> list[tuple[str, dict]]:
        now = datetime.now(BST)
        user = random.choice(["dba_hasan", "officer_001", "it_support_01"])
        records = random.randint(10000, 500000)

        log_line = (
            f"BANKSTACK_CBS: BULK_QUERY txn_type=select "
            f"account=ALL amount_bdt=0 user={user} branch=0101"
        )
        event = {
            "timestamp": now.isoformat(),
            "source": "cbs",
            "action": "BULK_QUERY",
            "user": user,
            "records": records,
            "attack_type": "data_exfiltration",
        }
        return [(log_line, event)]

    def _dns_tunnel(self) -> list[tuple[str, dict]]:
        now = datetime.now(BST)
        src = f"10.10.{random.randint(1, 254)}.{random.randint(1, 254)}"

        log_line = (
            f"BANKSTACK_FW: DNS_TUNNEL src={src} dst=8.8.8.8 "
            f"port=53 target_zone=internal bytes={random.randint(1000000, 50000000)}"
        )
        event = {
            "timestamp": now.isoformat(),
            "source": "firewall",
            "action": "DNS_TUNNEL",
            "srcip": src,
            "attack_type": "dns_exfiltration",
        }
        return [(log_line, event)]

    def _usb_mount(self) -> list[tuple[str, dict]]:
        now = datetime.now(BST)
        system = random.choice(["swift", "cbs", "rtgs"])

        log_line = (
            f"BANKSTACK_FW: USB_MOUNT src=localhost dst=localhost "
            f"port=0 target_zone={system} bytes=0"
        )
        event = {
            "timestamp": now.isoformat(),
            "source": "endpoint",
            "action": "USB_MOUNT",
            "system": system,
            "attack_type": "removable_media",
        }
        return [(log_line, event)]
