"""Preserve successful and failed driver attempts without private log contents."""

import json
import re
from source_mode import ROOT

records = []
for path in sorted((ROOT / ".work/verification").glob("*/run/*/*/commands.json")):
    commands = json.loads(path.read_text())
    steps = []
    for item in commands:
        meta = item.get("metadata", {})
        if "defineVariablesCommand" in item.get("command", {}):
            continue
        error = meta.get("error", {}).get("message", "")
        error = error.replace(str(ROOT), "<repository>")
        error = re.sub(r"[A-Fa-f0-9]{8}(?:-[A-Fa-f0-9]{4}){3}-[A-Fa-f0-9]{12}", "<device>", error)
        steps.append(
            {
                "command": next(iter(item.get("command", {})), "unknown"),
                "status": meta.get("status"),
                "timestampMs": meta.get("timestamp"),
                "driverDurationMs": meta.get("duration"),
                "error": error,
            }
        )
    records.append(
        {
            "flowKey": path.relative_to(ROOT / ".work/verification").parts[0],
            "attempt": path.parent.parent.name,
            "name": path.parent.name,
            "passed": all(step["status"] == "COMPLETED" for step in steps),
            "steps": steps,
        }
    )
(ROOT / "results/trials.json").write_text(
    json.dumps(
        {
            "scope": "All retained local Maestro attempts; durations describe the driver, not app performance. Earlier dirty-source attempts are exploratory, not milestone proof.",
            "attempts": records,
        },
        indent=2,
    )
    + "\n"
)
print(f"{len(records)} retained attempts")
