from __future__ import annotations

from .models import Asset, ScoreResult, BuyPlan


def build_buy_plan(asset: Asset, score: ScoreResult) -> BuyPlan:
    hard_blocks = []
    if score.valuation_pass == "FAIL":
        hard_blocks.append("valuation failed")
    if score.numbers_pass in {"FAIL", "PENDING"}:
        hard_blocks.append(f"numbers {score.numbers_pass.lower()}")
    if score.price_setup_pass == "FAIL":
        hard_blocks.append("price setup failed")
    if score.invalidation_defined != "YES":
        hard_blocks.append("invalidation missing")
    if score.risk_cap_defined != "YES":
        hard_blocks.append("risk cap missing")

    if hard_blocks:
        return BuyPlan(
            ticker=asset.ticker,
            asset_name=asset.name,
            action="NO BUY",
            suggested_allocation_pct=0.0,
            max_loss_rule="0% until all mandatory gates pass",
            entry_zone=score.entry_zone,
            invalidation=score.invalidation,
            reason=f"Blocked: {', '.join(hard_blocks)}. {score.notes}",
            risk_status="BLOCKED",
        )

    if score.price_setup_pass == "PASS" and score.valuation_pass == "PASS" and score.numbers_pass == "PASS" and score.score >= 8:
        return BuyPlan(
            ticker=asset.ticker,
            asset_name=asset.name,
            action="BUY PROBE",
            suggested_allocation_pct=score.suggested_probe_allocation_pct,
            max_loss_rule=f"Maximum modeled loss {score.max_loss_pct_of_portfolio:.4f}% of portfolio",
            entry_zone=score.entry_zone,
            invalidation=score.invalidation,
            reason=f"All first-entry gates passed. {score.notes}",
            risk_status="CONTROLLED_PROBE",
        )

    return BuyPlan(
        ticker=asset.ticker,
        asset_name=asset.name,
        action="PAPER BUY",
        suggested_allocation_pct=0.0,
        max_loss_rule="Paper only; no real capital",
        entry_zone=score.entry_zone,
        invalidation=score.invalidation,
        reason=f"No hard failure, but not enough evidence for real capital. {score.notes}",
        risk_status="PAPER_ONLY",
    )
