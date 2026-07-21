from __future__ import annotations

from typing import Iterable
import math

from .models import Asset, TechnicalSnapshot


def fetch_technical_snapshot(asset: Asset) -> TechnicalSnapshot:
    try:
        import yfinance as yf

        hist = yf.Ticker(asset.ticker).history(period="1y", interval="1d", auto_adjust=False)
        required = {"High", "Low", "Close"}
        if hist is None or hist.empty or not required.issubset(hist.columns):
            return TechnicalSnapshot(
                ticker=asset.ticker,
                source="yfinance-history",
                ok=False,
                error="Insufficient OHLC history",
            )

        hist = hist.dropna(subset=["High", "Low", "Close"])
        if len(hist) < 55:
            return TechnicalSnapshot(
                ticker=asset.ticker,
                source="yfinance-history",
                ok=False,
                error=f"Only {len(hist)} daily rows; need at least 55",
            )

        close = hist["Close"].astype(float)
        high = hist["High"].astype(float)
        low = hist["Low"].astype(float)
        prev_close = close.shift(1)
        true_range = (high - low).to_frame("hl")
        true_range["hc"] = (high - prev_close).abs()
        true_range["lc"] = (low - prev_close).abs()
        tr = true_range.max(axis=1)

        last_price = float(close.iloc[-1])
        sma20 = float(close.tail(20).mean())
        sma50 = float(close.tail(50).mean())
        low20 = float(low.tail(20).min())
        atr14 = float(tr.tail(14).mean())
        avg_volume20 = None
        current_volume = None
        if "Volume" in hist.columns:
            volume = hist["Volume"].dropna().astype(float)
            if len(volume):
                avg_volume20 = float(volume.tail(20).mean())
                current_volume = float(volume.iloc[-1])

        distance_from_sma20_pct = ((last_price - sma20) / sma20) * 100 if sma20 else None
        support_candidate = max(low20 * 0.995, sma50 - 1.5 * atr14)
        stop_price = min(support_candidate, last_price * 0.985)
        stop_distance_pct = ((last_price - stop_price) / last_price) * 100 if last_price else None

        entry_zone_low = min(last_price, sma20 * 0.995)
        entry_zone_high = max(last_price, sma20 * 1.01)

        setup_status = "FAIL"
        if (
            last_price >= sma20 >= sma50
            and distance_from_sma20_pct is not None
            and -1.5 <= distance_from_sma20_pct <= 3.0
            and stop_distance_pct is not None
            and 1.5 <= stop_distance_pct <= 9.0
        ):
            setup_status = "PASS"
        elif last_price >= sma50 and stop_distance_pct is not None and stop_distance_pct <= 12.0:
            setup_status = "PARTIAL"

        values = [last_price, sma20, sma50, low20, atr14, stop_price]
        if not all(math.isfinite(v) for v in values):
            return TechnicalSnapshot(
                ticker=asset.ticker,
                source="yfinance-history",
                ok=False,
                error="Non-finite technical values",
            )

        return TechnicalSnapshot(
            ticker=asset.ticker,
            source="yfinance-history",
            ok=True,
            last_price=last_price,
            sma20=sma20,
            sma50=sma50,
            low20=low20,
            atr14=atr14,
            avg_volume20=avg_volume20,
            current_volume=current_volume,
            distance_from_sma20_pct=distance_from_sma20_pct,
            entry_zone_low=entry_zone_low,
            entry_zone_high=entry_zone_high,
            stop_price=stop_price,
            stop_distance_pct=stop_distance_pct,
            setup_status=setup_status,
        )
    except Exception as exc:
        return TechnicalSnapshot(
            ticker=asset.ticker,
            source="yfinance-history",
            ok=False,
            error=f"{type(exc).__name__}: {exc}",
        )


def fetch_technical_snapshots(assets: Iterable[Asset]) -> list[TechnicalSnapshot]:
    return [fetch_technical_snapshot(asset) for asset in assets]
