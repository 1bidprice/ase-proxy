from __future__ import annotations

from typing import Iterable

from .models import Asset, NewsItem


def _match_tickers(text: str, assets: Iterable[Asset]) -> list[str]:
    text_l = text.lower()
    matched = []
    for asset in assets:
        token_candidates = {
            asset.ticker.lower(),
            asset.name.lower(),
            asset.name.split()[0].lower(),
        }
        if any(token and token in text_l for token in token_candidates):
            matched.append(asset.ticker)
    return sorted(set(matched))


def fetch_rss_news(sources: list[dict], assets: list[Asset], max_items_per_source: int = 20) -> list[NewsItem]:
    import feedparser

    items: list[NewsItem] = []

    for source in sources:
        if source.get("type") != "rss":
            continue

        feed = feedparser.parse(source["url"])
        for entry in feed.entries[:max_items_per_source]:
            title = getattr(entry, "title", "") or ""
            link = getattr(entry, "link", "") or ""
            published = getattr(entry, "published", None)

            matched = _match_tickers(f"{title} {link}", assets)
            if matched:
                items.append(
                    NewsItem(
                        source=source["name"],
                        title=title,
                        link=link,
                        published=published,
                        matched_tickers=matched,
                    )
                )

    return items
