from __future__ import annotations

from .models import Asset, MarketSnapshot, NewsItem, ScoreResult, FundamentalSnapshot, TechnicalSnapshot
from .risk import build_risk_parameters


def _valuation_gate(asset: Asset, fundamental: FundamentalSnapshot) -> tuple[str, list[str]]:
    notes: list[str] = []
    if not fundamental.ok:
        return "FAIL", [f"Fundamental data failed: {fundamental.error}"]

    sector = asset.sector.lower()

    if "bank" in sector:
        pe = fundamental.forward_pe or fundamental.trailing_pe
        pb = fundamental.price_to_book
        roe = fundamental.return_on_equity
        if pe is not None and pb is not None:
            notes.append(f"Bank P/E {pe:.2f}, P/B {pb:.2f}")
            if 0 < pe <= 12 and 0 < pb <= 1.5 and (roe is None or roe >= 0.08):
                return "PASS", notes
            if 0 < pe <= 15 and 0 < pb <= 2.0:
                return "PARTIAL", notes
            return "FAIL", notes
        return "PARTIAL", ["Bank valuation incomplete: need P/E and P/B"]

    if "semiconductor" in sector or "ai" in sector:
        pe = fundamental.forward_pe or fundamental.trailing_pe
        ev_ebitda = fundamental.enterprise_to_ebitda
        fcf = fundamental.free_cashflow
        if pe is not None:
            notes.append(f"Forward/trailing P/E {pe:.2f}")
        if ev_ebitda is not None:
            notes.append(f"EV/EBITDA {ev_ebitda:.2f}")
        if pe is not None and 0 < pe <= 30 and (ev_ebitda is None or ev_ebitda <= 20) and (fcf is None or fcf > 0):
            return "PASS", notes
        if pe is not None and 0 < pe <= 38:
            return "PARTIAL", notes
        return "FAIL", notes or ["Semiconductor valuation incomplete"]

    ev_ebitda = fundamental.enterprise_to_ebitda
    pe = fundamental.forward_pe or fundamental.trailing_pe
    if ev_ebitda is not None and 0 < ev_ebitda <= 14:
        return "PASS", [f"EV/EBITDA {ev_ebitda:.2f}"]
    if pe is not None and 0 < pe <= 25:
        return "PARTIAL", [f"P/E {pe:.2f}"]
    return "FAIL", ["No acceptable valuation evidence"]


def _numbers_gate(asset: Asset, fundamental: FundamentalSnapshot) -> tuple[str, list[str]]:
    if not fundamental.ok:
        return "FAIL", ["No usable fundamental snapshot"]

    sector = asset.sector.lower()
    risk = asset.risk_flag.lower()

    if "aktor" in asset.name.lower() or "dilution" in risk:
        return "PENDING", ["AKTOR AMK/final allocation event must settle before real buy"]

    if "bank" in sector:
        available = sum(v is not None for v in [fundamental.forward_pe, fundamental.trailing_pe, fundamental.price_to_book, fundamental.return_on_equity])
        if available >= 3:
            return "PARTIAL", ["Bank fundamentals available; current earnings event still pending"]
        return "PENDING", ["Bank numbers incomplete"]

    available = sum(v is not None for v in [fundamental.forward_pe, fundamental.trailing_pe, fundamental.enterprise_to_ebitda, fundamental.profit_margins, fundamental.free_cashflow])
    if available >= 3:
        return "PASS", ["Multiple fundamental fields available"]
    if available >= 1:
        return "PARTIAL", ["Limited fundamental fields available"]
    return "FAIL", ["No useful fundamental fields"]


def score_asset(
    asset: Asset,
    market: MarketSnapshot,
    news_items: list[NewsItem],
    fundamental: FundamentalSnapshot | None = None,
    technical: TechnicalSnapshot | None = None,
) -> ScoreResult:
    related_news = [n for n in news_items if asset.ticker in n.matched_tickers]
    theme_pass = "PASS" if related_news or asset.reason else "PARTIAL"

    notes: list[str] = []
    if related_news:
        notes.append(f"Matched {len(related_news)} news item(s)")

    if fundamental is None:
        valuation_pass = "FAIL"
        numbers_pass = "FAIL"
        notes.append("Fundamental snapshot missing")
    else:
        valuation_pass, valuation_notes = _valuation_gate(asset, fundamental)
        numbers_pass, numbers_notes = _numbers_gate(asset, fundamental)
        notes.extend(valuation_notes)
        notes.extend(numbers_notes)

    if technical is None or not technical.ok:
        price_setup_pass = "FAIL"
        invalidation_defined = "NO"
        risk_cap_defined = "NO"
        risk = build_risk_parameters(technical or TechnicalSnapshot(ticker=asset.ticker, source="none", ok=False, error="Missing technical snapshot"))
        notes.append(risk.reason)
    else:
        price_setup_pass = technical.setup_status
        risk = build_risk_parameters(technical)
        invalidation_defined = "YES" if risk.valid else "NO"
        risk_cap_defined = "YES" if risk.valid else "NO"
        notes.append(
            f"Technical {technical.setup_status}; SMA20 {technical.sma20:.2f}; SMA50 {technical.sma50:.2f}; stop {technical.stop_price:.2f}"
        )
        notes.append(risk.reason)

    if market.ok and market.day_change_pct is not None and market.day_change_pct > 3.0:
        price_setup_pass = "FAIL"
        notes.append(f"Daily move {market.day_change_pct:.2f}% triggers chase block")

    gate_score = {"PASS": 2, "PARTIAL": 1, "PENDING": 0, "FAIL": -2, "UNKNOWN": -1}
    score = sum(gate_score.get(g, 0) for g in [theme_pass, numbers_pass, valuation_pass, price_setup_pass])
    if invalidation_defined == "YES":
        score += 1
    if risk_cap_defined == "YES":
        score += 1

    status = "CANDIDATE_REVIEW"
    if price_setup_pass == "FAIL" or valuation_pass == "FAIL" or numbers_pass == "FAIL":
        status = "NO_BUY_BLOCKED"
    elif price_setup_pass == "PASS" and valuation_pass == "PASS" and numbers_pass == "PASS":
        status = "BUY_ENGINE_ELIGIBLE"
    elif price_setup_pass in {"PASS", "PARTIAL"}:
        status = "PAPER_OR_WATCH"

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
        entry_zone=risk.entry_zone,
        invalidation=risk.invalidation,
        stop_distance_pct=technical.stop_distance_pct if technical and technical.ok else None,
        suggested_probe_allocation_pct=risk.suggested_probe_allocation_pct,
        max_loss_pct_of_portfolio=risk.max_loss_pct_of_portfolio,
    )
