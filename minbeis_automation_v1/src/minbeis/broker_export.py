from __future__ import annotations

from pathlib import Path
import csv

from .models import BuyPlan


BROKER_FIELDS = [
    "date",
    "ticker",
    "asset",
    "action",
    "suggested_allocation",
    "max_loss",
    "entry_zone",
    "invalidation",
    "reason",
    "human_approval",
    "broker_executed",
    "execution_notes",
    "risk_status",
]


def write_broker_export(plans: list[BuyPlan], out_path: Path) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=BROKER_FIELDS)
        writer.writeheader()
        for plan in plans:
            writer.writerow(plan.to_broker_row())
    return out_path
