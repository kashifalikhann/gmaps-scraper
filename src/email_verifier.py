import asyncio
import time
from src.utils import DISPOSABLE_DOMAINS

MX_CACHE: dict[str, tuple[bool, float]] = {}
MX_CACHE_TTL = 3600


def is_disposable_domain(domain: str) -> bool:
    d = domain.lower().lstrip('www.')
    return d in DISPOSABLE_DOMAINS


async def verify_email_deliverability(email: str) -> dict:
    parts = email.split('@')
    if len(parts) != 2:
        return {'deliverable': False, 'method': ''}
    domain = parts[1].lower().lstrip('www.')
    if not domain or '.' not in domain:
        return {'deliverable': False, 'method': ''}

    if is_disposable_domain(domain):
        return {'deliverable': False, 'method': 'disposable'}

    now = time.time()
    if domain in MX_CACHE and now - MX_CACHE[domain][1] < MX_CACHE_TTL:
        cached = MX_CACHE[domain][0]
        return {'deliverable': cached, 'method': 'mx' if cached else 'no-mx'}

    try:
        loop = asyncio.get_event_loop()
        _, _, ips = await loop.getaddrinfo(domain, None)
        import socket
        try:
            records = await loop.getaddrinfo(domain, 'smtp', type=socket.SOCK_STREAM)
        except Exception:
            records = []
        deliverable = len(records) > 0
        MX_CACHE[domain] = (deliverable, now)
        return {'deliverable': deliverable, 'method': 'mx' if deliverable else 'no-mx'}
    except Exception:
        MX_CACHE[domain] = (False, now)
        return {'deliverable': False, 'method': 'dns-error'}
