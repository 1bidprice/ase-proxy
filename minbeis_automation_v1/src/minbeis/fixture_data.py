from __future__ import annotations

from .models import Asset, MarketSnapshot, NewsItem, FundamentalSnapshot, TechnicalSnapshot


def fixture_market_snapshots(assets: list[Asset]) -> list[MarketSnapshot]:
    prices = {
        "ALPHA.AT": (3.10, 3.04, 1_250_000),
        "ETE.AT": (15.10, 14.95, 900_000),
        "EUROB.AT": (3.40, 3.31, 1_100_000),
        "TPEIR.AT": (7.20, 7.02, 1_000_000),
        "AKTR.AT": (12.05, 12.90, 450_000),
        "STM": (31.20, 30.90, 2_100_000),
    }
    snapshots: list[MarketSnapshot] = []
    for asset in assets:
        last_price, previous_close, volume = prices.get(asset.ticker, (10.0, 9.9, 100_000))
        change = ((last_price - previous_close) / previous_close) * 100 if previous_close else None
        snapshots.append(
            MarketSnapshot(
                ticker=asset.ticker,
                source="fixture",
                ok=True,
                last_price=last_price,
                previous_close=previous_close,
                day_change_pct=change,
                volume=volume,
                currency="EUR" if asset.ticker.endswith(".AT") else "USD",
            )
        )
    return snapshots


def fixture_fundamental_snapshots(assets: list[Asset]) -> list[FundamentalSnapshot]:
    data = {
        "ALPHA.AT": dict(trailing_pe=9.8, forward_pe=8.9, price_to_book=0.95, return_on_equity=0.11),
        "ETE.AT": dict(trailing_pe=10.5, forward_pe=9.4, price_to_book=1.20, return_on_equity=0.14),
        "EUROB.AT": dict(trailing_pe=11.2, forward_pe=10.1, price_to_book=1.30, return_on_equity=0.13),
        "TPEIR.AT": dict(trailing_pe=9.9, forward_pe=8.8, price_to_book=1.15, return_on_equity=0.12),
        "AKTR.AT": dict(trailing_pe=None, forward_pe=None, price_to_book=2.7, enterprise_to_ebitda=18.0, free_cashflow=-10_000_000),
        "STM": dict(trailing_pe=22.0, forward_pe=19.0, price_to_book=3.1, enterprise_to_ebitda=13.0, profit_margins=0.16, free_cashflow=1_000_000_000),
    }
    snapshots: list[FundamentalSnapshot] = []
    for asset in assets:
        values = data.get(asset.ticker, {})
        snapshots.append(
            FundamentalSnapshot(
                ticker=asset.ticker,
                source="fixture",
                ok=True,
                market_cap=10_000_000_000,
                currency="EUR" if asset.ticker.endswith(".AT") else "USD",
                **values,
            )
        )
    return snapshots


def fixture_technical_snapshots(assets: list[Asset]) -> list[TechnicalSnapshot]:
    data = {
        "ALPHA.AT": dict(last_price=3.10, sma20=3.00, sma50=2.85, low20=2.80, atr14=0.08, stop_price=2.88, stop_distance_pct=7.10, setup_status="FAIL", entry_zone_low=2.99, entry_zone_high=3.10),
        "ETE.AT": dict(last_price=15.10, sma20=14.60, sma50=13.90, low20=13.80, atr14=0.35, stop_price=14.10, stop_distance_pct=6.62, setup_status="FAIL", entry_zone_low=14.53, entry_zone_high=15.10),
        "EUROB.AT": dict(last_price=3.40, sma20=3.20, sma50=3.00, low20=2.95, atr14=0.09, stop_price=3.08, stop_distance_pct=9.41, setup_status="FAIL", entry_zone_low=3.18, entry_zone_high=3.40),
        "TPEIR.AT": dict(last_price=7.20, sma20=6.95, sma50=6.60, low20=6.45, atr14=0.20, stop_price=6.65, stop_distance_pct=7.64, setup_status="FAIL", entry_zone_low=6.92, entry_zone_high=7.20),
        "AKTR.AT": dict(last_price=12.05, sma20=12.60, sma50=12.80, low20=11.70, atr14=0.40, stop_price=11.60, stop_distance_pct=3.73, setup_status="FAIL", entry_zone_low=12.05, entry_zone_high=12.73),
        "STM": dict(last_price=31.20, sma20=30.80, sma50=29.60, low20=29.40, atr14=0.70, stop_price=29.85, stop_distance_pct=4.33, setup_status="PASS", entry_zone_low=30.65, entry_zone_high=31.20),
    }
    snapshots: list[TechnicalSnapshot] = []
    for asset in assets:
        values = data.get(asset.ticker)
        if values is None:
            snapshots.append(TechnicalSnapshot(ticker=asset.ticker, source="fixture", ok=False, error="No fixture technical data"))
            continue
        snapshots.append(
            TechnicalSnapshot(
                ticker=asset.ticker,
                source="fixture",
                ok=True,
                avg_volume20=1_000_000,
                current_volume=900_000,
                distance_from_sma20_pct=((values["last_price"] - values["sma20"]) / values["sma20"]) * 100,
                **values,
            )
        )
    return snapshots


def fixture_news_items() -> list[NewsItem]:
    return [
        NewsItem(
            source="fixture-official",
            title="Greek banks prepare for half-year results",
            link="https://example.invalid/banks-results",
            published="2026-07-21",
            matched_tickers=["ALPHA.AT", "ETE.AT", "EUROB.AT", "TPEIR.AT"],
        ),
        NewsItem(
            source="fixture-official",
            title="AKTOR capital increase pricing update",
            link="https://example.invalid/aktor-amk",
            published="2026-07-21",
            matched_tickers=["AKTR.AT"],
        ),
        NewsItem(
            source="fixture-official",
            title="STMicro AI infrastructure demand update",
            link="https://example.invalid/stm-ai",
            published="2026-07-21",
            matched_tickers=["STM"],
        ),
    ]
