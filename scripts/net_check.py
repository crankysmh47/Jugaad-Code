# scripts/net_check.py
import json
import random
import socket
import struct
import sys
import time
import urllib.error
import urllib.request

ENDPOINTS = {
    "github.com": {
        "url": "https://github.com",
        "cable": "SMW4/AAE-1",
        "critical": True
    },
    "registry.npmjs.org": {
        "url": "https://registry.npmjs.org/",
        "cable": "SMW4",
        "critical": True
    },
    "pypi.org": {
        "url": "https://pypi.org/simple/",
        "cable": "SMW4",
        "critical": False
    },
    "api.anthropic.com": {
        "url": "https://api.anthropic.com",
        "cable": "SMW4/AAE-1",
        "critical": True
    },
    "1.1.1.1": {
        "kind": "dns_resolver",
        "cable": "LOCAL",
        "critical": True
    },
    "8.8.8.8": {
        "kind": "dns_resolver",
        "cable": "LOCAL",
        "critical": False
    }
}

PK_MIRRORS = {
    "npm": "https://registry.npmmirror.com/",
    "pip": "https://pypi.tuna.tsinghua.edu.cn/simple/"
}

def dns_resolve(host, timeout=3):
    try:
        start = time.time()
        socket.setdefaulttimeout(timeout)
        socket.gethostbyname(host)
        return round((time.time() - start) * 1000, 1)
    except:
        return None

def dns_query_ms(resolver, query_host="github.com", timeout=3):
    """Send a real DNS A query to a resolver over UDP 53 and time it."""
    try:
        txid = random.randint(0, 65535)
        header = struct.pack(">HHHHHH", txid, 0x0100, 1, 0, 0, 0)
        qname = b"".join(
            bytes([len(label)]) + label.encode() for label in query_host.split(".")
        ) + b"\x00"
        question = qname + struct.pack(">HH", 1, 1)
        packet = header + question

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(timeout)
        start = time.time()
        sock.sendto(packet, (resolver, 53))
        sock.recvfrom(512)
        sock.close()
        return round((time.time() - start) * 1000, 1)
    except:
        return None

def tcp_connect(host, port=443, timeout=3):
    try:
        start = time.time()
        sock = socket.create_connection((host, port), timeout=timeout)
        sock.close()
        return round((time.time() - start) * 1000, 1)
    except:
        return None

def ttfb(url, timeout=5):
    start = time.time()
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; jugaad-code/1.0)"}
        )
        resp = urllib.request.urlopen(req, timeout=timeout)
        resp.read(1)
        return round((time.time() - start) * 1000, 1)
    except urllib.error.HTTPError:
        # Server reached and responded with HTTP status (e.g. 403/404)
        return round((time.time() - start) * 1000, 1)
    except Exception:
        return None

def diagnose():
    results = {}
    failed_international = 0
    failed_local = 0
    total_international = 0

    for host, meta in ENDPOINTS.items():
        # DNS resolvers get a real UDP 53 query, not a TCP 443 probe
        if meta.get("kind") == "dns_resolver":
            dns_ms = dns_query_ms(host)
            results[host] = {
                "dns_ms": dns_ms,
                "tcp_ms": None,
                "ttfb_ms": None,
                "status": "ok" if dns_ms is not None else "dns_fail",
                "cable": meta["cable"],
                "critical": meta["critical"]
            }
            if dns_ms is None:
                failed_local += 1
            continue

        total_international += 1

        dns_ms = dns_resolve(host)
        tcp_ms = tcp_connect(host) if dns_ms else None
        ttfb_ms = ttfb(meta["url"]) if tcp_ms else None

        status = "ok"
        if dns_ms is None:
            status = "dns_fail"
            failed_international += 1
        elif tcp_ms is None:
            status = "tcp_fail"
            failed_international += 1
        elif ttfb_ms is None or ttfb_ms > 3000:
            status = "slow"
            failed_international += 1

        results[host] = {
            "dns_ms": dns_ms,
            "tcp_ms": tcp_ms,
            "ttfb_ms": ttfb_ms,
            "status": status,
            "cable": meta["cable"],
            "critical": meta["critical"]
        }

    # Classify root cause
    if failed_local > 0:
        diagnosis = "LOCAL_NETWORK"
        recommendation = "Check your WiFi/router. Problem is before your ISP."
    elif failed_international == total_international and total_international > 0:
        diagnosis = "SUBMARINE_CABLE"
        recommendation = "Likely SMW4/AAE-1 congestion. Affects all Pakistani ISPs. Use Asian mirrors."
    elif failed_international > 0:
        diagnosis = "ISP_ROUTING"
        recommendation = "Partial international routing issue. Your ISP may have asymmetric congestion."
    else:
        diagnosis = "ALL_OK"
        recommendation = "Network looks healthy. If installs fail, check your code."

    return {
        "endpoints": results,
        "diagnosis": diagnosis,
        "recommendation": recommendation,
        "mirrors": PK_MIRRORS
    }

if __name__ == "__main__":
    print(json.dumps(diagnose(), indent=2))
