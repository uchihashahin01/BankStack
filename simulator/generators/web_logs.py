"""Web application log generator for internet banking."""

import random
from datetime import datetime, timezone, timedelta

BST = timezone(timedelta(hours=6))

ENDPOINTS = [
    "/api/v1/transfer", "/api/v1/payment", "/api/v1/balance",
    "/api/v1/swift/initiate", "/api/v1/beneficiary", "/api/v1/statement",
    "/login", "/dashboard", "/api/v1/accounts", "/api/v1/profile",
]

METHODS = ["GET", "POST", "PUT", "DELETE"]

NORMAL_ACTIONS = ["HTTP_REQUEST", "HTTP_REQUEST", "HTTP_REQUEST", "API_CALL"]
ATTACK_ACTIONS = [
    "SQL_INJECTION", "XSS_ATTEMPT", "WEBSHELL_DETECTED", "API_ABUSE",
]

URLS = [
    "ibank.example-bd.com", "corporate.example-bd.com",
    "api.example-bd.com", "portal.example-bd.com",
]


def _random_ip():
    return f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"


class WebLogGenerator:
    def __init__(self, weight: float = 0.04):
        self.weight = weight

    def generate(self) -> tuple[str, dict]:
        now = datetime.now(BST)
        src = _random_ip()
        url = random.choice(URLS)
        endpoint = random.choice(ENDPOINTS)
        method = random.choice(METHODS)

        action = random.choices(
            NORMAL_ACTIONS + ATTACK_ACTIONS,
            weights=[60, 15, 10, 5, 2, 2, 3, 3],
            k=1,
        )[0]

        log_line = (
            f"BANKSTACK_WEB: {action} src={src} url={url} "
            f"endpoint={endpoint} method={method}"
        )
        event = {
            "timestamp": now.isoformat(),
            "source": "web",
            "action": action,
            "srcip": src,
            "url": url,
            "endpoint": endpoint,
            "method": method,
        }
        return log_line, event
