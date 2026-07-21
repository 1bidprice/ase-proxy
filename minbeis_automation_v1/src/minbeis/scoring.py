from __future__ import annotations

from .models import Asset, MarketSnapshot, NewsItem, ScoreResult


def score_asset(asset: Asset, market: MarketSnapshot, news_items: list[NewsItem]) -> ScoreResult:
    # Conservative scoring. It blocks buys unless essential gates are present.
    related_news = [n for n in news_items if asset.ticker in n.matched_tickers]

    theme_pass = "PASS" if related_news or asset.reason else "PARTIAL"
    price_setup_pass = "UNKNOWN"
    numbers_pass = "UNKNOWN"
    valuation_pass = "UNKNOWN"
    invalidation_defined = "NO"
    risk_cap_defined = "NO"

    notes = []

    if market.ok and market.last_price:
        notes.append(f"Price available: {market.last_price}")
        if market.day_change_pct is not None:
            if market.day_change_pct > 3.0:
                price_setup_pass = "FAIL"
                notes.append("Large positive daily move: chase risk")
            elif market.day_change_pct < -7.0:
                price_setup_pass = "PARTIAL"
                notes.append("Sharp fall: requires event validation, not automatic buy")
            else:
                price_setup_pass = "PARTIAL"
                notes.append("Price exists but support/invalidation not defined")
    else:
        price_setup_pass = "FAIL"
        notes.append(f"Market data failed: {market.error}")

    sector_l = asset.sector.lower()
    name_l = asset.name.lower()
    risk_l = asset.risk_flag.lower()

    if "bank" in sector_l:
        numbers_pass = "PENDING"
        notes.append("Bank results/guidance required before buy upgrade")

    if "aktor" in name_l or "dilution" in risk_l:
        numbers_pass = "PENDING"
        notes.append("AMK/final allocation required before buy upgrade")

    if "semiconductor" in sector_l or "ai" in sector_l:
        numbers_pass = "PARTIAL"
        notes.append("AI infrastructure theme requires valuation/backlog confirmation")

    valuation_pass = "UNKNOWN"

    score = 0
    for gate in [theme_pass, numbers_pass, valuation_pass, price_setup_pass]:
        if gate == "PASS":
            score += 2
        elif gate == "PARTIAL":
            score += 1
        elif gate == "PENDING":
            score += 0

    if price_setup_pass == "FAIL":
        score -= 2

    status = "RESEARCH"
    if market.ok:
        status = "WATCH_CHECK"
    if price_setup_pass == "FAIL":
        status = "NO_BUY_BLOCKED"

    return ScoreResult(
        ticker=asset.ticker,
        theme_pass=theme_pass,
        numbers_pass=numbers_pass,
        valuation_pass=valuation_pass,
        price_setup_pass=price_setup_pass,
        invalidation_defined=invalidation_defined,
        risk_cap_defined=risk_cap_defined,
        status=status,
        score=score,
        notes=" | ".join(notes),
    )
