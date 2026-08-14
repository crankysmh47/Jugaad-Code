# scripts/mirror_switch.py
import subprocess
import sys
import json
import os

def switch_mirror(package_manager, mirror_url):
    try:
        use_shell = os.name == 'nt'
        if package_manager == "npm":
            result = subprocess.run(
                ["npm", "config", "set", "registry", mirror_url],
                capture_output=True, text=True, shell=use_shell
            )
            return {"switched": True, "pm": "npm", "mirror": mirror_url}
        
        elif package_manager == "pip":
            result = subprocess.run(
                [sys.executable, "-m", "pip", "config", "set", "global.index-url", mirror_url],
                capture_output=True, text=True, shell=use_shell
            )
            return {"switched": True, "pm": "pip", "mirror": mirror_url}
        else:
            return {"switched": False, "error": f"Unknown package manager: {package_manager}"}
    
    except Exception as e:
        return {"switched": False, "error": str(e)}

def reset_mirror(package_manager):
    defaults = {
        "npm": "https://registry.npmjs.org/",
        "pip": "https://pypi.org/simple/"
    }
    return switch_mirror(package_manager, defaults.get(package_manager, ""))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: mirror_switch.py <npm|pip|reset> [mirror_url]"}))
        sys.exit(1)
    
    pm = sys.argv[1]
    if pm == "reset":
        target_pm = sys.argv[2] if len(sys.argv) > 2 else "all"
        if target_pm == "all":
            npm_res = reset_mirror("npm")
            pip_res = reset_mirror("pip")
            print(json.dumps({"npm": npm_res, "pip": pip_res}, indent=2))
        else:
            print(json.dumps(reset_mirror(target_pm), indent=2))
    elif len(sys.argv) >= 3:
        url = sys.argv[2]
        print(json.dumps(switch_mirror(pm, url), indent=2))
    else:
        print(json.dumps({"error": "Usage: mirror_switch.py <npm|pip> <mirror_url>"}))
        sys.exit(1)
