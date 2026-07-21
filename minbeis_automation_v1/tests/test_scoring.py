from src.minbeis.models import Asset, MarketSnapshot
from src.minbeis.scoring import score_asset
from src.minbeis.buy_engine import build_buy_plan


def test_missing_valuation_blocks_buy():
    asset = Asset(
        ticker="TEST",
        name="Test Asset",
        market="Test",
        sector="Banks",
        priority="High",
        active=True,
    )
    market = MarketSnapshot(
        ticker="TEST",
        source="unit",
        ok=True,
        last_price=10.0,
        previous_close=9.9,
        day_change_pct=1.01,
        volume=1000,
    )
    score = score_asset(asset, market, [])
    plan = build_buy_plan(asset, score)
    assert plan.action == "NO BUY"
    assert plan.suggested_allocation_pct == 0.0
