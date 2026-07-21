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
