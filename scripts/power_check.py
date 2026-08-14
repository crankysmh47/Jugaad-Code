# scripts/power_check.py
import json
import sys
import platform

def check_power():
    status = {
        "on_ac": True,
        "battery_percent": 100,
        "estimated_minutes": 999,
        "platform": platform.system()
    }

    try:
        if platform.system() == "Windows":
            import subprocess
            result = subprocess.run(
                ["powershell", "-Command",
                 "Get-CimInstance Win32_Battery | Select-Object EstimatedChargeRemaining, BatteryStatus, EstimatedRunTime | ConvertTo-Json"],
                capture_output=True, text=True, timeout=5
            )
            if result.stdout.strip():
                data = json.loads(result.stdout)
                # In Win32_Battery: BatteryStatus 2 = Connected to AC/Charging, 1 = Discharging (Battery)
                # Also handle list if multiple batteries returned
                if isinstance(data, list):
                    data = data[0] if data else {}
                status["on_ac"] = data.get("BatteryStatus") == 2 or data.get("BatteryStatus") == 3 or data.get("BatteryStatus") == 6
                status["battery_percent"] = data.get("EstimatedChargeRemaining", 100)
                status["estimated_minutes"] = data.get("EstimatedRunTime", 999)
            else:
                # No battery found (likely Desktop PC on direct AC power)
                status["on_ac"] = True
                status["battery_percent"] = 100
                status["estimated_minutes"] = 999
        else:
            try:
                import psutil
                battery = psutil.sensors_battery()
                if battery:
                    status["on_ac"] = battery.power_plugged if battery.power_plugged is not None else True
                    status["battery_percent"] = int(battery.percent)
                    status["estimated_minutes"] = int(battery.secsleft / 60) if battery.secsleft and battery.secsleft > 0 else 999
            except ImportError:
                pass

    except Exception as e:
        status["error"] = str(e)

    return status

if __name__ == "__main__":
    result = check_power()
    print(json.dumps(result, indent=2))
    
    # Exit code 1 if on battery — hooks can check this
    if not result["on_ac"]:
        sys.exit(1)
