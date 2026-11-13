#!/usr/bin/env python3
from pathlib import Path
import csv, json

ROOT = Path(__file__).resolve().parents[1]
cfg = json.loads((ROOT / "config/model_config.json").read_text())
out = ROOT / "results"
out.mkdir(exist_ok=True)
h, w = cfg["host"], cfg["workload"]
usable_ram = h["ram_gb"] - h["host_reserved_ram_gb"]
network = h["nic_count"] * h["nic_speed_gbps_each"]
planned_network = network * h["network_planning_utilization"]
rows = []
for ratio in cfg["memory_overcommit_ratios"]:
    rows.append({
        "memory_overcommit_ratio": f"1:{ratio}",
        "usable_ram_gb": usable_ram,
        "average_vm_memory_gb": w["average_vm_memory_gb"],
        "theoretical_vm_count": int((usable_ram * ratio) // w["average_vm_memory_gb"]),
        "network_nominal_gbps": network,
        "network_planning_gbps": round(planned_network, 2)
    })
with (out / "capacity_results.csv").open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)
payload = {
    "scenario": cfg["scenario"], "assumptions": cfg,
    "derived_values": {
        "usable_ram_gb": usable_ram,
        "nominal_aggregate_network_gbps": network,
        "planned_network_gbps_at_utilization_target": round(planned_network, 2),
        "vm_exit_to_native_syscall_ratio": round(w["vm_exit_cost_us"] / w["native_syscall_cost_us"], 2)
    },
    "capacity_scenarios": rows,
    "interpretation": [
        "VM counts are theoretical memory-based limits, not validated deployment capacity.",
        "CPU overhead percentages are illustrative inputs, not benchmark results.",
        "Actual capacity also depends on CPU scheduling, storage, workload peaks and operational reserve."
    ]
}
(out / "capacity_results.json").write_text(json.dumps(payload, indent=2) + "\n")
print("Analytical model completed successfully.")
print(f"Usable RAM: {usable_ram} GB")
print(f"Nominal aggregate network: {network} Gbps")
print(f"Planning network capacity: {planned_network:.2f} Gbps")
for row in rows:
    print(f"{row['memory_overcommit_ratio']}: {row['theoretical_vm_count']} theoretical VMs")
print("Results saved in results/capacity_results.csv and .json")
