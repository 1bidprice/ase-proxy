from __future__ import annotations

import os
from datetime import datetime

from .models import BuyPlan, ScoreResult


def _client():
    import gspread
    from google.oauth2.service_account import Credentials

    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not creds_path:
        raise RuntimeError("GOOGLE_APPLICATION_CREDENTIALS is not set")

    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
    return gspread.authorize(creds)


def write_run_log(spreadsheet_id: str, run_id: str, output: str, errors: str = "") -> None:
    gc = _client()
    sh = gc.open_by_key(spreadsheet_id)
    ws = sh.worksheet("Automation Run Log")
    ws.append_row([
        run_id,
        datetime.utcnow().isoformat(),
        "DAILY_AFTER_CLOSE",
        "",
        "OK",
        "OK",
        "OK",
        "OK",
        "OK",
        output,
        errors,
        "Written by MINBEIS Automation Engine v1",
    ])


def write_candidate_buy_plans(spreadsheet_id: str, plans: list[BuyPlan], scores: dict[str, ScoreResult]) -> None:
    gc = _client()
    sh = gc.open_by_key(spreadsheet_id)
    ws = sh.worksheet("Candidate Buy Plans")

    for plan in plans:
        score = scores[plan.ticker]
        ws.append_row([
            f"AUTO-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{plan.ticker}",
            plan.generated_at[:10],
            "AUTO",
            plan.ticker,
            score.status,
            score.theme_pass,
            score.numbers_pass,
            score.valuation_pass,
            score.price_setup_pass,
            score.invalidation_defined,
            score.risk_cap_defined,
            plan.action,
            f"{plan.suggested_allocation_pct:.2f}%",
            plan.max_loss_rule,
            "Automated run; verify official sources before upgrade.",
            plan.reason,
        ])


def write_broker_export_sheet(spreadsheet_id: str, plans: list[BuyPlan]) -> None:
    gc = _client()
    sh = gc.open_by_key(spreadsheet_id)
    ws = sh.worksheet("Broker Export")

    for plan in plans:
        row = plan.to_broker_row()
        ws.append_row([
            f"AUTO-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{plan.ticker}",
            row["date"],
            row["ticker"],
            row["asset"],
            row["action"],
            row["suggested_allocation"],
            row["max_loss"],
            row["entry_zone"],
            row["invalidation"],
            row["reason"],
            row["human_approval"],
            row["broker_executed"],
            row["execution_notes"],
            row["risk_status"],
        ])
