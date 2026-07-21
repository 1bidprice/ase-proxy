from __future__ import annotations

from typing import Iterable
import math

from .models import Asset, MarketSnapshot


def fetch_yfinance_snapshot(asset: Asset) -> MarketSnapshot:
    # Public/delayed prototype adapter.
    # Production warning: yfinance/Yahoo is not an official exchange feed.
    try:
        import yfinance as yf

        ticker = yf.Ticker(asset.ticker)
        hist = ticker.history(period="5d", interval="1d")

        if hist is None or hist.empty or "Close" not in hist.columns:
            return MarketSnapshot(
                ticker=asset.ticker,
                source="yfinance",
                ok=False,
                error="No historical close data returned",
            )

        closes = hist["Close"].dropna()
        volumes = hist["Volume"].dropna() if "Volume" in hist.columns else []

        if len(closes) == 0:
            return MarketSnapshot(
                ticker=asset.ticker,
                source="yfinance",
                ok=False,
                error="No valid closes",
            )

        last_price = float(closes.iloc[-1])
        previous_close = float(closes.iloc[-2]) if len(closes) >= 2 else None

        if previous_close and previous_close != 0:
            day_change_pct = ((last_price - previous_close) / previous_close) * 100.0
        else:
            day_change_pct = None

        volume = float(volumes.iloc[-1]) if len(volumes) else None

        if not math.isfinite(last_price):
            return MarketSnapshot(
                ticker=asset.ticker,
                source="yfinance",
                ok=False,
                error="Non-finite last price",
            )

        return MarketSnapshot(
            ticker=asset.ticker,
            source="yfinance",
            ok=True,
            last_price=last_price,
            previous_close=previous_close,
            day_change_pct=day_change_pct,
            volume=volume,
        )
    except Exception as exc:
        return MarketSnapshot(
            ticker=asset.ticker,
            source="yfinance",
            ok=False,
            error=f"{type(exc).__name__}: {exc}",
        )


def fetch_market_snapshots(assets: Iterable[Asset]) -> list[MarketSnapshot]:
    return [fetch_yfinance_snapshot(asset) for asset in assets]
