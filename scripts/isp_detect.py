# scripts/isp_detect.py
import urllib.request
import json

# Known Pakistani ISP quirks — hardcoded research
ISP_QUIRKS = {
    "PTCL": {
        "aliases": ["ptcl", "pak telecom", "pakistan telecommunication", "broadband"],
        "known_issues": [
            "GitHub slow after 9pm PKT",
            "Docker Hub inconsistent",
            "Heavy SMW4 dependence"
        ],
        "recommended_npm": "https://registry.npmmirror.com/",
        "recommended_pip": "https://pypi.tuna.tsinghua.edu.cn/simple/",
        "recommended_dns": "8.8.8.8"
    },
    "StormFiber": {
        "aliases": ["stormfiber", "storm fiber", "cybernet", "cyber internet"],
        "known_issues": [
            "Claude API spikes 7-10pm PKT",
            "GitHub push slow evenings"
        ],
        "recommended_npm": "https://registry.npmmirror.com/",
        "recommended_pip": "https://mirrors.aliyun.com/pypi/simple/",
        "recommended_dns": "1.1.1.1"
    },
    "Nayatel": {
        "aliases": ["nayatel", "ntl"],
        "known_issues": [
            "Generally stable",
            "Occasional AAE-1 dependence"
        ],
        "recommended_npm": "https://registry.npmjs.org/",
        "recommended_pip": "https://pypi.org/simple/",
        "recommended_dns": "1.1.1.1"
    },
    "Jazz": {
        "aliases": ["jazz", "mobilink", "pmcl", "pakistan mobile"],
        "known_issues": [
            "Mobile data — bandwidth expensive",
            "Throttling after 1GB",
            "High latency to US endpoints"
        ],
        "recommended_npm": "https://registry.npmmirror.com/",
        "recommended_pip": "https://pypi.tuna.tsinghua.edu.cn/simple/",
        "recommended_dns": "8.8.8.8"
    },
    "Zong": {
        "aliases": ["zong", "cmpak", "china mobile"],
        "known_issues": [
            "Mobile hotspot — monitor data usage",
            "Inconsistent international routing"
        ],
        "recommended_npm": "https://registry.npmmirror.com/",
        "recommended_pip": "https://mirrors.aliyun.com/pypi/simple/",
        "recommended_dns": "1.1.1.1"
    },
    "Transworld": {
        "aliases": ["transworld", "tes", "tw1"],
        "known_issues": [
            "Good international routing via TW1",
            "Occasional peering drops with local IXPs"
        ],
        "recommended_npm": "https://registry.npmjs.org/",
        "recommended_pip": "https://pypi.org/simple/",
        "recommended_dns": "1.1.1.1"
    }
}

def detect_isp():
    endpoints = [
        ("https://ipapi.co/json/", lambda d: (d.get("org", ""), d.get("isp", ""), d.get("city", "Unknown"), d.get("country_name", "Unknown"), d.get("ip", "Unknown"))),
        ("https://ip-api.com/json/", lambda d: (d.get("org", ""), d.get("isp", ""), d.get("city", "Unknown"), d.get("country", "Unknown"), d.get("query", "Unknown"))),
        ("https://ipinfo.io/json", lambda d: (d.get("org", ""), d.get("org", ""), d.get("city", "Unknown"), d.get("country", "Unknown"), d.get("ip", "Unknown")))
    ]

    last_error = None
    for url, extractor in endpoints:
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (compatible; jugaad-code/1.0)"}
            )
            with urllib.request.urlopen(req, timeout=4) as response:
                data = json.loads(response.read().decode())
            
            org, isp_raw, city, country, ip = extractor(data)
            combined = f"{org} {isp_raw}".lower()
            isp_name = "Unknown"

            for name, meta in ISP_QUIRKS.items():
                aliases = meta.get("aliases", [name.lower()])
                if any(alias in combined for alias in aliases):
                    isp_name = name
                    break

            return {
                "isp": isp_name,
                "org": org or isp_raw or "Unknown",
                "city": city,
                "country": country,
                "ip": ip,
                "quirks": ISP_QUIRKS.get(isp_name, {})
            }
        except Exception as e:
            last_error = str(e)
            continue

    return {"isp": "Unknown", "error": last_error or "Detection failed"}

if __name__ == "__main__":
    print(json.dumps(detect_isp(), indent=2))
