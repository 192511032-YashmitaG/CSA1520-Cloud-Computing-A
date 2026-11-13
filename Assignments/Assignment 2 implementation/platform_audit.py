#!/usr/bin/env python3
from pathlib import Path
import json, platform, shutil, subprocess, os

ROOT = Path(__file__).resolve().parents[1]
out = ROOT / "results"
out.mkdir(exist_ok=True)
commands = ["docker","podman","virsh","qemu-system-x86_64","kata-runtime","containerd","kubectl"]
tools = {}
for name in commands:
    path = shutil.which(name)
    version = None
    if path:
        try:
            args = [name, "--version"]
            if name == "kubectl":
                args = [name, "version", "--client"]
            p = subprocess.run(args, capture_output=True, text=True, timeout=5)
            version = (p.stdout or p.stderr).strip().splitlines()[0:1]
            version = version[0] if version else "available; version not reported"
        except Exception as e:
            version = "available; version check failed: " + type(e).__name__
    tools[name] = {"available": bool(path), "path": path, "version": version}
kvm = Path("/dev/kvm")
report = {
    "platform": platform.platform(), "system": platform.system(),
    "machine": platform.machine(), "python": platform.python_version(),
    "devices": {
        "/dev/kvm": {"exists": kvm.exists(),
                     "readable": kvm.exists() and os.access(kvm, os.R_OK),
                     "writable": kvm.exists() and os.access(kvm, os.W_OK)},
        "docker_socket_exists": Path("/var/run/docker.sock").exists()
    },
    "tools": tools,
    "limitation": "Presence checks do not prove that a runtime is configured or functional."
}
(out / "platform_audit.json").write_text(json.dumps(report, indent=2) + "\n")
print("Platform audit completed (read-only).")
print("Platform:", report["platform"])
print("/dev/kvm exists:", report["devices"]["/dev/kvm"]["exists"])
for name, item in tools.items():
    print(name + ":", "available" if item["available"] else "not found")
print("Report saved to results/platform_audit.json")
