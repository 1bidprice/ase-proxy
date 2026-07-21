from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Literal, Dict, Any, List


Action = Literal["NO BUY", "PAPER BUY", "BUY PROBE", "BUY STARTER", "BUY CORE"]


@dataclass
class Asset:
    ticker: str
    name: str
    market: str
    sector: str
    priority: str
    active: bool
    risk_flag: str = ""
    reason: str = ""
    aliases: List[str] = field(default_factory=list)


@dataclass
class MarketSnapshot:
    ticker: str
    source: str
    ok: bool
    last_price: Optional[float] = None
    previous_close: Optional[float] = None
    day_change_pct: Optional[float] = None
    volume: Optional[float] = None
    currency: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    error: Optional[str] = None


@dataclass
class FundamentalSnapshot:
    ticker: str
    source: str
    ok: bool
    market_cap: Optional[float] = None
    trailing_pe: Optional[float] = None
    forward_pe: Optional[float] = None
    price_to_book: Optional[float] = None
    enterprise_to_ebitda: Optional[float] = None
    profit_margins: Optional[float] = None
    return_on_equity: Optional[float] = None
    revenue_growth: Optional[float] = None
    earnings_growth: Optional[float] = None
    free_cashflow: Optional[float] = None
    total_debt: Optional[float] = None
    total_cash: Optional[float] = None
    currency: Optional[str] = None
    error: Optional[str] = None


@dataclass
class TechnicalSnapshot:
    ticker: str
    source: str
    ok: bool
    last_price: Optional[float] = None
    sma20: Optional[float] = None
    sma50: Optional[float] = None
    low20: Optional[float] = None
    atr14: Optional[float] = None
    avg_volume20: Optional[float] = None
    current_volume: Optional[float] = None
    distance_from_sma20_pct: Optional[float] = None
    entry_zone_low: Optional[float] = None
    entry_zone_high: Optional[float] = None
    stop_price: Optional[float] = None
    stop_distance_pct: Optional[float] = None
    setup_status: str = "UNKNOWN"
    error: Optional[str] = None


@dataclass
class NewsItem:
    source: str
    title: str
    link: str
    published: Optional[str] = None
    matched_tickers: List[str] = field(default_factory=list)


@dataclass
class ScoreResult:
    ticker: str
    theme_pass: str
    numbers_pass: str
    valuation_pass: str
    price_setup_pass: str
    invalidation_defined: str
    risk_cap_defined: str
    status: str
    score: int
    notes: str
    entry_zone: str = "N/A"
    invalidation: str = "N/A"
    stop_distance_pct: Optional[float] = None
    suggested_probe_allocation_pct: float = 0.0
    max_loss_pct_of_portfolio: float = 0.0


@dataclass
class BuyPlan:
    ticker: str
    asset_name: str
    action: Action
    suggested_allocation_pct: float
    max_loss_rule: str
    entry_zone: str
    invalidation: str
    reason: str
    risk_status: str
    generated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_broker_row(self) -> Dict[str, Any]:
        return {
            "date": self.generated_at[:10],
            "ticker": self.ticker,
            "asset": self.asset_name,
            "action": self.action,
            "suggested_allocation": f"{self.suggested_allocation_pct:.2f}%",
            "max_loss": self.max_loss_rule,
            "entry_zone": self.entry_zone,
            "invalidation": self.invalidation,
            "reason": self.reason,
            "human_approval": "REQUIRED",
            "broker_executed": "NO",
            "execution_notes": "Human-only boundary",
            "risk_status": self.risk_status,
        }
