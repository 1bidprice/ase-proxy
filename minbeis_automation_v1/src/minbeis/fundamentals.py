from __future__ import annotations

from typing import Iterable

from .models import Asset, FundamentalSnapshot


def _safe_float(value):
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def fetch_fundamental_snapshot(asset: Asset) -> FundamentalSnapshot:
    try:
        import yfinance as yf

        info = yf.Ticker(asset.ticker).info or {}
        snapshot = FundamentalSnapshot(
            ticker=asset.ticker,
            source="yfinance-info",
            ok=True,
            market_cap=_safe_float(info.get("marketCap")),
            trailing_pe=_safe_float(info.get("trailingPE")),
            forward_pe=_safe_float(info.get("forwardPE")),
            price_to_book=_safe_float(info.get("priceToBook")),
            enterprise_to_ebitda=_safe_float(info.get("enterpriseToEbitda")),
            profit_margins=_safe_float(info.get("profitMargins")),
            return_on_equity=_safe_float(info.get("returnOnEquity")),
            revenue_growth=_safe_float(info.get("revenueGrowth")),
            earnings_growth=_safe_float(info.get("earningsGrowth")),
            free_cashflow=_safe_float(info.get("freeCashflow")),
            total_debt=_safe_float(info.get("totalDebt")),
            total_cash=_safe_float(info.get("totalCash")),
            currency=info.get("currency"),
        )

        meaningful = [
            snapshot.trailing_pe,
            snapshot.forward_pe,
            snapshot.price_to_book,
            snapshot.enterprise_to_ebitda,
            snapshot.return_on_equity,
            snapshot.free_cashflow,
        ]
        if not any(value is not None for value in meaningful):
            snapshot.ok = False
            snapshot.error = "No meaningful valuation/fundamental fields returned"
        return snapshot
    except Exception as exc:
        return FundamentalSnapshot(
            ticker=asset.ticker,
            source="yfinance-info",
            ok=False,
            error=f"{type(exc).__name__}: {exc}",
        )


def fetch_fundamental_snapshots(assets: Iterable[Asset]) -> list[FundamentalSnapshot]:
    return [fetch_fundamental_snapshot(asset) for asset in assets]
