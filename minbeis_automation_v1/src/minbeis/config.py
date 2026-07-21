from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv
import yaml

from .models import Asset


ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = ROOT / "config"


def load_env() -> None:
    load_dotenv(ROOT / ".env")


def get_setting(name: str, default: str = "") -> str:
    return os.getenv(name, default)


def load_universe(path: Path | None = None) -> list[Asset]:
    path = path or CONFIG_DIR / "watch_universe.yaml"
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    assets: list[Asset] = []
    for item in raw.get("universe", []):
        assets.append(
            Asset(
                ticker=item["ticker"],
                name=item["name"],
                market=item["market"],
                sector=item["sector"],
                priority=item.get("priority", "Medium"),
                active=bool(item.get("active", True)),
                risk_flag=item.get("risk_flag", ""),
                reason=item.get("reason", ""),
                aliases=list(item.get("aliases", [])),
            )
        )
    return [a for a in assets if a.active]


def load_news_sources(path: Path | None = None) -> list[dict]:
    path = path or CONFIG_DIR / "news_sources.yaml"
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    return raw.get("sources", [])
