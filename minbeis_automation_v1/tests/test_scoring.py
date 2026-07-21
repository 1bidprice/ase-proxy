from src.minbeis.models import Asset, MarketSnapshot, FundamentalSnapshot, TechnicalSnapshot
from src.minbeis.scoring import score_asset
from src.minbeis.buy_engine import build_buy_plan
from src.minbeis.main import run


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
    fundamental = FundamentalSnapshot(ticker="TEST", source="unit", ok=False, error="missing")
    technical = TechnicalSnapshot(
        ticker="TEST",
        source="unit",
        ok=True,
        last_price=10.0,
        sma20=9.9,
        sma50=9.5,
        low20=9.2,
        atr14=0.2,
        entry_zone_low=9.85,
        entry_zone_high=10.0,
        stop_price=9.4,
        stop_distance_pct=6.0,
        setup_status="PASS",
    )
    score = score_asset(asset, market, [], fundamental=fundamental, technical=technical)
    plan = build_buy_plan(asset, score)
    assert plan.action == "NO BUY"
    assert plan.suggested_allocation_pct == 0.0


def test_fixture_engine_can_generate_controlled_buy_probe(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    summary = run(dry_run=True, fixture_mode=True)
    probes = [p for p in summary["plans"] if p["action"] == "BUY PROBE"]
    assert len(probes) >= 1
    assert any(p["ticker"] == "STM" for p in probes)
    stm = next(p for p in probes if p["ticker"] == "STM")
    assert 0.25 <= stm["allocation_pct"] <= 0.75
    assert stm["invalidation"] != "N/A"


def test_fixture_writeback_is_forbidden(monkeypatch):
    monkeypatch.setenv("MINBEIS_WRITEBACK", "true")
    try:
        run(dry_run=False, fixture_mode=True)
    except RuntimeError as exc:
        assert "Fixture mode is forbidden" in str(exc)
    else:
        raise AssertionError("Fixture writeback must be blocked")
