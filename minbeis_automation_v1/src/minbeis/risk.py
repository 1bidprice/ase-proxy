from __future__ import annotations

from dataclasses import dataclass

from .models import TechnicalSnapshot


@dataclass
class RiskParameters:
    valid: bool
    suggested_probe_allocation_pct: float
    max_loss_pct_of_portfolio: float
    entry_zone: str
    invalidation: str
    reason: str


def build_risk_parameters(
    technical: TechnicalSnapshot,
    risk_budget_pct_of_portfolio: float = 0.05,
    probe_cap_pct_of_portfolio: float = 0.75,
) -> RiskParameters:
    if not technical.ok:
        return RiskParameters(False, 0.0, 0.0, "N/A", "N/A", f"Technical data failed: {technical.error}")

    required = [
        technical.entry_zone_low,
        technical.entry_zone_high,
        technical.stop_price,
        technical.stop_distance_pct,
    ]
    if any(value is None for value in required):
        return RiskParameters(False, 0.0, 0.0, "N/A", "N/A", "Missing entry/stop parameters")

    stop_distance_pct = float(technical.stop_distance_pct)
    if stop_distance_pct < 1.5 or stop_distance_pct > 10.0:
        return RiskParameters(
            False,
            0.0,
            0.0,
            "N/A",
            "N/A",
            f"Stop distance {stop_distance_pct:.2f}% outside allowed 1.5%-10%",
        )

    risk_based_position_pct = (risk_budget_pct_of_portfolio / stop_distance_pct) * 100.0
    allocation = min(probe_cap_pct_of_portfolio, risk_based_position_pct)
    allocation = max(0.25, round(allocation, 2))
    max_loss_pct = round((allocation * stop_distance_pct) / 100.0, 4)

    return RiskParameters(
        valid=True,
        suggested_probe_allocation_pct=allocation,
        max_loss_pct_of_portfolio=max_loss_pct,
        entry_zone=f"{technical.entry_zone_low:.2f}-{technical.entry_zone_high:.2f}",
        invalidation=f"Close below {technical.stop_price:.2f}",
        reason=f"Stop distance {stop_distance_pct:.2f}%; portfolio risk cap {max_loss_pct:.4f}%",
    )
