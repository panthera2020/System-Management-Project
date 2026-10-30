"""Recommendation engine service.

For the MVP it inspects a dict of simple metrics (cpu, ram_percent, disk_percent, battery_percent)
and returns a list of recommendation dicts with keys:
    issue, evidence, benefit, risk, action
The logic is deliberately lightweight – thresholds are hard‑coded but can be
replaced later with a more sophisticated rule‑engine.
"""

from typing import List, Dict, Any

def get_recommendations(metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
    recs: List[Dict[str, Any]] = []
    cpu = metrics.get("cpu_percent", 0)
    ram = metrics.get("ram_percent", 0)
    disk = metrics.get("disk_percent", 0)
    batt = metrics.get("battery_percent", 0)
    if cpu > 80:
        recs.append({
            "issue": "High CPU usage",
            "evidence": f"CPU at {cpu}%",
            "benefit": "Potential speed improvement",
            "risk": "Closing a critical process may cause data loss",
            "action": "Review top CPU processes and close if safe",
        })
    if ram > 85:
        recs.append({
            "issue": "High memory pressure",
            "evidence": f"RAM at {ram}%",
            "benefit": "Free memory, reduce paging",
            "risk": "Closing system services may destabilize OS",
            "action": "Identify unnecessary apps and close",
        })
    if disk > 90:
        recs.append({
            "issue": "Low disk free space",
            "evidence": f"Disk at {disk}% used",
            "benefit": "Avoid out‑of‑space errors",
            "risk": "Deleting files may remove important data",
            "action": "Run storage cleanup and review large files",
        })
    if batt and batt < 20:
        recs.append({
            "issue": "Low battery",
            "evidence": f"Battery at {batt}%",
            "benefit": "Extend runtime",
            "risk": "Power‑saving may reduce performance",
            "action": "Enable power‑saving mode",
        })
    return recs
