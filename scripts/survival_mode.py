# scripts/survival_mode.py
import json
import os
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

STATE_NORMAL = "NORMAL"
STATE_NETWORK = "NETWORK_DEGRADED"
STATE_POWER = "POWER_UNSTABLE"
STATE_CRITICAL = "CRITICAL"


def run_json(script_name):
    try:
        result = subprocess.run(
            [sys.executable, os.path.join(SCRIPT_DIR, script_name)],
            capture_output=True, text=True, timeout=30
        )
        if result.stdout.strip():
            return json.loads(result.stdout)
        return {"error": result.stderr or "Empty output"}
    except Exception as e:
        return {"error": str(e)}


def determine_state(power, network):
    on_ac = power.get("on_ac", True)
    battery = power.get("battery_percent", 100)
    diagnosis = network.get("diagnosis", "ALL_OK")

    network_bad = diagnosis in [
        "SUBMARINE_CABLE",
        "ISP_ROUTING",
        "LOCAL_NETWORK",
        "INTERNATIONAL_CONNECTIVITY_DEGRADED"
    ]

    if not on_ac and battery <= 15 and network_bad:
        return STATE_CRITICAL

    if not on_ac:
        return STATE_POWER

    if network_bad:
        return STATE_NETWORK

    return STATE_NORMAL


def actions_for(state):
    return {
        STATE_NORMAL: [
            "normal_operation"
        ],
        STATE_NETWORK: [
            "prefer_cache",
            "avoid_large_downloads",
            "retry_transient_network_commands",
            "prefer_asian_mirrors",
            "warn_before_expensive_network_operations"
        ],
        STATE_POWER: [
            "protect_workspace",
            "warn_before_long_operations",
            "encourage_checkpoint"
        ],
        STATE_CRITICAL: [
            "protect_workspace",
            "avoid_long_operations",
            "finish_current_edit",
            "checkpoint_now",
            "push_when_network_recovers"
        ]
    }.get(state, ["normal_operation"])


def evaluate():
    power = run_json("power_check.py")
    network = run_json("net_check.py")
    state = determine_state(power, network)

    return {
        "state": state,
        "power": power,
        "network": network,
        "actions": actions_for(state)
    }


def print_human(result):
    state = result["state"]
    print(f"jugaadi-claude state: {state}")
    print("Active protections:")
    for action in result["actions"]:
        print(f"  - {action}")


if __name__ == "__main__":
    result = evaluate()
    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        print(json.dumps(result, indent=2))
    else:
        print_human(result)
