from __future__ import annotations

from .models import Asset, ScoreResult, BuyPlan


def build_buy_plan(asset: Asset, score: ScoreResult) -> BuyPlan:
    # Safety-first buy engine.
    # No valuation / no invalidation / no risk cap = no real buy.
    mandatory_failures = []

    if score.valuation_pass not in {"PASS", "PARTIAL"}:
        mandatory_failures.append("valuation missing")
    if score.price_setup_pass == "FAIL":
        mandatory_failures.append("price setup failed")
    if score.invalidation_defined != "YES":
        mandatory_failures.append("invalidation missing")
    if score.risk_cap_defined != "YES":
        mandatory_failures.append("risk cap missing")

    if mandatory_failures:
        return BuyPlan(
            ticker=asset.ticker,
            asset_name=asset.name,
            action="NO BUY",
            suggested_allocation_pct=0.0,
            max_loss_rule="0€ until valuation, invalidation and risk cap are defined",
            entry_zone="N/A",
            invalidation="N/A",
            reason=f"Blocked: {', '.join(mandatory_failures)}. Notes: {score.notes}",
            risk_status="BLOCKED",
        )

    if score.score >= 7:
        return BuyPlan(
            ticker=asset.ticker,
            asset_name=asset.name,
            action="BUY PROBE",
            suggested_allocation_pct=0.5,
            max_loss_rule="Max loss must be defined in risk module before export",
            entry_zone="To be calculated by price module",
            invalidation="To be calculated by risk module",
            reason="All essential gates passed for probe position",
            risk_status="CONTROLLED",
        )

    return BuyPlan(
        ticker=asset.ticker,
        asset_name=asset.name,
        action="PAPER BUY",
        suggested_allocation_pct=0.0,
        max_loss_rule="Paper only",
        entry_zone="Paper plan only",
        invalidation="Paper plan only",
        reason="Some gates passed but score not enough for real allocation",
        risk_status="PAPER_ONLY",
    )
