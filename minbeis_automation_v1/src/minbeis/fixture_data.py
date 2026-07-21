from __future__ import annotations

from .models import Asset, MarketSnapshot, NewsItem


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
