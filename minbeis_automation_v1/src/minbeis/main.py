from __future__ import annotations

from datetime import datetime
from pathlib import Path
import argparse
import json
import os

from .config import load_env, load_universe, load_news_sources, get_setting
from .market_data import fetch_market_snapshots
from .news_intake import fetch_rss_news
from .scoring import score_asset
from .buy_engine import build_buy_plan
from .broker_export import write_broker_export
from .sheet_writer import write_run_log, write_candidate_buy_plans, write_broker_export_sheet


def run(dry_run: bool = True) -> dict:
    load_env()

    spreadsheet_id = get_setting("SPREADSHEET_ID")
    writeback_enabled = get_setting("MINBEIS_WRITEBACK", "false").lower() == "true"
    run_id = f"RUN-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"

    assets = load_universe()
    news_sources = load_news_sources()

    snapshots = fetch_market_snapshots(assets)
    snapshot_map = {s.ticker: s for s in snapshots}

    news_items = fetch_rss_news(news_sources, assets)

    scores = {}
    plans = []

    for asset in assets:
        snapshot = snapshot_map[asset.ticker]
        score = score_asset(asset, snapshot, news_items)
        plan = build_buy_plan(asset, score)
        scores[asset.ticker] = score
        plans.append(plan)

    out_dir = Path("output")
    out_dir.mkdir(exist_ok=True)

    broker_path = write_broker_export(plans, out_dir / f"broker_export_{run_id}.csv")

    summary = {
        "run_id": run_id,
        "timestamp": datetime.utcnow().isoformat(),
        "assets_checked": len(assets),
        "news_items_matched": len(news_items),
        "plans": [
            {
                "ticker": p.ticker,
                "asset": p.asset_name,
                "action": p.action,
                "allocation_pct": p.suggested_allocation_pct,
                "risk_status": p.risk_status,
                "reason": p.reason[:300],
            }
            for p in plans
        ],
        "broker_export_path": str(broker_path),
        "writeback_enabled": writeback_enabled,
        "dry_run": dry_run,
    }

    (out_dir / f"summary_{run_id}.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    if writeback_enabled and not dry_run:
        if not spreadsheet_id:
            raise RuntimeError("SPREADSHEET_ID missing")
        write_candidate_buy_plans(spreadsheet_id, plans, scores)
        write_broker_export_sheet(spreadsheet_id, plans)
        write_run_log(spreadsheet_id, run_id, output="Completed with Google Sheet writeback", errors="")
    else:
        print(json.dumps(summary, ensure_ascii=False, indent=2))

    return summary


def main():
    parser = argparse.ArgumentParser(description="Run MINBEIS Automation Engine v1")
    parser.add_argument("--dry-run", action="store_true", help="Run without Google Sheet writeback")
    parser.add_argument("--writeback", action="store_true", help="Run with Google Sheet writeback if credentials exist")
    args = parser.parse_args()

    dry_run = True
    if args.writeback:
        dry_run = False
        os.environ["MINBEIS_WRITEBACK"] = "true"

    if args.dry_run:
        dry_run = True
        os.environ["MINBEIS_WRITEBACK"] = "false"

    run(dry_run=dry_run)


if __name__ == "__main__":
    main()
